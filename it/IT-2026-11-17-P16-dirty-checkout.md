# IT note, 17 Nov 16:10Z: P16 blocked by dirty checkout, P16s routed

1. Goal: restart the no-token shadow logger (Nick yes 14:36:23Z) into data-v3 on the data volume and finish the Goalserve chunk D copy-out.
2. Where it stands: P16 stopped before running anything (pkarbs 4d24c06f, agent/status/shadow-logger-restart-2026-11-17.md): /root/pkarbs is at 026be71f, 26 commits behind 89c36e7d, with 191 dirty tracked paths (174 staged deletions) and 118 untracked paths. Scope inactive; data volume 29,627,131,184 B free (same file). P15d4 open since 15:12Z with no agent commit.
3. Most important: P16 cannot start until the checkout is clean, so IT routed P16s (stash it, deleting nothing) ahead of P16.

Items
- Routed P16s (waiting: after P15d4): count dirty paths, measure untracked bytes (stop if > 500 MB), then `git stash push -u -m pre-P16-17Nov`, and check porcelain = 0. This follows the existing GIT RULES. The stash keeps the 174 staged deletions and untracked files recoverable (`git stash show -p stash@{0}`).
- P16 is now `waiting: after P16s`. It reruns unchanged once the stash lands.
- If those staged deletions or untracked files are work you need on the branch, say so in a REPLY before P16s runs and IT will hold it.
- Order: P15d4 runs first, then P16s, then P16.
