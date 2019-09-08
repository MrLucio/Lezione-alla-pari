from CourseDescriptor import CourseDescriptor
from bs4 import BeautifulSoup
from Error import Error
import shutil
import os
import json


class CourseFileSystem:

    DEFAULT_COURSES_PATH = os.path.join("data", "Courses")

    def __init__(self):
        """L'init di questa classe controlla che la cartella dei corsi esista e, in caso contrario,
        ne crea una nuova; successivamente viene creata un'istanza di CourseDescriptor che
        verrà utilizzata per la modifica di dati sul file descrittore."""

        self._create_courses_folder()

        # Creo e salvo un'istanza del modulo CourseDescriptor che verrà utilizzata da altre funzioni
        self.descriptor = CourseDescriptor()

    def get_courses_list(self):
        """Una funzione che restituisce la lista di corsi disponibili, controllando che siano
        presenti sia sul FileSystem che nel file descrittore

        :returns: Lista di corsi disponibili
        :rtype: list"""

        fs_courses = os.listdir(CourseFileSystem.DEFAULT_COURSES_PATH)
        descriptor_courses = self.descriptor.get_courses_list()

        # Controllo incrociato tra corsi nel FileSystem e nel file descrittore
        return [course for course in fs_courses if course in descriptor_courses]

    def get_topics_list(self, course_id):
        """Una funzione che restituisce la lista di topic disponibili di un corso, controllando che siano
        presenti sia sul FileSystem che nel file descrittore

        :param course_id: Id del corso di cui si vogliono conoscere i topic
        :type course_id: str

        :returns: Lista di topic disponibili per quel corso
        :rtype: list"""

        fs_topics = os.listdir(os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id))
        descriptor_topics = self.descriptor.get_topics_list(course_id)

        # Controllo incrociato tra topics nel FileSystem e nel file descrittore
        return [topic for topic in fs_topics if topic in descriptor_topics]

    def get_elements_list(self, topic_id, course_id):
        """Funzione che restituisce la lista di elementi disponibili di un topic, controllando che siano
        presenti sia sul FileSystem che nel file descrittore

        :param topic_id: Id del topic di cui si vogliono conoscere gli elementi
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic di cui si vogliono conoscere gli elementi
        :type course_id: str

        :returns: Lista di elementi disponibili per quel topic
        :rtype: list"""

        fs_elements = os.listdir(os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id))
        descriptor_elements = self.descriptor.get_elements_list(
            topic_id, course_id)

        # Controllo incrociato tra elementi nel FileSystem e nel file descrittore
        return [element for element in fs_elements if element in descriptor_elements]

    def add_course(self, course_name):
        """Funzione che permette l'aggiunta di un corso

        :param course_name: Nome del corso da creare. Verrà utilizzato dal modulo CourseDescriptor
        :type course_name: str

        :returns: Id del corso appena creato oppure errore
        :rtype: str o Error"""

        # Genero un id univoco per il corso
        new_course_id = self.descriptor.get_new_course_id()

        try:
            # Tento di creare la cartella del corso sul FileSystem
            os.mkdir(os.path.join(
                CourseFileSystem.DEFAULT_COURSES_PATH, new_course_id))
        except OSError:
            return Error("io_error", "Errore nella creazione del corso")

        # Tento di creare il corso all'interno del file descrittore
        if not self.descriptor.add_course(course_name, new_course_id):
            return Error("Errore durante la creazione del corso")

        return new_course_id

    def remove_course(self, course_id):
        """Funzione che permette di cancellare un corso

        :param course_id: Id del corso da cancellare
        :type course_id: str

        :returns: True se l'operazione è andata a buon fine oppure errore
        :rtype: bool o Error"""

        # Rimuovo il corso all'interno del file descrittore
        if not self.descriptor.remove_course(course_id):
            return Error("Errore durante la rimozione del corso")

        return True

    def add_topic(self, topic_name, course_id):
        """Funzione che permetta l'aggiunta di un topic

        :param topic_name: Nome del topic da creare
        :type topic_name: str
        :param course_id: Id del corso in cui inserire il topic
        :type course_id: str

        :returns: Id del topic appena creato oppure errore
        :rtype: str o Error"""

        # Genero un id univoco per il topic
        new_topic_id = self.descriptor.get_new_topic_id()

        # "Assemblo" la path del nuovo topic
        topic_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, new_topic_id
        )

        try:
            # Tento di creare la cartella del topic sul FileSystem
            os.mkdir(topic_dir)
        except OSError:
            return Error("io_error", "Errore nella creazione del topic")

        # Tento di creare il topic all'interno del file descrittore
        if not self.descriptor.add_topic(topic_name, new_topic_id, course_id):
            return Error("Errore durante la creazione del topic")

        return new_topic_id

    def remove_topic(self, topic_id, course_id):
        """Funzione che permette di cancellare un topic

        :param topic_id: Id del topic da cancellare
        :type topic_id: str

        :param course_id: Id del corso che contiene il topic
        :type course_id: str

        :returns: True se l'operazione è andata a buon fine oppure errore
        :rtype: bool o Error"""

        # "Assemblo" la path del topic da cancellare
        topic_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id
        )

        # Tento di rimuove il topic dal file descrittore
        if not self.descriptor.remove_topic(topic_id, course_id):
            return Error("Errore durante la rimozione del topic")

        return True

    def add_lesson(self, element_name, topic_id, course_id):
        """Funzione che permette l'aggiunta di una lezione

        :param element_name: Nome della lezione da aggiungere
        :type element_name: str
        :param topic_id: Id del topic che contiene l'elemento
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic che a sua volta contiene l'elemento
        :type course_id: str

        :returns: True se l'operazione è andata a buon fine oppure Errore
        :rtype: bool o Error"""

        # Genero un id univoco per l'elemento
        new_element_id = self.descriptor.get_new_element_id()

        # "Assemblo" la path dell'elemento da aggiungere
        element_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id, new_element_id
        )

        try:
            # Tento di creare la cartella dell'elemento sul FileSystem
            os.mkdir(element_dir)
        except OSError:
            return Error("io_error", "Errore nella creazione dell'elemento")

        # Creo il file "index.html" dell'elemento sul FileSystem e inserisco i vari tag
        with open(os.path.join(element_dir, "index.html"), "w") as html_file_object:
            html_file_object.write('')

        # Tento di creare l'elemento sul file descrittore
        if not self.descriptor.add_element(element_name, "lesson", new_element_id, topic_id, course_id):
            return Error("Errore durante la creazione dell'elemento")

        return new_element_id

    def add_quiz(self, element_name, topic_id, course_id):
        # Genero un id univoco per l'elemento
        new_element_id = self.descriptor.get_new_element_id()

        # "Assemblo" la path dell'elemento da aggiungere
        element_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id, new_element_id
        )

        try:
            # Tento di creare la cartella dell'elemento sul FileSystem e anche la sua cartella media, che conterrà i media dell'elemento
            os.mkdir(element_dir)
            os.mkdir(os.path.join(element_dir, "media"))
        except OSError:
            return Error("io_error", "Errore nella creazione dell'elemento")

        # Creo il file "index.html" dell'elemento sul FileSystem e inserisco i vari tag
        with open(os.path.join(element_dir, "index.json"), "w") as quiz_object:
            quiz_object.write(json.dumps({"questions":{"count":0}, "stats":{}}, indent=4))

        # Tento di creare l'elemento sul file descrittore
        if not self.descriptor.add_element(element_name, "quiz", new_element_id, topic_id, course_id):
            return Error("Errore durante la creazione dell'elemento")

    def edit_lesson(self, element_id, topic_id, course_id, element_html):

        # "Assemblo" la path dell'elemento
        element_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id, element_id
        )

        # Creo il parser html dell' elemento
        element_html_parser = BeautifulSoup(element_html, "html.parser")

        # Creo il file "index.html" dell'elemento sul FileSystem e inserisco i vari tag
        with open(os.path.join(element_dir, "index.html"), "w", encoding="utf-8") as html_file_object:
            html_file_object.write(
                element_html)

        return element_id

    def edit_quiz(self, element_id, topic_id, course_id, element_json):

        # "Assemblo" la path dell'elemento
        element_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id, element_id
        )

        # Creo il file "index.html" dell'elemento sul FileSystem e inserisco i vari tag
        with open(os.path.join(element_dir, "index.json"), "w") as quiz_object:
            quiz_object.write(json.dumps(element_json, indent=4))

        return element_id


    def remove_element(self, element_id, topic_id, course_id):
        """Funzione che permette di cancellare un elemento

        :param element_id: Id dell'elemento da cancellare
        :type element_id: str
        :param topic_id: Id del topic che contiene l'elemento
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic che a sua volta contiene l'elemento
        :type course_id: str

        :returns: True se l'operazione è andata a buon fine oppure errore
        :rtype: bool o Error"""

        # "Assemblo" la path dell'elemento da aggiungere
        element_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id, element_id
        )

        # Tento di rimuovere l'elemento dal file descrittore
        if not self.descriptor.remove_element(element_id, topic_id, course_id):
            return Error("Errore durante la cancellazione dell'elemento")

        return True

    def get_lesson_html(self, element_id, topic_id, course_id):
        """Funzione che restituisce il contenuto html di un elemento (lezione o quiz)

        :param element_id: Id dell'elemento da leggere
        :type element_id: str
        :param topic_id: Id del topic che contiene l'elemento
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic che a sua volta contiene l'elemento
        :type course_id: str

        :returns: Parser html dell'elemento oppure errore
        :rtype: bs4.BeautifulSoup o Error"""

        # "Assemblo" la path dell'elemento
        element_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id, element_id
        )

        try:
            # Tento di aprire l'elemento e di leggerne il contenuto
            with open(os.path.join(element_dir, "index.html")) as element_object:
                element_html = element_object.read().encode('utf-8').strip()
        except:
            return Error("Errore nella lettura dell'elemento")

        # Genero il parser che mi permetterà di accedere ai contenuti html dell'elemento con facilità
        element_html_parser = BeautifulSoup(element_html, "html.parser")

        return element_html_parser

    def get_quiz_json(self, element_id, topic_id, course_id):

        quiz_dir = os.path.join(
            CourseFileSystem.DEFAULT_COURSES_PATH, course_id, topic_id, element_id
        )

        try:
            # Tento di aprire il quiz e di leggerne il contenuto
            with open(os.path.join(quiz_dir, "index.json")) as quiz_object:
                return json.loads(quiz_object.read())
        except:
            return Error("Errore nella lettura dell'elemento")

    def get_course_attributes(self, course_id):
        """Funzione che restituisce gli attributi di un corso presenti nel file descrittore

        :param course_id: Id del corso
        :type course_id: str

        :returns: Attributi del corso
        :rtype: dict"""

        return self.descriptor.get_course_attributes(course_id)

    def get_topic_attributes(self, topic_id, course_id):
        """Funzione che restituisce gli attributi di un topic presenti nel file descrittore

        :param topic_id: Id del topic
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic
        :type course_id: str

        :returns: Attributi del topic
        :rtype: dict"""

        return self.descriptor.get_topic_attributes(topic_id, course_id)

    def get_element_attributes(self, element_id, topic_id, course_id):
        """Funzione che restituisce gli attributi di un elemento presenti nel file descrittore

        :param element_id: Id dell'elemento da leggere
        :type element_id: str
        :param topic_id: Id del topic che contiene l'elemento
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic che a sua volta contiene l'elemento
        :type course_id: str

        :returns: Attributi dell'elemento
        :rtype: dict"""

        return self.descriptor.get_element_attributes(element_id, topic_id, course_id)

    @staticmethod
    def _create_courses_folder():
        """Funzione che controlla che la cartella dei corsi esista e, in caso contrario,
        ne crea una nuova

        :returns: True se la cartella è stata creata altrimenti False
        :rtype: bool"""

        if not os.path.isdir(CourseFileSystem.DEFAULT_COURSES_PATH):
            os.mkdir(CourseFileSystem.DEFAULT_COURSES_PATH)
            return True
        return False

    @staticmethod
    def is_course_file_system(value):
        """Funzione che verifica che una variabile sia di tipo CourseFileSystem

        :param value: Valore da verificare
        :type value: any

        :returns: True se la variabile è di tipo CourseFileSystem oppure False
        :rtype: bool"""

        if isinstance(value, CourseFileSystem):
            return True
        return False
