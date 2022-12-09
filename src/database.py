import json
import random
import datetime
from time import sleep

class UserDatabase:
    def __init__(self, user_file: str="../db/user.json"):
        self.user_file = user_file
        self.users = self.load_users()

        self.name_dict = {u["name"]: u for u in self.users}
        self.id_dict = {u["id"]: u for u in self.users}

    def get_unique_id(self):
        while True:
            uid = random.randint(1, 1000000)
            if uid not in self.id_dict.keys():
                return uid

    def load_users(self):
        try:
            f = open(self.user_file, "r")
        except:
            return {}
        else:
            users = json.load(f)
            f.close()
            return users["users"]

    def save_users(self):
        try:
            f = open(self.user_file, "w")
        except:
            pass
        else:
            json.dump({"users": self.users}, f, indent=4)
            f.close()

    def add_user(self, name, password):
        if name in self.name_dict.keys():
            return False
        else:
            self.users.append({"name": name, "pass": password, "id": self.get_unique_id()})
            self.save_users()
            return True

    def find(self, name=None, uid=None, name_only=False, id_only=False) -> dict:
        if name:
            if name in self.name_dict:
                if name_only:
                    return self.name_dict[name]["name"]
                elif id_only:
                    return self.name_dict[name]["id"]
                return self.name_dict[name]
            else:
                return None
        elif uid:
            uid = int(uid)
            if uid in self.id_dict:
                if name_only:
                    return self.id_dict[uid]["name"]
                elif id_only:
                    return self.id_dict[uid]["id"]
                return self.id_dict[uid]
            else:
                return None
        else:
            return None

    def validate(self, name, password):
        if name not in self.name_dict.keys():
            return 0
        else:
            if self.name_dict[name]["pass"] == password:
                return self.name_dict[name]["id"]
            else:
                return 0

class CommentDatabase:
    def __init__(self, comment_file: str="../db/comment.json"):
        self.comment_file = comment_file
        self.comments = self.load_comments()

        self.id_dict = {c["id"]: c for c in self.comments}

    def current_time_str(self):
        return datetime.datetime.now().isoformat()

    def get_unique_id(self):
        while True:
            cid = random.randint(1, 1000000)
            if cid not in self.id_dict.keys():
                return cid

    def load_comments(self):
        try:
            f = open(self.comment_file, "r")
        except:
            return {}
        else:
            comments = json.load(f)
            f.close()
            return comments["comments"]
    
    def save_comments(self):
        try:
            f = open(self.comment_file, "w")
        except:
            pass
        else:
            json.dump({"comments": self.comments}, f, indent=4)
            f.close()

    def add_comment(self, name, comment):
        cid = self.get_unique_id()
        self.comments.append({"id": cid, "name": name, "comment": comment, "time": self.current_time_str()})
        self.save_comments()
        return cid

    def get_all_comment_json(self):
        return json.dumps({"success": True, "data": [{"name": c["name"], "comment": c["comment"], "time": c["time"]} for c in self.comments]}, indent=4)
