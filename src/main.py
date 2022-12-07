import argparse
import os
import shutil

from server import Server, Handler, eprint
from utils.status import HttpStatus


class MyHandler(Handler):
    def handle_head(self):
        self.file_str = self.root + self.request.path

        if self.file_str.endswith("/"):
            self.file_str += "index.html"

        # for single-page application
        # if self.file_str.find(".") == -1:
        #     self.file_str = self.root + "/index.html"

        try:
            f = open(self.file_str, "rb")
        except FileNotFoundError:
            self.send_error(HttpStatus.NOT_FOUND)
            self.file_str = None
            return
        except PermissionError:
            self.send_error(HttpStatus.FORBIDDEN)
            self.file_str = None
            return
        except:
            self.send_error(HttpStatus.INTERNAL_SERVER_ERROR)
            self.file_str = None
            return

        # 200 OK
        self.send_response(HttpStatus.OK)
        self.send_header("Content-Type", self.get_mime_type(self.file_str))
        self.send_header("Content-Length", size := os.path.getsize(self.file_str))
        self.end_headers()
        f.close()
        return

    def handle_get(self):
        self.handle_head()
        if self.file_str is None:
            return
        f = open(self.file_str, "rb")
        # self.wfile.write(f.read())
        shutil.copyfileobj(f, self.wfile)
        f.close()
        return


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=4567)
    parser.add_argument("-a", "--address", type=str, default="0.0.0.0")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    server = Server(args.address, args.port, MyHandler)
    server.run_forever()


if __name__ == "__main__":
    main()
