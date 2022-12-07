import argparse
import os
import shutil

from server import Server, Handler, eprint
from utils.status import HttpStatus
from utils.message import HttpResponse


class MainHandler(Handler):
    def handle_get(self):
        if self.request.path == "/":
            file_str = self.root + "/index.html"
        else:
            file_str = self.root + self.request.path

        response = HttpResponse()
        status = response.set_body(file_str)
        if status != HttpStatus.OK:
            response.set_error(status)
        else:
            response.set_status(status)

        self.send_response(response)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=4567)
    parser.add_argument("-a", "--address", type=str, default="0.0.0.0")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    server = Server(args.address, args.port, MainHandler)
    server.mainloop()


if __name__ == "__main__":
    main()
