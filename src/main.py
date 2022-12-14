import argparse
import os
import shutil

from server import Server, Handler, eprint
from utils.status import HttpStatus
from utils.message import HttpResponse


class MainHandler(Handler):
    def get_all_ranges(self, ranges: str):
        ret = []
        ranges = ranges.replace("bytes=", "")

        for range_str in ranges.split(","):
            start, end = range_str.strip().split("-")
            if start == "":
                start = 0
            else:
                start = int(start)
            if end == "":
                end = -1
            else:
                end = int(end)
            ret.append([start, end])
        return ret

    def handle_get(self):
        if self.request.path == "/":
            file_str = self.root + "/index.html"
        else:
            file_str = self.root + self.request.path

        response = HttpResponse(ranges=True)
        if "Range" in self.request.headers:
            range_list = self.get_all_ranges(self.request.headers["Range"])
            status = response.set_body(file_path=file_str, partial_range=range_list)
        else:
            status = response.set_body(file_path=file_str)

        if status != HttpStatus.OK and status != HttpStatus.PARTIAL_CONTENT:
            response.set_error(status)
        else:
            response.set_status(status)

        self.send_response(response)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=4567)
    parser.add_argument("-a", "--address", type=str, default="0.0.0.0")
    parser.add_argument("-r", "--root", type=str, default="dist")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    server = Server(args.address, args.port, MainHandler, root=args.root)
    server.mainloop()


if __name__ == "__main__":
    main()
