import argparse

from server import Server, Handler, eprint
from utils.status import HttpStatus
from utils.message import HttpResponse
from database import UserDatabase, CommentDatabase

import json

ERROR_RES_BODY = '{{\n "success": false,\n "data": {0}\n}}'

class APIServer(Server):
    def __init__(self, addr: str, port: int, Handler: "Handler", clinet_timeout: int = 60, root="dist", max_conn=50):
        super().__init__(addr, port, Handler, clinet_timeout, root, max_conn)
        self.online_users = dict()
    
    def get_handler(self):
        ret = super().get_handler()
        ret.set_server(self)
        return ret

    def check_login(self, user_id):
        user_id = int(user_id)
        return user_id in self.online_users

    def login(self, user_id):
        user_id = int(user_id)
        self.online_users[user_id] = True

    def logout(self, user_id):
        user_id = int(user_id)
        if user_id in self.online_users:
            del self.online_users[user_id]

class APIHandler(Handler):
    def __init__(self, root: str, client_timeout=60, udb_path = "./db/user.json", cdb_path = "./db/comment.json"):
        super().__init__(root, client_timeout)
        self.udb_path = udb_path
        self.cdb_path = cdb_path
        self.udb = UserDatabase(self.udb_path)
        self.cdb = CommentDatabase(self.cdb_path)

    def set_server(self, server: "Server"):
        self.server = server

    def parse_cookie(self, cookies):
        if cookies is None:
            return {}
        ret = {}
        for cookie in cookies.split("; "):
            key, value = cookie.split("=")
            ret[key] = value
        return ret

    def check_login(self, cookies):
        if "session_id" not in cookies:
            return False
        return self.server.check_login(cookies["session_id"])

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
        uid = self.udb.validate(req["name"], req["pass"])

        if uid:
            eprint(f"User {req['name']} (id: {str(uid)}) logged in")
            self.server.login(uid)
            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.add_header("Set-Cookie", "session_id={}; path=/".format(uid))
            response.set_body(json_str='{{\n "success": true\n}}')
            self.send_response(response)
        else:
            response = HttpResponse()
            response.set_status(HttpStatus.UNAUTHORIZED)
            response.set_body(json_str=ERROR_RES_BODY.format('"Invalid username or password"'))
            self.send_response(response)

    def api_post_logout(self):
        cookies = self.parse_cookie(self.request.headers.get("Cookie"))

        if self.check_login(cookies) is False:
            response = HttpResponse()
            response.set_status(HttpStatus.UNAUTHORIZED)
            response.set_body(json_str=ERROR_RES_BODY.format('"Not logged in"'))
            self.send_response(response)
        else:
            uid = cookies.get("session_id")
            eprint(f"User {self.udb.find(uid=uid, name_only=True)} (id: {str(uid)}) logged out")
            self.server.logout(uid)
            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.add_header("Set-Cookie", "session_id=; expires=Thu, 01 Jan 1970 00:00:00 GMT")
            response.set_body(json_str='{{\n "success": true\n}}')
            self.send_response(response)

    def api_post_comment(self):
        cookies = self.parse_cookie(self.request.headers.get("Cookie"))

        if self.check_login(cookies) is True:
            req = json.loads(self.request.body)
            cid = self.cdb.add_comment(req["user"], req["comment"])

            response = HttpResponse()
            response.set_status(HttpStatus.OK)
            response.set_body(json_str=json.dumps({"success": True, "data": {"id": cid}}, indent=4))
            self.send_response(response)
        else:
            response = HttpResponse()
            response.set_status(HttpStatus.UNAUTHORIZED)
            response.set_body(json_str=ERROR_RES_BODY.format('"Not logged in"'))
            self.send_response(response)

    def api_get_comment(self):
        cookies = self.parse_cookie(self.request.headers.get("Cookie"))

        if self.check_login(cookies) is True:
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
    server = APIServer(args.address, args.port, APIHandler, 300)
    server.mainloop()


if __name__ == "__main__":
    main()
