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
        new_id = self.quiz_dict["count"]
        self.quiz_dict["count"] += 1

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

    def evaluate_answers(self, user_id, answers):
        scores = {}
        for key, value in answers.items():
            question_type = self.quiz_dict["questions"][key]["type"]

            if question_type == "checkbox":
                wrong_answers = [
                    i for i in value if i in self.quiz_dict["questions"][key]["wrong_answers"]]
                correct_answers = [
                    i for i in value if i in self.quiz_dict["questions"][key]["correct_answers"]]
                points = len(correct_answers) - len(wrong_answers)
                if points >= 0:
                    scores[key] = points / \
                        len(self.quiz_dict["questions"]
                            [key]["correct_answers"])
                else:
                    scores[key] = 0
            elif question_type == "radio":
                if value == self.quiz_dict["questions"][key]["correct_answer"]:
                    scores[key] = 1
                else:
                    scores[key] = 0
            elif question_type == "open":
                if value in self.quiz_dict["questions"][key]["correct_answers"]:
                    scores[key] = 1
                else:
                    scores[key] = 0
        return scores

    def add_attempt(self, user_id, answers, scores):
        if user_id not in self.quiz_dict["stats"]:
            self.quiz_dict["stats"][user_id] = []
        mark = sum(scores.values())/len(scores) * 10
        self.quiz_dict["stats"][user_id].append({"date": datetime.now(
        ).isoformat(), "mark": mark, "answers": answers, "scores": scores})

    def get_user_attempts(self, user_id):
        if user_id in self.quiz_dict["stats"]:
            return self.quiz_dict["stats"][user_id]
        else:
            return None
