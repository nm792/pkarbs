#!/usr/bin/env python3
"""Publish complete Dota capture JSONL deltas to the storage box; git stores a manifest only."""
import datetime as dt
import gzip
import hashlib
import json
import os
import pathlib
import subprocess
import sys

REPO = pathlib.Path('/root/pkarbs')
BRANCH = 'claude/project-thread-vg2ckg'
OUT = pathlib.Path('/vol2/pkarbs/dotacap/run-2026-11-16/out')
WORK = pathlib.Path('/vol2/pkarbs/dotacap/run-2026-11-16/publisher')
CHUNKS = WORK / 'chunks'
STATE = WORK / 'state.json'
MANIFEST = WORK / 'manifest.tsv'
BOX_SUB = 'pkarbs/dotacap-2026-11-16'
REPO_MANIFEST = 'manifest/dotacap-2026-11-16.tsv'


def load_env(path):
    vals = {}
    for line in pathlib.Path(path).read_text().splitlines():
        if not line or line.lstrip().startswith('#') or '=' not in line:
            continue
        key, value = line.split('=', 1)
        value = value.strip().strip('"').strip("'")
        if key in ('BOX_ROOT', 'RSYNC_RSH'):
            vals[key] = value
    return vals


def run(args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def save_state(state):
    tmp = STATE.with_suffix('.tmp')
    tmp.write_text(json.dumps(state, sort_keys=True))
    os.replace(tmp, STATE)


def main():
    env = load_env('/root/ship/ship.env')
    box_root = env.get('BOX_ROOT')
    if not box_root:
        raise RuntimeError('BOX_ROOT missing')
    rsync_rsh = env.get('RSYNC_RSH', '')
    WORK.mkdir(parents=True, exist_ok=True)
    CHUNKS.mkdir(parents=True, exist_ok=True)
    state = json.loads(STATE.read_text()) if STATE.exists() else {'offsets': {}}
    manifest_lines = MANIFEST.read_text().splitlines() if MANIFEST.exists() else []
    known = {line.split('\t')[2] for line in manifest_lines if len(line.split('\t')) >= 3}
    now = dt.datetime.now(dt.timezone.utc)
    if now >= dt.datetime(2026, 11, 17, 20, 35, tzinfo=dt.timezone.utc):
        print('CAPTURE_WINDOW_ENDED; final-copy invocation only')
    stamp = now.strftime('%Y%m%dT%H%M%SZ')
    sent = 0
    for src in sorted(OUT.glob('*.jsonl')) + [OUT / 'capture.log']:
        if not src.is_file():
            continue
        key = src.name
        offset = int(state['offsets'].get(key, 0))
        size = src.stat().st_size
        if size < offset:
            offset = 0
        with src.open('rb') as f:
            f.seek(offset)
            data = f.read()
        last = data.rfind(b'\n')
        if last < 0:
            continue
        payload = data[:last + 1]
        new_offset = offset + last + 1
        chunk_name = f'{src.stem}.{stamp}.jsonl.gz' if src.suffix == '.jsonl' else f'capture.{stamp}.log.gz'
        if chunk_name in known:
            state['offsets'][key] = new_offset
            save_state(state)
            continue
        local = CHUNKS / chunk_name
        with local.open('wb') as raw:
            with gzip.GzipFile(fileobj=raw, mode='wb', compresslevel=6, mtime=0) as gz:
                gz.write(payload)
        sha = hashlib.sha256(local.read_bytes()).hexdigest()
        cmd = ['rsync', '-a', '--mkpath']
        if rsync_rsh:
            cmd.extend(['-e', rsync_rsh])
        cmd.extend([str(local), f'{box_root.rstrip("/")}/{BOX_SUB}/{chunk_name}'])
        run(cmd)
        verify = ['rsync', '-a', '--checksum', '--dry-run', '--itemize-changes']
        if rsync_rsh:
            verify.extend(['-e', rsync_rsh])
        verify.extend([str(local), f'{box_root.rstrip("/")}/{BOX_SUB}/{chunk_name}'])
        check = subprocess.run(verify, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if check.returncode != 0 or check.stdout.strip():
            raise RuntimeError(f'box checksum verification failed for {chunk_name}: {check.stderr.strip()} {check.stdout.strip()}')
        rows = payload.count(b'\n')
        line = f'{now.isoformat()}\t{key}\t{chunk_name}\t{rows}\t{len(payload)}\t{local.stat().st_size}\t{sha}'
        with MANIFEST.open('a') as mf:
            mf.write(line + '\n')
            mf.flush()
            os.fsync(mf.fileno())
        known.add(chunk_name)
        state['offsets'][key] = new_offset
        save_state(state)
        local.unlink()
        sent += 1
        print(f'BOX_OK file={chunk_name} rows={rows} raw_bytes={len(payload)} gzip_bytes={len(gzip.compress(payload))} sha256={sha}')
    if not MANIFEST.exists():
        print('NO_NEW_COMPLETE_ROWS')
        return 0
    subprocess.run(['git', '-C', str(REPO), 'fetch', '-q', 'origin', BRANCH], check=True)
    tip = subprocess.check_output(['git', '-C', str(REPO), 'rev-parse', f'origin/{BRANCH}'], text=True).strip()
    remote_manifest = subprocess.run(
        ['git', '-C', str(REPO), 'show', f'origin/{BRANCH}:{REPO_MANIFEST}'],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if sent == 0 and remote_manifest.returncode == 0 and remote_manifest.stdout == MANIFEST.read_text():
        print('NO_NEW_COMPLETE_ROWS; manifest already current on origin')
        return 0
    index = WORK / 'git-index'
    index.unlink(missing_ok=True)
    git_env = os.environ.copy()
    git_env['GIT_INDEX_FILE'] = str(index)
    subprocess.run(['git', '-C', str(REPO), 'read-tree', tip], env=git_env, check=True)
    blob = subprocess.check_output(['git', '-C', str(REPO), 'hash-object', '-w', str(MANIFEST)], text=True).strip()
    subprocess.run(['git', '-C', str(REPO), 'update-index', '--add', '--cacheinfo', f'100644,{blob},{REPO_MANIFEST}'], env=git_env, check=True)
    tree = subprocess.check_output(['git', '-C', str(REPO), 'write-tree'], env=git_env, text=True).strip()
    msg = f'Dota capture manifest {now.strftime("%Y-%m-%dT%H:%MZ")}'
    commit = subprocess.check_output(['git', '-C', str(REPO), 'commit-tree', tree, '-p', tip, '-m', msg], text=True).strip()
    if not commit:
        raise RuntimeError('empty manifest commit; refusing push')
    run(['git', '-C', str(REPO), 'push', 'origin', f'{commit}:refs/heads/{BRANCH}'])
    landed = subprocess.check_output(['git', '-C', str(REPO), 'show', f'origin/{BRANCH}:{REPO_MANIFEST}'], text=True)
    if landed != MANIFEST.read_text():
        raise RuntimeError('pushed manifest does not match local manifest')
    print(f'MANIFEST_PUSHED commit={commit} path={REPO_MANIFEST} new_chunks={sent}')
    index.unlink(missing_ok=True)
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as exc:
        print(f'PUBLISH_ERROR {type(exc).__name__}: {exc}', file=sys.stderr)
        sys.exit(1)
