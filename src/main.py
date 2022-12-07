import argparse

from server import Server, Handler
from utils.status import HttpStatus


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=4567)
    parser.add_argument("-a", "--address", type=str, default="0.0.0.0")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    server = Server(args.address, args.port, Handler)
    server.run_forever()


if __name__ == "__main__":
    main()
