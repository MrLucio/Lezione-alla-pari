import os
import re
from dateutil.parser import parse
from Error import Error
import xml.etree.ElementTree as ET


class UserManager:
    """La classe UserManager, rappresentata dal Controller nel modello MVC, è responsabile di tutta l'interazione con il
    database degli utenti. Esso presenta molte possibilità di aggiunta, modifica e rimozione."""

    DEFAULT_LOGIN_FILENAME = "user_data.xml"
    DEFAULT_DATA_DIRECTORY = "data"
    FULL_PATH = os.path.join(DEFAULT_DATA_DIRECTORY, DEFAULT_LOGIN_FILENAME)

    def __init__(self):
        """Lo scopo dell'init è parsare il file xml e creare un albero xml ad oggetti in memoria, facilmente editabile
        grazie alla libreria ElementTree"""
        self.check_files()
        self._tree = ET.parse(UserManager.FULL_PATH)
        self._users = self._tree.getroot()

    def get_userdata(self, id, name=False, surname=False, email=False, type=False):
        """Questa funzione fornisce, in base ai parametri selezionati, le informazioni di un utente dato il suo id.
        Fornisce anche una versione censurata della password, che per motivi di privacy non viene resa in plain text

        :param id: L'id dell'utente, caraterizzato dal formato u-numero
        :type id: str
        :param name: Esprima la volonta di chi invoca la funzione di aver fornito il nome
        :type name: bool
        :param surname: Esprima la volonta di chi invoca la funzione di aver fornito il cognome
        :type surname: bool
        :param email: Esprima la volonta di chi invoca la funzione di aver fornita l'email
        :type email: bool
        :param type: Esprima la volonta di chi invoca la funzione di aver fornito il tipo di utente
        :type type: bool

        :returns: False, se l'utente specificato non esiste
        :rtype: bool"""
        child = self._users.find(".user[@id='{}']".format(id))
        ret = {}
        if child:
            if name:
                ret["name"] = child.find("name").text
            if surname:
                ret["surname"] = child.find("surname").text
            if email:
                ret["email"] = child.find("email").text
            if type:
                ret["type"] = child.find("type").text
            return ret
        return False

    def user_exists(self, id):
        """Questa funzione fornisce un oggetto User, fornito un id. Questa funzione sarà utile al modulo successivo,
        che avrà accesso solo ai dati dell'utente autenticato, senza possibilità di modificarli o accedere al database

        :param id: l'id dell'utente da restituire sotto forma di oggetto
        :type id: str
        :return: User, se l'id inserito è corretto
        :rtype: User
        :return: False, se l'id inserito è errato
        :rtype: bool
        """
        child = self._users.find(".user[@id='{}']".format(id))
        if child:
            return True
        return False

    def check_login(self, email, password):
        """Questa funzione, data una email ed una password, verifica passo per passo i parametri, restituendo una
        stringa che esprime quali dei campi sono errati, oppure l'id se email e password trovano riscontro ad un utente
        esistente nel database

        :param email: l'email dell'utente che deve autenticarsi
        :param password: la password dell'utente che deve autenticarsi
        :type: str

        :return inexistent: Un Error, che può esprimere uno di tre messaggi:
        :rtype: str"""

        child = self._users.find(".user[email='{}']".format(email))
        if child:
            if child.find("password").text == password:
                if child.attrib["active"] == "true":
                    return child.attrib['id']
                return Error("inactive", "User has been deactivated, contact support for details")
            return Error("password", "Incorrect Password")
        return Error("inexistent", "Incorrect Email")

    def add_user(self, type, name, surname, password, email, birthdate):

        """Questa funzione presenta la possibilità di aggiungere un utente al database, ma soltanto se i dati inseriti
        nei campi sono validi. Se essi non lo fossero, la funzione restituisce un Error con la quale è possibile
        informare l'utente del suo errore.

        :param type: Il tipo di utente da aggiungere
        :param name: Il nome dell'utente da aggiungere
        :param surname: Il cognome dell'utente da aggiungere:
        :param password: La password dell'utente da aggiungere
        :param email: La email dell'utente da aggiungere
        :param birthdate: La data di nascita dell'utente da aggiungere
        :type: str

        :returns: Un oggetto Error, che contiene il tipo di errore insieme ad una stringa da recapitare all'utente
        :rtype: Error"""

        if not self._type_valid(type):
            return Error("type", "Please select an user type")

        elif not self._name_valid(name):
            return Error("name", "Please type a valid name")

        elif not self._name_valid(surname):
            return Error("surname", "Please type a valid surname")

        elif not self._password_valid(password):
            return Error("password", "Please type a valid password")

        elif not self._email_valid(email):
            return Error("email", "Please type a valid email address")

        elif not self._email_unique(email):
            return Error("uniqueemail", "Your email is already in use")

        elif not self._birthdate_valid(birthdate):
            return Error("birthdate", "Please type a valid birthdate")

        # Creo un nuovo utente in nel tree di questa sessione
        new_id = self.get_new_id()
        new_user = ET.SubElement(self._users, "user", attrib={"active": "true", "id": new_id})

        new_user_type = ET.SubElement(new_user, "type")
        new_user_name = ET.SubElement(new_user, "name")
        new_user_surname = ET.SubElement(new_user, "surname")
        new_user_password = ET.SubElement(new_user, "password")
        new_user_email = ET.SubElement(new_user, "email")
        new_user_birthdate = ET.SubElement(new_user, "birthdate")

        new_user_type.text = type
        new_user_name.text = name
        new_user_surname.text = surname
        new_user_password.text = password
        new_user_email.text = email
        new_user_birthdate.text = birthdate

        self._indent_tree(self._users)

    def modify_user(self, id, **kwargs):

        """Una funzione che permette di modificare email, password e tipo di un utente già esistente. Si può modificare
        anche più di un parametro alla volta, ma si è limitati a questi tre. La funzione esegue i corretti controlli
        sulle key che conosce e le modifica se i loro valori sono corretti, igorando quelle che non conosce

        :param id: l'ID del utente da modificare
        :type: str
        :param kwargs: un dizionario che esprime il parametro da modificare, con un certo valore
        :type: dict

        :returns: Un oggetto Error, che comunica il tipo di errore ed un eventuale messaggio da recapitare all'utente
        :rtype: Error"""

        child = self._users.find(".user[@id='{}']".format(id))
        for key, value in kwargs.items():
            child_tag = child.find(key)
            if key == "email":
                if self._email_valid(value):
                    if self._email_unique(value):
                        child_tag.text = value
                    else:
                        return Error("uniqueemail", "This email is already in use")
                else:
                    return Error("email", "Please type a valid email address")
            elif key == "type":
                if self._type_valid(value):
                    child_tag.text = value
                else:
                    return Error("type", "Please select an user type")
            elif key == "password":
                if self._password_valid(value):
                    child_tag.text = value
                else:
                    return Error("password", "Please type a valid password")
            self.update_file()

    def remove_user(self, id):
        """FUNZIONE PER TESTING Una funzione che permette di rimuovere completamente un utente dal database utenti.
        Attenzione che questo non rimuove i suoi permessi, i suoi risultati nei test e la sua presenza in alcuni corsi,
        e questo potrebbe causare problemi nella CourseApplication. Usare deactivate_user se possibile.

        :param id: L'ID dell'utente da rimuovere
        :type id: str"""

        child = self._users.find(".user[@id='{}']".format(id))
        self._users.remove(child)

    def activate_user(self, id):
        """Una funzione che permette di riattivare un utente, dato il suo id.

        :param id: L'ID dell'utente da abilitare
        :type id: str"""

        child = self._users.find(".user[@id='{}']".format(id))
        child.attrib["active"] = "true"

    def deactivate_user(self, id):
        """Una funzione che permette di disabilitare un utente, dato il suo id.

        :param id: L'ID dell'utente da disabilitare
        :type id: str"""

        child = self._users.find(".user[@id='{}']".format(id))
        child.attrib["active"] = "false"

    def get_new_id(self):
        """Una funzione che fornisce un nuovo id, aggiornando il contatore di utenti nel database xml

        :returns: Un nuovo ID, che non appartiene a nessun utente
        :rtype: str"""

        self._users.attrib["usercounter"] = str(int(self._users.attrib["usercounter"])+1)
        return "u-"+self._users.attrib["usercounter"]

    def get_last_id(self):
        """Una funzione che fornisce l'ultimo id aggiunto, corrispondente a quello dell'ultimo utente nel file xml

        :returns: L'ID dell'ultimo utente aggiunto
        :rtype: str"""

        return "u-" + self._users.attrib["usercounter"]

    def update_file(self):
        """La funzione responsabile di scrivere sul file xml l'albero presente in memoria"""
        self._tree.write(UserManager.FULL_PATH, "UTF-8")

    def _indent_tree(self, elem, indent=0):
        """La funzione responsabile di effettuare l'indentazione dell'albero presente in memoria, in modo che appaia
        indentato nel file xml. Ringrazio https://norwied.wordpress.com/ per il codice di questa funzione, che ho solo
        modificato in parte."""

        i = "\n" + ("\t" * indent)
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "\t"
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self._indent_tree(elem, indent + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if indent and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    @staticmethod
    def check_files():
        """Questa funzione verifica se la cartella data e il file xml esistono. Se esse mancano, vengono create, e viene
        scritta la root nel file xml."""

        if os.path.isdir(UserManager.DEFAULT_DATA_DIRECTORY):
            if os.path.exists(UserManager.FULL_PATH):
                return True
            else:
                with open(UserManager.FULL_PATH, "w+") as f:
                    f.write("<users usercounter=\"0\">\n</users>")
        else:
            os.mkdir(UserManager.DEFAULT_DATA_DIRECTORY)
            with open(UserManager.FULL_PATH, "w+") as f:
                f.write("<users usercounter=\"0\">\n</users>")

    @staticmethod
    def _type_valid(type):
        if not re.match(r'^((Teacher)|(Student))$', type):
            return False
        return True

    @staticmethod
    def _name_valid(name):
        if not re.match(r'^[a-zA-Z]+(([\',. \-][a-zA-Z ])?[a-zA-Z]*)*$', name):
            return False
        return True

    @staticmethod
    def _password_valid(password):
        if not re.match(r'((?=.+\d)(?=.+[a-z])(?=.+[@#$%^&+=]).{8,20})', password):
            return False
        return True

    @staticmethod
    def _email_valid(email):
        if not re.match(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', email):
            return False
        return True

    def _email_unique(self, email):
        if self._users.find(".user[email='{}']".format(email)):
            return False
        return True

    @staticmethod
    def _birthdate_valid(birthdate):
        try:
            parse(birthdate, dayfirst=True)
            return True
        except ValueError:
            return False
