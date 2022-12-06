from thread_server import thread_server
import argparse

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=4567)
    parser.add_argument("-a", "--address", type=str, default="0.0.0.0")

    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    server = thread_server(args.port, args.address)
    server.loop()

if __name__ == "__main__":
    main()