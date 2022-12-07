import argparse

from server import Server, Handler, eprint
from utils.status import HttpStatus
from utils.message import HttpResponse
from database import UserDatabase, CommentDatabase

import json

ERROR_RES_BODY = '{{\n "success": false,\n "data": {0}\n}}'

class APIHandler(Handler):
    def __init__(self, root: str, client_timeout=60, udb_path = "./db/user.json", cdb_path = "./db/comment.json"):
        super().__init__(root, client_timeout)
        self.udb_path = udb_path
        self.cdb_path = cdb_path
        self.udb = UserDatabase(self.udb_path)
        self.cdb = CommentDatabase(self.cdb_path)

    def handle_get(self):
        method_name = "api_get_" + self.request.path[1:].split("/")[0]
        if not hasattr(self, method_name):
            response = HttpResponse()
            response.set_error(HttpStatus.NOT_IMPLEMENTED)
            self.send_response(response)
        else:
            method = getattr(self, method_name)
            method()
    
    def handle_post(self):
        method_name = "api_post_" + self.request.path[1:].split("/")[0]
        if not hasattr(self, method_name):
            response = HttpResponse()
            response.set_error(HttpStatus.NOT_IMPLEMENTED)
            self.send_response(response)
        else:
            method = getattr(self, method_name)
            method()

    def api_post_register(self):
        req = json.loads(self.request.body)
        ret = self.udb.add_user(req["name"], req["pass"])
        if ret:
            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.set_body(json_str='{{\n "success": true,\n "data": null\n}}')
            self.send_response(response)
        else:
            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.set_body(json_str=ERROR_RES_BODY.format('"User already exists"'))
            self.send_response(response)

    def api_post_login(self):
        req = json.loads(self.request.body)
        ret = self.udb.validate(req["name"], req["pass"])
        if ret:
            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.add_header("Set-Cookie", "session_id={}".format(ret))
            response.set_body(json_str='{{\n "success": true\n}}')
            self.send_response(response)
        else:
            response = HttpResponse()
            response.set_status(HttpStatus.UNAUTHORIZED)
            response.set_body(json_str=ERROR_RES_BODY.format('"Invalid username or password"'))
            self.send_response(response)

    def api_post_logout(self):
        if self.request.headers.get("Cookie") is None:
            response = HttpResponse()
            response.set_status(HttpStatus.UNAUTHORIZED)
            response.set_body(json_str=ERROR_RES_BODY.format('"Not logged in"'))
            self.send_response(response)
        else:
            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.add_header("Set-Cookie", "session_id=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            response.set_body(json_str='{{\n "success": true\n}}')
            self.send_response(response)

    # TODO: check sessino_id of cookie
    def api_post_comment(self):
        if self.request.headers.get("Cookie") is not None:
            req = json.loads(self.request.body)
            ret = self.cdb.add_comment(req["name"], req["comment"])

            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.set_body(json_str=json.dumps({"success": True, "data": {"id": ret}}, indent=4))
            self.send_response(response)
        else:
            response = HttpResponse()
            response.set_status(HttpStatus.UNAUTHORIZED)
            response.set_body(json_str=ERROR_RES_BODY.format('"Not logged in"'))
            self.send_response(response)

    def api_get_comment(self):
        if self.request.headers.get("Cookie") is not None:
            ret = self.cdb.get_all_comment_json()
            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.set_body(json_str=ret)
            self.send_response(response)
        else:
            response = HttpResponse()
            response.set_status(HttpStatus.UNAUTHORIZED)
            response.set_body(json_str=ERROR_RES_BODY.format('"Not logged in"'))
            self.send_response(response)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--port", type=int, default=4678)
    parser.add_argument("-a", "--address", type=str, default="0.0.0.0")

    args = parser.parse_args()
    return args


def main():
    args = parse_args()
    server = Server(args.address, args.port, APIHandler)
    server.mainloop()


if __name__ == "__main__":
    main()
