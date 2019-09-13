import json
import os
import re


class PermissionManager:

    DEFAULT_ACL_JSON = {
        "courses": {
        }
    }

    DEFAULT_INDENT_LEVEL = 4
    DEFAULT_FILE_NAME = "acl.json"
    DEFAULT_DATA_DIRECTORY = "data"
    FULL_PATH = os.path.join(DEFAULT_DATA_DIRECTORY, DEFAULT_FILE_NAME)

    def __init__(self):
        self.check_files()

    @staticmethod
    def check_files(overwrite=False):
        if os.path.isdir(PermissionManager.DEFAULT_DATA_DIRECTORY):
            if os.path.exists(PermissionManager.FULL_PATH) and not overwrite:
                return True
            else:
                with open(PermissionManager.FULL_PATH, "w+") as file:
                    file.write(json.dumps(
                        PermissionManager.DEFAULT_ACL_JSON, indent=4))
                return True
        else:
            os.mkdir(PermissionManager.DEFAULT_DATA_DIRECTORY)
            with open(PermissionManager.FULL_PATH, "w+") as file:
                file.write(json.dumps(
                    PermissionManager.DEFAULT_ACL_JSON, indent=4))

    @staticmethod
    def _read_acl_data():

        with open(PermissionManager.FULL_PATH, "r") as file:
            return json.loads(file.read())

    @staticmethod
    def _write_acl_data(new_dict):

        new_acl = json.dumps(
            new_dict, indent=PermissionManager.DEFAULT_INDENT_LEVEL)
        with open(PermissionManager.FULL_PATH, "w") as file:
            file.write(new_acl)
        return True

    def add_course(self, course_id):

        if not re.match(r'^c-\d+$', course_id):
            return False

        acl_dict = self._read_acl_data()
        if course_id not in acl_dict["courses"]:
            acl_dict["courses"][course_id] = {"everyone": False}
            self._write_acl_data(acl_dict)

    def remove_course(self, course_id):

        if not re.match(r'^c-\d+$', course_id):
            return False

        acl_dict = self._read_acl_data()
        if course_id in acl_dict["courses"]:
            del acl_dict["courses"][course_id]
            self._write_acl_data(acl_dict)

    def add_permission(self, user_id, course_id, mode):

        if not (re.match(r'^u-\d+$', user_id) and re.match(r'^c-\d+$', course_id) and re.match(r'^(r|rw)$', mode)):
            return False

        acl_dict = self._read_acl_data()
        acl_dict["courses"][course_id][user_id] = mode
        self._write_acl_data(acl_dict)
        return True

    def remove_permission(self, user_id, course_id):

        if not (re.match(r'^u-\d+$', user_id) and re.match(r'^c-\d+$', course_id)):
            return False

        acl_dict = self._read_acl_data()
        if user_id in acl_dict["courses"][course_id]:
            del acl_dict["courses"][course_id][user_id]
        else:
            return False

        self._write_acl_data(acl_dict)
        return True

    def set_everyone(self, course_id, mode):

        if not re.match(r'^c-\d+$', course_id) and re.match(r'^(r|rw)$', mode) or mode == False:
            return False
        acl_dict = self._read_acl_data()
        acl_dict["courses"][course_id]["everyone"] = mode
        self._write_acl_data(acl_dict)

    def get_user_permission(self, user_id, course_id):

        acl_dict = self._read_acl_data()
        if course_id in acl_dict["courses"] and user_id in acl_dict["courses"][course_id]:
            return acl_dict["courses"][course_id][user_id]
        elif acl_dict["courses"][course_id]["everyone"]:
            return acl_dict["courses"][course_id]["everyone"]
        else:
            return False

    def get_user_permissions(self, user_id):

        acl_dict = self._read_acl_data()
        permissions = {"r": [], "rw": []}
        for key, value in acl_dict["courses"].items():
            if value["everyone"]:
                permissions[value["everyone"]].append(key)
            elif user_id in value:
                permissions[value[user_id]].append(key)
        return permissions
