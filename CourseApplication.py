from PermissionManager import PermissionManager
from CourseFileSystem import CourseFileSystem
from UserManager import UserManager
from bs4 import BeautifulSoup
from Error import Error

import os
import webview
import threading
import http.server
import socketserver
import urllib.request
import sys


class CourseApplication:

    def __init__(self, usermanager, user_id):
        api = Api(usermanager, user_id)

        t = threading.Thread(target=self.load_html)
        t1 = threading.Thread(target=self.start_local_html_server, args=[t])
        t1.start()

        webview.config.gui = "cef"
        webview.create_window("Lezioni alla Pari", debug=True, js_api=api)

    @staticmethod
    def load_html():
        with open(os.path.join("html", "index.html"), "r") as html:
            webview.load_html(html.read())

    @staticmethod
    def start_local_html_server(t):
        port = 8080
        handler = http.server.SimpleHTTPRequestHandler
        with socketserver.ThreadingTCPServer(("", port), handler) as httpd:
            t.start()
            httpd.serve_forever()


class Api:

    def __init__(self, usermanager, user_id):
        self.user_mgr = usermanager
        self.permission_mgr = PermissionManager()
        self.course_fs = CourseFileSystem()
        self._logged_user = user_id

    def add_course(self, args_dict):
        id = self.course_fs.add_course(args_dict["course_name"])
        self.permission_mgr.add_course(id)
        self.permission_mgr.add_permission(self._logged_user, id, "rw")
        return id

    def remove_course(self, course_id):
        self.course_fs.remove_course(course_id)
        self.permission_mgr.remove_course(course_id)

    def add_topic(self, args_dict):
        id = self.course_fs.add_topic(args_dict["topic_name"], args_dict["course_id"])
        return id

    def remove_topic(self, args_dict):
        self.course_fs.remove_topic(args_dict["topic_id"], args_dict["course_id"])

    def add_element(self, args_dict):
        id = self.course_fs.add_element(args_dict["element_name"], args_dict["element_type"], args_dict["topic_id"],
                                        args_dict["course_id"])
        return id

    def remove_element(self, args_dict):
        self.course_fs.remove_element(args_dict["element_id"], args_dict["topic_id"], args_dict["course_id"])

    def list_courses(self, arg):
        return {"message": self.permission_mgr.get_user_permissions(self._logged_user)}

    def list_topics(self, args_dict):
        return {"message": self.course_fs.get_topics_list(args_dict["course_id"])}

    def list_elements(self, args_dict):
        return {"message": self.course_fs.get_elements_list(args_dict["topic_id"], args_dict["course_id"])}

    def get_course_attributes(self, args_dict):
        return {"message": self.course_fs.get_course_attributes(args_dict["course_id"])}

    def get_topic_attributes(self, args_dict):
        return {"message": self.course_fs.get_topic_attributes(args_dict["topic_id"], args_dict["course_id"])}

    def get_element_attributes(self, args_dict):
        return {"message": self.course_fs.get_element_attributes(args_dict["element_id"], args_dict["topic_id"],
                                                                 args_dict["course_id"])}

    def load_element_html(self, cose):
        element_html = self.course_fs.get_element_html(cose["element_id"], cose["topic_id"], cose["course_id"])
        element_title = str(element_html.title.string)
        element_content = element_html.content
        webview.set_title(element_title)

        lesson_model = self._load_html_lesson_model()
        html_page = lesson_model.format(
            title=element_title, content=element_content
        ).replace("\r", "").replace("\n", "")

        return {"message": html_page}

    @staticmethod
    def close_everything(*args):
        print("gesu crosto")
        sys.exit(0)

    @staticmethod
    def _load_html_lesson_model():
        with urllib.request.urlopen("http://localhost:8080/html/lesson_model.html") as html_file:
            return html_file.read().decode("utf-8")
