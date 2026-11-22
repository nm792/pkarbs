"""Minimal stdlib websocket client (RFC 6455, text frames, client masking, ping/pong, TLS). No third-party packages: Prime may not have `websockets`."""
import base64, hashlib, os, socket, ssl, struct, time, urllib.parse


class WS:
    def __init__(self, url, timeout=30, proxy=None):
        u = urllib.parse.urlparse(url); host, port = u.hostname, u.port or 443; self.buf = b''
        sock = socket.create_connection((host, port), timeout=timeout)
        self.sock = ssl.create_default_context().wrap_socket(sock, server_hostname=host); key = base64.b64encode(os.urandom(16)).decode()
        path = (u.path or '/') + ('?' + u.query if u.query else '')
        self.sock.sendall(('GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n' % (path, host, key)).encode())
        hdr = b''
        while b'\r\n\r\n' not in hdr:
            c = self.sock.recv(4096)
            if not c: raise ConnectionError('closed in handshake')
            hdr += c
        head, self.buf = hdr.split(b'\r\n\r\n', 1)
        if b' 101 ' not in head.split(b'\r\n')[0]: raise ConnectionError('handshake failed: ' + head[:80].decode(errors='replace'))
        exp = base64.b64encode(hashlib.sha1((key + '258EAFA5-E914-47DA-95CA-C5AB0DC85B11').encode()).digest())
        if exp not in head: raise ConnectionError('bad accept key')

    def send(self, text, opcode=1):
        d = text.encode() if isinstance(text, str) else text; n = len(d); m = os.urandom(4)
        h = bytes([0x80 | opcode]) + (bytes([0x80 | n]) if n < 126 else bytes([0x80 | 126]) + struct.pack('>H', n) if n < 65536 else bytes([0x80 | 127]) + struct.pack('>Q', n))
        self.sock.sendall(h + m + bytes(b ^ m[i % 4] for i, b in enumerate(d)))

    def _need(self, n):
        while len(self.buf) < n:
            c = self.sock.recv(65536)
            if not c: raise ConnectionError('closed')
            self.buf += c
        r, self.buf = self.buf[:n], self.buf[n:]; return r

    def recv(self):
        """Next text message (str); answers pings; raises ConnectionError on close; socket.timeout when idle."""
        msg = b''
        while True:
            b1, b2 = self._need(2); fin, op = b1 & 0x80, b1 & 0x0f; n = b2 & 0x7f
            if n == 126: n = struct.unpack('>H', self._need(2))[0]
            elif n == 127: n = struct.unpack('>Q', self._need(8))[0]
            p = self._need(n)
            if op == 9: self.send(p, 10); continue
            if op == 10: continue
            if op == 8: raise ConnectionError('server closed')
            msg += p
            if fin: return msg.decode('utf-8', 'replace')

    def close(self):
        try: self.sock.close()
        except Exception: pass
