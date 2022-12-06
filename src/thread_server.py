import io
import shutil
import signal
import socket
import threading
import os
import sys
from http_msg import HttpRequest, HttpResponse
import http_status as http_SC
import mimetypes

BUFSIZE = 8192


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class Server:
    def __init__(self, addr, port, handler, max_conn=50):
        self.addr = addr
        self.port = port
        self.handler = handler
        self.max_conn = max_conn

        # create server socket
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((self.addr, self.port))
        self.server.listen(self.max_conn)

        # get hostname and ip address
        self.hostname = socket.gethostname()
        self.ip = socket.gethostbyname(self.hostname)

        # register signal handler
        signal.signal(signal.SIGINT, self.signal_handler)

        eprint(f"Server created at http://{self.ip}:{self.port} ({self.server.fileno()})")
        eprint("---------------------------------------")

    def run_forever(self):
        while True:
            client, addr = self.server.accept()
            thread = threading.Thread(target=self.handler, args=(client, addr), daemon=True)
            thread.start()

    def signal_handler(self, sig, frame):
        eprint("\rServer shutting down...")
        self.server.close()
        sys.exit(0)


class Handler:
    def __init__(self, root: str):
        self.root = root
        self.client: socket.socket = None
        self.rfile: io.BufferedReader = None
        self.wfile: io.BufferedWriter = None

    def __call__(self, client: socket.socket, addr: tuple[str, int]):
        try:
            self.client = client
            self.rfile = client.makefile("rb", -1)
            self.wfile = client.makefile("wb", 0)
            eprint(f"\033[32mNew connection from {addr[0]}:{addr[1]} ({self.client.fileno()})\033[0m")
            # eprint([t.name for t in threading.enumerate()])

            while True:
                # receive one request
                req = HttpRequest()
                try:
                    req.parse(self.rfile)
                except ConnectionResetError:
                    break
                if req.method == "GET":
                    self.handle_get(req)
                elif req.method == "POST":
                    self.handle_post(req)
                else:
                    self.send_error(req, *http_SC.NOT_IMPLEMENTED)
        except BrokenPipeError:
            pass
        self.exit_thread()

    def exit_thread(self):
        eprint(f"\033[31mConnection closed ({self.client.fileno()})\033[0m")
        # eprint(f"\033[31mConnection closed ({threading.current_thread().name})\033[0m")
        # eprint(f"Active threads: {threading.active_count() - 1}")
        # eprint([t.name for t in threading.enumerate()])
        self.client.close()
        sys.exit(0)

    def handle_get(self, req: HttpRequest):
        res = HttpResponse()
        res.version = req.version
        file_str = self.root + req.path

        # for single-page application
        if file_str.find(".") == -1:
            file_str = self.root + "/index.html"

        try:
            f = open(file_str, "rb")
        except FileNotFoundError:
            eprint(f"GET {req.path} 404 Not Found")
            self.send_error(req, *http_SC.NOT_FOUND)
            return
        except PermissionError:
            eprint(f"GET {req.path} 403 Forbidden")
            self.send_error(req, *http_SC.FORBIDDEN)
            return
        except:
            eprint(f"GET {req.path} 500 Internal Server Error")
            self.send_error(req, *http_SC.INTERNAL_SERVER_ERROR)
            return

        # 200 OK
        eprint(f"GET {req.path} 200 OK ({self.client.fileno()})")
        res.status_code = 200
        res.status_msg = "OK"
        res.headers["Content-Type"] = self.get_mime_type(file_str)
        res.headers["Server"] = "Project Demo for NTU CSIE Computer Network course"
        f.seek(0, os.SEEK_END)
        size = f.tell()
        res.headers["Content-Length"] = str(size)
        eprint(f"File Size: {res.headers['Content-Length']}")
        self.wfile.write(res.encode())

        # send file
        f.seek(0)
        shutil.copyfileobj(f, self.wfile)
        # res.body = f.read()

        # TODO: partial content if range is specified
        if "Range" in req.headers:
            pass

        # self.wfile.write(res.body)
        f.close()
        return

    def send_error(self, req: HttpRequest, code: int, msg: str, desc: str):
        res = HttpResponse()
        res.version = req.version
        res.status_code = code
        res.status_msg = msg
        res.headers["Content-Type"] = "text/html"
        error_page = self.root + "/error/" + str(code) + ".html"

        try:
            f = open(error_page, "rb")
        except:
            res.body = desc.encode()
        else:
            res.body = f.read()
            f.close()

        res.headers["Content-Length"] = str(len(res.body))
        self.wfile.write(res.encode())
        return

    def get_mime_type(self, file):
        mime, encoding = mimetypes.guess_type(file)
        return mime
