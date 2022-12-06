import socket
import threading
import sys
from http_msg import http_request, http_response
import http_status as http_SC
import mimetypes

BUFSIZE = 8192

def errprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

class thread_server:
    def __init__(self, port_num, sock_addr="0.0.0.0", max_conn=50, root="dist"):
        self.port_num = port_num
        self.sock_addr = sock_addr
        self.max_conn = max_conn
        self.root = root

        # create server socket
        self.serv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.serv_socket.bind((self.sock_addr, self.port_num))
        self.serv_socket.listen(self.max_conn)

        # get hostname
        self.hostname = socket.gethostname()
        # get ip address of self.hostname
        self.ip_addr = socket.gethostbyname(self.hostname)

        errprint(f"Server created at {self.ip_addr} : {self.port_num}")
        errprint("---------------------------------------")

    def loop(self):
        while True:
            client, addr = self.serv_socket.accept()
            errprint(f"New connection from IP address {addr[0]} port {addr[1]}")
            # create new thread to handle client
            thread = threading.Thread(target=self.handle_thread, args=(client, addr))
            thread.start()

    def handle_thread(self, client, addr):
        errprint(f"Thread {threading.get_ident()} created")
        cli_addr = addr
        while(True):
            status, data = self.handle_read(client)
            if not status:
                # client close connection
                break
            req: http_request = self.parse_request(data)
            if req.method == "GET":
                self.handle_get(client, req)

        errprint(f"Connection from IP address {cli_addr[0]} port {cli_addr[1]} closed, thread {threading.get_ident()} terminated")
        return

    def handle_read(self, client):
        try:
            data = client.recv(BUFSIZE)
        except:
            return False, None
        return True, data.decode()

    def parse_request(self, data):
        fields = [s for s in data.split("\n") if s]
        method, path, version = fields[0].rstrip().split(" ")
        headers = dict()
        now_h = 1
        while fields[now_h] != "\r":
            key, value = fields[now_h].rstrip().split(": ")
            headers[key] = value
            now_h += 1
        
        body = "\n".join(fields[now_h+1:])
        req = http_request()
        req.method = method
        req.path = path
        req.version = version
        req.headers = headers
        req.body = body
        return req

    def handle_get(self, client, req: http_request):
        res = http_response()
        res.version = req.version
        file_str: str = self.root + req.path

        # for single-page application
        if file_str.find(".") == -1:
            file_str = self.root + "/index.html"

        # check if file exists
        try:
            with open(file_str, "r") as f:
                pass
        except:
            errprint(f"GET {req.path} 404 Not Found")
            self.send_error(client, req, *http_SC.NOT_FOUND)
            return

        # try to open file in binary
        try:
            f = open(file_str, "rb")
        except:
            errprint(f"GET {req.path} 500 Internal Server Error")
            self.send_error(client, req, *http_SC.INTERNAL_SERVER_ERROR)
            return

        # 200 OK
        errprint(f"GET {req.path} 200 OK")
        res.status_code = 200
        res.status_msg = "OK"
        res.headers["Content-Type"] = self.get_mime_type(file_str)
        res.headers["Server"] = "Project Demo for NTU CSIE Computer Network course"
        res.headers["Content-Length"] = str(len(f.read()))
        errprint(f"File Size: {res.headers['Content-Length']}")
        # f seek to begining
        f.seek(0)

        res.body = f.read()
        # to-do: partial content if range is specified
        if "Range" in req.headers:
            pass

        client.send(res.to_string(no_body=True).encode())
        client.send(res.body)
        f.close()
        return

    def send_error(self, client, req: http_request, code: int, msg: str, desc: str):
        res = http_response()
        res.version = req.version
        res.status_code = code
        res.status_msg = msg
        res.headers["Content-Type"] = "text/html"
        error_page = self.root + "/error/" + str(code) + ".html"
        
        # try to open error_page file
        try:
            with open(error_page, "r") as f:
                res.body = f.read()
        except:
            res.body = desc

        res.headers["Content-Length"] = str(len(res.body))
        client.send(res.to_string().encode())
        client.close()

    def get_mime_type(self, file):
        mime, encoding = mimetypes.guess_type(file)
        return mime