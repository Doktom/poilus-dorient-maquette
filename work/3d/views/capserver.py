"""Serveur local : sert out/ et enregistre les captures POST /save?name=<id> (corps = dataURL JPEG) dans views/out/."""
import http.server, os, base64, urllib.parse, sys
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'out')
SAVE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def do_POST(self):
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        name = ''.join(c for c in q.get('name', ['x'])[0] if c.isalnum() or c in '-_')
        data = self.rfile.read(int(self.headers['Content-Length'])).decode()
        open(os.path.join(SAVE, name + '.jpg'), 'wb').write(base64.b64decode(data.split(',', 1)[1]))
        self.send_response(200); self.end_headers(); self.wfile.write(b'ok')
http.server.ThreadingHTTPServer(('127.0.0.1', int(sys.argv[1])), H).serve_forever()
