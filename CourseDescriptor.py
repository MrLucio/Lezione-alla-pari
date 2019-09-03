from datetime import datetime
from shutil import copyfile
from Error import Error
import json
import time
import os


class CourseDescriptor():

    DEFAULT_DESCRIPTOR_JSON = {
        "courses counter": 1,
        "topics counter": 1,
        "elements counter": 1,
        "courses": {}
    }

    AVAILABLE_ELEMENT_TYPES = ["lesson", "quiz"]
    # DEFAULT DIRECTORY FOR DESCRIPTOR FILE
    DEFAULT_DESCRIPTOR_PATH = os.path.join("data", "descriptor.json")
    DEFAULT_BACKUP_FOLDER = os.path.join("data", "backup_descriptor")
    DEFAULT_INDENT_LEVEL = 4

    def __init__(self):
        """L'init di questa classe controlla che il file descrittore esista e, in caso contrario,
        ne crea uno nuovo"""

        self.create_descriptor_file()

    def create_descriptor_file(self, overwrite=False, backup=True):
        """Funzione che crea un nuovo file descrittore, sostituendone uno già esistente in base
        al parametro "overwrite" e, nel caso, creandone un backup in base al parametro "backup"

        :param overwrite: Parametro che decide se sostituire o meno un file descrittore già esistente
        :type overwrite: bool
        :param backup: Parametro che decide se creare un file di backup del file descrittore che si vuole sostituire

        :returns: True se l'operazione è andata a buon fine altrimenti False
        :rtype: bool"""

        # Verifico che non esista già un file descrittore oppure che "overwrite" valga True
        if not os.path.isfile(CourseDescriptor.DEFAULT_DESCRIPTOR_PATH) or overwrite:

            if backup:
                self._create_backup_folder()
                self._create_backup_file()

            # Creo e inserisco la struttura basilare nel nuovo file descrittore
            with open(CourseDescriptor.DEFAULT_DESCRIPTOR_PATH, "w") as file_object:
                file_object.write(
                    json.dumps(
                        CourseDescriptor.DEFAULT_DESCRIPTOR_JSON, indent=4)
                )

            return True

        return False

    def filter_deleted(self, unfiltered_dict):
        filtered_result = {}
        for key, value in unfiltered_dict.items():
            if not value["delete date"]:
                filtered_result[key] = value
        return filtered_result

    def get_new_course_id(self):
        """Funzione che genera un id univoco per un corso

        :returns: Id del corso
        :rtype: str"""

        descriptor_data = self._read_descriptor_data()

        # Prelevo l'ultimo id e aumento il suo valore per la prossima entry
        course_id = "c-" + str(descriptor_data["courses counter"])
        descriptor_data["courses counter"] += 1

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return course_id

    def get_new_topic_id(self):
        """Funzione che genera un id univoco per un topic

        :returns: Id del topic
        :rtype: str"""

        descriptor_data = self._read_descriptor_data()

        # Prelevo l'ultimo id e aumento il suo valore per la prossima entry
        topic_id = "t-" + str(descriptor_data["topics counter"])
        descriptor_data["topics counter"] += 1

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return topic_id

    def get_new_element_id(self):
        """Funzione che genera un id univoco per un elemento

        :returns: Id dell'elemento
        :rtype: str"""

        descriptor_data = self._read_descriptor_data()

        # Prelevo l'ultimo id e aumento il suo valore per la prossima entry
        element_id = "e-" + str(descriptor_data["elements counter"])
        descriptor_data["elements counter"] += 1

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return element_id

    def get_courses_list(self):
        """Funzione che restituisce la lista dei corsi disponibili nel file descrittore

        :returns: Lista dei corsi
        :rtype: list"""

        # Recupero il contenuto del file descrittore
        descriptor_data = self._read_descriptor_data()

        filtered_data = self.filter_deleted(descriptor_data["courses"])

        return list(filtered_data.keys())

    def get_topics_list(self, course_id):
        """Funzione che restituisce la lista dei topic disponibili di un corso nel file descrittore

        :param course_id: Id del corso di cui si vogliono conoscere i topic
        :type course_id: str

        :returns: Lista dei topic presenti nel corso
        :rtype: list"""

        # Recupero il contenuto del file descrittore
        descriptor_data = self._read_descriptor_data()

        filtered_data = self.filter_deleted(
            descriptor_data["courses"][course_id]["topics"])

        return list(filtered_data.keys())

    def get_elements_list(self, topic_id, course_id):
        """Funzione che restituisce la lista degli elementi disponibili di un topic di un corso
        nel file descrittore

        :param topic_id: Id del topic di cui si vogliono conoscere gli elementi
        :type topic_id: str
        :param course_id: Id del corso contenente il topic di cui si vogliono conoscere gli elementi
        :type course_id: str

        :returns: Lista degli elementi presenti nel topic del corso
        :rtype: list"""

        # Recupero il contenuto del file descrittore
        descriptor_data = self._read_descriptor_data()

        filtered_data = self.filter_deleted(
            descriptor_data["courses"][course_id]["topics"][topic_id]["elements"]
        )

        return list(filtered_data.keys())

    def get_course_attributes(self, course_id):
        """Funzione che restituisce gli attributi di un corso

        :param course_id: Id del corso
        :type course_id: str

        :returns: Attributi del corso
        :rtype: dict"""

        descriptor_data = self._read_descriptor_data()

        return descriptor_data["courses"][course_id]

    def get_topic_attributes(self, topic_id, course_id):
        """Funzione che restituisce gli attributi di un topic di un corso

        :param topic_id: Id del topic di cui si vogliono conoscere gli attributi
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic di cui si vogliono conoscere gli attributi
        :type course_id: str

        :returns: Attributi del topic
        :rtype: dict"""

        descriptor_data = self._read_descriptor_data()

        return descriptor_data["courses"][course_id]["topics"][topic_id]

    def get_element_attributes(self, element_id, topic_id, course_id):
        """Funzione che restituisce gli attributi di un elemento di un topic in un corso

        :param element_id: Id dell'elemento di cui si vogliono conoscere gli attributi
        :type element_id: str
        :param topic_id: Id del topic che contiene l'elemento di cui si vogliono conoscere gli attributi
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic e quindi dell'elemento di cui si vogliono conoscere gli attributi
        :type course_id: str

        :returns: Attributi del corso
        :rtype: dict"""

        descriptor_data = self._read_descriptor_data()

        return descriptor_data["courses"][course_id]["topics"][topic_id]["elements"][element_id]

    def add_course(self, course_name, course_id):
        """Funzione che permette l'aggiunta di un corso

        :param course_name: Nome del corso da aggiungere
        :type course_name: str
        :param course_id: Id del corso
        :type course_id: str

        :returns: True se l'azione è andata a buon fine altrimenti, nel caso il nome del corso non fosse valido, False
        :rtype: bool"""

        # Controllo che il nome del corso sia valido
        if not isinstance(course_name, str):
            return False

        descriptor_data = self._read_descriptor_data()

        # Creo la entry del nuovo corso
        new_course = {
            "name": course_name, "topics": {},
            "creation date": datetime.now().isoformat(),
            "delete date": None
        }
        descriptor_data["courses"][course_id] = new_course

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return True

    def remove_course(self, course_id):
        """Funzione che permette di cancellare un corso

        :param course_id: Id del corso da cancellare
        :type course_id: str

        :returns: True se l'azione è andata a buon fine altrimenti False
        :rtype: bool"""

        # Controllo che il corso esista
        if not course_id in self.get_courses_list():
            return False

        descriptor_data = self._read_descriptor_data()

        # Recupero la lista dei corsi dal file descrittore e cancello la entry
        courses_list = descriptor_data["courses"]
        courses_list[course_id]["delete date"] = datetime.now().isoformat()

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return True

    def add_topic(self, topic_name, topic_id, course_id):
        """Funzione che permette l'aggiunta di un topic

        :param topic_name: Nome del topic da aggiungere
        :type topic_name: str
        :param topic_id: Id del topic
        :type topic_id: str
        :param course_id: Id del corso in cui inserire il topic
        :type course_id: str

        :returns: True se l'azione è andata a buon fine altrimenti, nel caso il nome del topic non fosse valido, False
        :rtype:"""

        # Controllo che il nome del topic sia valido
        if not isinstance(topic_name, str):
            return False

        descriptor_data = self._read_descriptor_data()

        # Creo la entry del nuovo topic
        new_topic = {
            "name": topic_name, "elements": {},
            "creation date": datetime.now().isoformat(),
            "delete date": None
        }
        descriptor_data["courses"][course_id]["topics"][topic_id] = new_topic

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return True

    def remove_topic(self, topic_id, course_id):
        """Funzione che permette di cancellare un topic

        :param topic_id: Id del topic da cancellare
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic da cancellare
        :type course_id: str

        :returns: True se l'azione è andata a buon fine altrimenti False
        :rtype: bool"""

        # Controllo che il corso esista
        if not topic_id in self.get_topics_list(course_id):
            return False

        descriptor_data = self._read_descriptor_data()

        # Recupero la lista dei topic dal file descrittore e cancello la entry
        topics_list = descriptor_data["courses"][course_id]["topics"]
        topics_list[topic_id]["delete date"] = datetime.now().isoformat()

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return True

    def add_element(self, element_name, element_type, element_id, topic_id, course_id):
        """Funzione che permette l'aggiunta di un elemento

        :param element_name: Nome dell'elemento da aggiungere
        :type element_name: str
        :param element_type: Tipo dell'elemento che si vuole creare ("lesson" oppure "quiz")
        :type element_type: str
        :param element_id: Id dell'elemento
        :type element_id: str
        :param topic_id: Id del topic che contiene l'elemento
        :type topic_id: str
        :param course_id: Id del corso che contiene il topic che a sua volta contiene l'elemento
        :type course_id: str

        :returns: True se l'azione è andata a buon fine altrimenti, nel caso il nome o il tipo dell'elemento non siano validi, False
        :rtype: bool"""

        # Controllo che il nome dell'elemento sia valido
        if not isinstance(element_name, str):
            return False

        # Controllo che il tipo dell'elemento sia valido
        if not element_type in CourseDescriptor.AVAILABLE_ELEMENT_TYPES:
            return False

        descriptor_data = self._read_descriptor_data()

        # Creo la entry del nuovo elemento
        new_element = {
            "name": element_name, "type": element_type,
            "creation date": datetime.now().isoformat(),
            "edit date": datetime.now().isoformat(),
            "delete date": None
        }
        descriptor_data["courses"][course_id]["topics"][topic_id]["elements"][element_id] = new_element

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return True

    def edit_element(self, element_name, element_id, topic_id, course_id):

        # Controllo che l'elemento esista
        if not element_id in self.get_elements_list(topic_id, course_id):
            return False

        descriptor_data = self._read_descriptor_data()

        # Recupero la lista degli elementi dal file descrittore e cancello la entry
        elements_list = descriptor_data["courses"][course_id]["topics"][topic_id]["elements"]
        elements_list[element_id]["delete date"] = datetime.now().isoformat()

    def remove_element(self, element_id, topic_id, course_id):
        """Funzione che permette di cancellare un elemento

        :param element_id: Id dell'elemento da cancellare
        :type element_id: str
        :param topic_id: Id del topic che contiene l'elemento da cancellare
        :type topic_id:str
        :param course_id: Id del corso che contiene il topic che a sua volta contiene l'elemento da cancellare
        :type course_id: str

        :returns: True se l'azione è andata a buon fine altrimenti False
        :rtype: bool"""

        # Controllo che l'elemento esista
        if not element_id in self.get_elements_list(topic_id, course_id):
            return False

        descriptor_data = self._read_descriptor_data()

        # Recupero la lista degli elementi dal file descrittore e cancello la entry
        elements_list = descriptor_data["courses"][course_id]["topics"][topic_id]["elements"]
        elements_list[element_id]["delete date"] = datetime.now().isoformat()

        # Aggiorno il file descrittore
        self._write_descriptor_data(descriptor_data)

        return True

    @staticmethod
    def _read_descriptor_data():
        """Funzione che restituisce il contenuto del file descrittore

        :returns: Contenuto del file descrittore
        :rtype: dict"""

        with open(CourseDescriptor.DEFAULT_DESCRIPTOR_PATH, "r") as file_object:
            file_json = json.loads(file_object.read())

        return file_json

    @staticmethod
    # Caution while writing descriptor, it will overwrite everything!
    def _write_descriptor_data(new_descriptor, backup=False):
        """Funzione che permette di scrivere sul file descrittore. La scrittura non avviene
        in modalità "append", ecco perchè bisogna stare attenti altrimenti si rischia di
        perdere tutto il contenuto del file descrittore

        :param new_descriptor: Nuovo contenuto del file descrittore
        :type new_descriptor: dict
        :param backup: Parametro che decide se creare un file di backup del file descrittore prima di scriverci sopra
        :type backup: bool

        :returns: True per indicare che l'azione è andata a buon fine
        :rtype: bool"""

        # Converto "new_descriptor" (di tipo "dict") in una stringa così da poterne scrivere il contenuto sul file descrittore
        new_descriptor = json.dumps(
            new_descriptor,
            indent=CourseDescriptor.DEFAULT_INDENT_LEVEL
        )

        # Apro e scrivo il nuovo contenuto sul file descrittore
        with open(CourseDescriptor.DEFAULT_DESCRIPTOR_PATH, "w") as file_object:
            file_object.write(new_descriptor)
            file_object.close()

        return True

    @staticmethod
    def _create_backup_file():
        """Funzione che controlla che esista un file descrittore e ne crea una copia
        nella cartella di backup. Ogni file di backup conterrà nel suo nome la data di creazione,
        che permetterà di identificarlo più facilmente

        :returns: True se l'operazione è andata a buon fine altrimenti errore
        :rtype: bool o Error"""

        if not os.path.isfile(CourseDescriptor.DEFAULT_DESCRIPTOR_PATH):
            return Error("backup", "Impossibile fare backup su file non esistente")

        current_date = datetime.now().isoformat()

        # Copio il file nella cartella di backup e lo identifico tramite la data corrente
        copyfile(
            CourseDescriptor.DEFAULT_DESCRIPTOR_PATH,
            os.path.join(
                CourseDescriptor.DEFAULT_BACKUP_FOLDER,
                "descriptor{}.json".format(current_date)
            )
        )

        return True

    @staticmethod
    def _create_backup_folder():
        """Funzione che controlla che la cartella di backup del file descrittore esista e,
        in caso contrario, ne crea una nuova

        :returns: True se la cartella è stata creata altrimenti False
        :rtype: bool"""

        if not os.path.isdir(CourseDescriptor.DEFAULT_BACKUP_FOLDER):
            os.makedirs(CourseDescriptor.DEFAULT_BACKUP_FOLDER)
            return True

        return False

    @staticmethod
    def _is_course_descriptor(value):
        """Funzione che verifica che una variabile sia di tipo CourseDescriptor

        :param value: Valore da verificare
        :type value: any

        :returns: True se la variabile è di tipo CourseDescriptor oppure False
        :rtype: bool"""

        if isinstance(value, CourseDescriptor):
            return True
        return False
