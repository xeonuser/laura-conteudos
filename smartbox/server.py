"""Dependency-free LAN runtime. No privileged host operations are performed."""
import argparse
import hmac
import json
import secrets
import threading
import time
import webbrowser
from collections import deque
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CATALOG = [
    {"id": "bbb", "title": "Big Buck Bunny", "category": "Filmes", "year": 2008, "tag": "Animação • Blender Foundation", "description": "Uma aventura bem-humorada em um mundo cheio de pequenos detalhes. Curta aberto do projeto Blender.", "url": "https://download.blender.org/peach/bigbuckbunny_movies/BigBuckBunny_640x360.m4v", "license": "CC BY 3.0", "source": "https://peach.blender.org/", "color": "#427660"},
    {"id": "sintel", "title": "Sintel", "category": "Filmes", "year": 2010, "tag": "Fantasia • Blender Foundation", "description": "Uma viajante atravessa um mundo extraordinário em busca de seu pequeno dragão.", "url": "https://download.blender.org/durian/trailer/sintel_trailer-480p.mp4", "license": "CC BY 3.0 • trailer", "source": "https://durian.blender.org/", "color": "#826350"},
    {"id": "local", "title": "Sua biblioteca", "category": "Biblioteca", "year": "Local", "tag": "Abra um vídeo do computador", "description": "Reproduza seus próprios arquivos sem enviá-los a um servidor.", "url": None, "color": "#425979"},
]


class Runtime:
    def __init__(self):
        self.lock = threading.Lock()
        self.code = f"{secrets.randbelow(1000000):06d}"
        self.code_until = time.monotonic() + 300
        self.tv_token = secrets.token_urlsafe(32)
        self.tokens = set()
        self.attempts = {}
        self.events = deque(maxlen=256)
        self.seq = 0
        self.playing = None


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT / "web"), **kwargs)

    def log_message(self, fmt, *args):
        # Do not log URLs, pairing codes, bodies or bearer credentials.
        pass

    def reply(self, obj, status=200):
        data = json.dumps(obj).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def authorized(self, tv=False):
        token = self.headers.get("Authorization", "").removeprefix("Bearer ")
        return hmac.compare_digest(token, self.server.runtime.tv_token) if tv else token in self.server.runtime.tokens

    def do_GET(self):
        path = urlsplit(self.path).path
        r = self.server.runtime
        if path == "/api/catalog":
            return self.reply(CATALOG)
        if path == "/api/health":
            return self.reply({"status": "ok", "adapter": "simulation", "version": "0.1.0"})
        if path == "/api/events":
            if not self.authorized(tv=True):
                return self.reply({"error": "Não autorizado"}, 401)
            with r.lock:
                return self.reply({"events": list(r.events)})
        if path == "/api/pairing":
            if not self.authorized(tv=True):
                return self.reply({"error": "Não autorizado"}, 401)
            with r.lock:
                if time.monotonic() > r.code_until:
                    r.code = f"{secrets.randbelow(1000000):06d}"
                    r.code_until = time.monotonic() + 300
                return self.reply({"code": r.code, "expires_in": int(r.code_until-time.monotonic())})
        if path == "/api/now":
            if not self.authorized() and not self.authorized(tv=True):
                return self.reply({"error": "Não autorizado"}, 401)
            return self.reply({"title": r.playing})
        if path.startswith("/api/"):
            return self.reply({"error": "Não encontrado"}, 404)
        return super().do_GET()

    def do_POST(self):
        # Prevent cross-origin form submissions and DNS-rebinding write requests.
        origin = self.headers.get("Origin")
        if origin and urlsplit(origin).netloc != self.headers.get("Host"):
            return self.reply({"error": "Origem recusada"}, 403)
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= 4096:
                raise ValueError()
            body = json.loads(self.rfile.read(size))
            if not isinstance(body, dict):
                raise ValueError()
        except (ValueError, TypeError):
            return self.reply({"error": "Pedido inválido"}, 400)
        r = self.server.runtime
        path = urlsplit(self.path).path
        with r.lock:
            if path == "/api/pair":
                ip = self.client_address[0]
                attempts = [t for t in r.attempts.get(ip, []) if time.monotonic()-t < 60]
                if len(attempts) >= 5:
                    return self.reply({"error": "Aguarde um minuto"}, 429)
                attempts.append(time.monotonic())
                r.attempts[ip] = attempts
                if time.monotonic() > r.code_until or not hmac.compare_digest(str(body.get("code", "")), r.code):
                    return self.reply({"error": "Código inválido ou expirado"}, 403)
                token = secrets.token_urlsafe(32)
                r.tokens.add(token)
                r.code_until = 0
                return self.reply({"token": token})
            if path == "/api/command":
                if not self.authorized():
                    return self.reply({"error": "Pareie novamente"}, 401)
                command = body.get("command")
                if command not in {"up", "down", "left", "right", "ok", "back", "home", "play", "forward", "rewind", "search", "volumeup", "volumedown"}:
                    return self.reply({"error": "Comando inválido"}, 400)
                r.seq += 1
                r.events.append({"id": r.seq, "command": command, "text": str(body.get("text", ""))[:200]})
                return self.reply({"ok": True})
            if path == "/api/now" and self.authorized(tv=True):
                r.playing = str(body.get("title", ""))[:200]
                return self.reply({"ok": True})
        return self.reply({"error": "Não autorizado"}, 401)


def create_server(host="127.0.0.1", port=8080):
    server = ThreadingHTTPServer((host, port), Handler)
    server.runtime = Runtime()
    return server


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--open", action="store_true", help="Abrir a interface no navegador")
    args = parser.parse_args()
    server = create_server(args.host, args.port)
    browser_host = "127.0.0.1" if args.host == "0.0.0.0" else args.host
    url = f"http://{browser_host}:{server.server_port}/#tv={server.runtime.tv_token}"
    print(f"Aurora TV: {url}", flush=True)
    if args.open:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    print("Abra o endereço acima SOMENTE na tela da TV. No celular use /remote.html, sem o token.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
