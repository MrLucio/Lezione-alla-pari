from datetime import datetime
from Error import Error
import json
import os
import re   


class QuizManager:

    def __init__(self, quiz_dict):
        self.quiz_dict = quiz_dict

    def get_quiz_dict(self):
        return self.quiz_dict

    def get_new_question_id(self):
        new_id = self.quiz_dict["questions"]["count"]
        self.quiz_dict["questions"]["count"] += 1

        return new_id

    def add_checkbox(self, question_text, wrong_answers, correct_answers):
        new_id = "q-"+str(self.get_new_question_id())
        self.quiz_dict["questions"][new_id] = {}
        self.quiz_dict["questions"][new_id]["type"] = "checkbox"
        self.quiz_dict["questions"][new_id]["text"] = question_text
        self.quiz_dict["questions"][new_id]["wrong_answers"] = wrong_answers
        self.quiz_dict["questions"][new_id]["correct_answers"] = correct_answers
        return new_id

    def add_radio(self, question_text, wrong_answers, correct_answer):
        new_id = "q-"+str(self.get_new_question_id())
        self.quiz_dict["questions"][new_id] = {}
        self.quiz_dict["questions"][new_id]["type"] = "radio"
        self.quiz_dict["questions"][new_id]["text"] = question_text
        self.quiz_dict["questions"][new_id]["wrong_answers"] = wrong_answers
        self.quiz_dict["questions"][new_id]["correct_answer"] = correct_answer
        return new_id

    def add_open(self, question_text, correct_answers):
        new_id = "q-"+str(self.get_new_question_id())
        self.quiz_dict["questions"][new_id] = {}
        self.quiz_dict["questions"][new_id]["type"] = "open"
        self.quiz_dict["questions"][new_id]["text"] = question_text
        self.quiz_dict["questions"][new_id]["correct_answers"] = correct_answers
        return new_id

    def remove_question(self, question_id):
        if question_id not in self.quiz_dict["questions"]:
            return Error("Question ID not found")
        
        del self.quiz_dict["questions"][question_id]
        return True

    def add_attempt(self, user_id, mark, answers):
        if user_id not in self.quiz_dict["stats"]:
            self.quiz_dict["stats"][user_id] = []
        
        self.quiz_dict["stats"][user_id].append({"date": datetime.now().isoformat(), "mark": mark, "answers": answers})