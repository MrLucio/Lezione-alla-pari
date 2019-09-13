from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk

from UserManager import UserManager
from Error import Error


class LoginApplication(Tk):

    """Questa classe fornisce il framework utile per creare e memorizzare finestre, permettendo una comunicazione tra
    di esse molto semplice e diretta. Essa equivale alla View in un modello MVC, ma in realtà l'albero MVC è nestato,
    perchè questa classe funge da View_Controller e da Model, perchè tutte le finestre vengono memorizzate e fatte
    visualizzare qui. I vari frame rappresenterebbero finalmente la View vera e propria."""

    LARGE_FONT = ("Verdana", 12)

    def __init__(self, *args, **kwargs):

        """L'init di questa classe va a creare la root e crea il dizionario dei frame e delle finestre attive, utile
        per selezionare quale di queste verrà visualizzata dall'utente. Di default, mostra la Login Page

        :param args: una lista di eventuali parametri da passare all'init della root
        :type args: list
        :param kwargs: un dizionario di eventuali parametri da passare all'init della root
        :type kwargs: dict"""

        Tk.__init__(self, *args, **kwargs)

        self.controller = UserManager()

        self.title("Login")
        self.resizable(False, False)
        self.iconbitmap("media/logo.ico")

        self.frames = {}
        self.windows = {}

        # Istanzio le pagine "autonome" cioè che non si basano sull'output di altre finestre
        for page in (LoginPage, RegisterPage):
            frame = page(self)
            self.frames[page] = frame

        self.show_frame(LoginPage)

    def show_frame(self, page):
        """Questa funzione permette di mostrare una pagina all'utente

        :param page: La classe della pagina/frame da mostrare all'utente
        :type: Frame"""

        # Rimuovo eventuali pagine mostrate all'utente dalla view
        for key, value in self.frames.items():
            value.pack_forget()

        # Mostro quella inserita nel parametro
        page = self.frames[page]
        page.pack(side="top", fill="both", expand=True)

    def get_frame(self, page):
        """Una funzione che permette di prendere l'istanza corrente della pagina presa come parametro
        :param page: L'istanza del frame scelto
        :type: Frame"""

        return self.frames[page]

    def add_frame(self, page, *args):
        """Una funzione che permette di aggiungere una pagina al dizionario, se essa non esiste già.

        :param page: La pagina da aggiungere al dizionario, che verrà istanziata grazie a questa funzione
        :type page: Frame
        :param args: Parametri extra da passare alla pagina
        :type args: list"""

        if page not in self.frames:
            self.frames[page] = page(*args)

    def get_window(self, window):
        """Una funzione che permette di prendere l'istanza di una finestra
        :param window: L'istanza della finestra da prendere
        :type window: Toplevel

        :returns: L'istanza della finestra
        :rtype: Frame"""
        return self.windows[window]

    def add_window(self, window, *args):
        """Una funzione che permette di aggiungere una finestra al dizionario, istanziandola
        :param window: La classe della finestra da istanziare
        :type window: Toplevel"""

        self.windows[window] = window(*args)

    def remove_window(self, window):
        """Una funzione che permette la rimozione di una finestra dal dizionario, distruggendo anche la sua istanza
        :param window: La classe della finestra da distruggere
        :type window: Toplevel"""

        if window in self.windows:
            del self.windows[window]


class LoginPage(Frame):

    """La pagina di Login, grazie alla quale l'utente può autenticarsi"""

    def __init__(self, view_controller):

        """L'init di questa classe istanzia eventuali oggetti di tkinter e ttk

        :param view_controller: Viene passata un'istanza della LoginApplication, in modo che la pagina possia interagire
        con la view dell'utente, cambiandola ad esempio con un pulsante, e per istanziare altre finestre
        :type view_controller: LoginApplication"""

        super().__init__(view_controller)
        self._view_controller = view_controller
        self.configure(background="#4d13d1")

        image_size = 120

        pil_image = Image.open("media/logo.jpg").resize((image_size, image_size))
        self.img = ImageTk.PhotoImage(pil_image)
        lbimg = ttk.Label(self, image=self.img)
        lbimg.grid(row=2, column=1, rowspan=3)

        self.lb3 = Label(self, text="", bd=1, relief=SUNKEN)
        self.lb3.grid(row=5, column=1, columnspan=4, sticky=N+S+E+W)

        self.e1 = FormEntry(self, text="Email")
        self.e1.grid(row=2, column=2, padx=10, sticky=EW, columnspan=2)

        self.e2 = FormEntry(self, text="Password", show="*")
        self.e2.grid(row=3, column=2, padx=10, sticky=EW, columnspan=2)

        btn1 = ttk.Button(self, text="Log-in", command=lambda: self.login())
        btn1.grid(row=4, column=2, padx=10)

        btn2 = ttk.Button(self, text="Register", command=lambda: view_controller.show_frame(RegisterPage))
        btn2.grid(row=4, column=3, padx=10)

    def login(self):

        """Questa funzione permette all'utente di fare il login e autenticarsi nella app. Se il login è corretto, viene
        istanziata e mostrata la LoginSuccessPage, altrimenti le stringhe restituite dalla funzione check_login
        nell'UserManager servono per capire cos'è andato storto, e dirlo all'utente in modo che possia correggere i suoi
        imput"""

        user_id = self._view_controller.controller.check_login(self.e1.get().lower(), self.e2.get())
        if isinstance(user_id, str):
            self._view_controller.add_frame(LoginSuccessPage, self._view_controller, user_id)
            self._view_controller.show_frame(LoginSuccessPage)

        elif isinstance(user_id, Error):
            self.lb3['text'] = user_id.get_message()


class RegisterPage(Frame):

    """La pagina di registrazione, che permette ad un utente di inserire i suoi dati nel database per fare il login"""

    def __init__(self, view_controller):

        """L'init di questa classe istanzia eventuali oggetti di tkinter e ttk

        :param view_controller: Viene passata un'istanza della LoginApplication, in modo che la pagina possia interagire
        con la view dell'utente, cambiandola ad esempio con un pulsante, e per istanziare altre finestre
        :type view_controller: LoginApplication"""

        super().__init__(view_controller)
        self.configure(background="#e67e22")

        image_width = 120
        image_height = 120

        self._view_controller = view_controller

        pil_image = Image.open("media/logo.jpg").resize((image_width, image_height))
        self.img = ImageTk.PhotoImage(pil_image)
        lbimg = ttk.Label(self, image=self.img, anchor="c")
        lbimg.grid(row=1, column=1, columnspan=2, sticky=EW)

        self.cb1 = ttk.Combobox(self, state="readonly", values=("User Type", "Student", "Teacher"))
        self.cb1.current(0)
        self.cb1.grid(row=2, column=1, columnspan=2, sticky=EW, padx=5, pady=7)

        self.lb1 = ttk.Label(self, text="Name must contain letters only")
        self.lb1.grid(row=4, column=1, columnspan=2, sticky=EW, padx=5)
        self.lb1.grid_remove()

        self.e1 = FormEntry(self, "Name", self.lb1)
        self.e1.grid(row=3, column=1, columnspan=2, sticky=EW, padx=5, pady=7)

        self.lb2 = ttk.Label(self, text="Surname must contain letters only")
        self.lb2.grid(row=6, column=1, columnspan=2, sticky=EW, padx=5)
        self.lb2.grid_remove()

        self.e2 = FormEntry(self, "Surname", self.lb2)
        self.e2.grid(row=5, column=1, columnspan=2, sticky=EW, padx=5, pady=7)

        self.lb3 = ttk.Label(self, text="Password must be 8 char. long, and contain 1 letter, 1 symbol and 1 number")
        self.lb3.grid(row=8, column=1, columnspan=2, sticky=EW, padx=5)
        self.lb3.grid_remove()

        self.e3 = FormEntry(self, "Password", self.lb3, show="*")
        self.e3.grid(row=7, column=1, columnspan=2, sticky=EW, padx=5, pady=7)

        self.lb4 = ttk.Label(self, text="Email must follow the standard format")
        self.lb4.grid(row=10, column=1, columnspan=2, sticky=EW, padx=5)
        self.lb4.grid_remove()

        self.e4 = FormEntry(self, "Email", self.lb4)
        self.e4.grid(row=9, column=1, columnspan=2, sticky=EW, padx=5, pady=7)

        self.lb5 = ttk.Label(self, text="Birthdate must be inserted following the day-month-year format")
        self.lb5.grid(row=12, column=1, columnspan=2, sticky=EW, padx=5)
        self.lb5.grid_remove()

        self.e5 = FormEntry(self, "Birthdate", self.lb5)
        self.e5.grid(row=11, column=1, columnspan=2, sticky=EW, padx=5, pady=7)

        btn1 = ttk.Button(self, text="Registrati!", command= self.register_user)
        btn1.grid(row=13, column=1, padx=10, pady=10)

        btn2 = ttk.Button(self, text="Torna alla Home", command=lambda: view_controller.show_frame(LoginPage))
        btn2.grid(row=13, column=2, padx=10, pady=10)

        self.lb6 = Label(self, text="", bd=1, relief=SUNKEN)
        self.lb6.grid(row=14, column=1, columnspan=2, sticky=N + S + E + W)

    def register_user(self):

        """Questa funzione permette all'utente di registrarsi nel database, grazie alla funzione add_user fornita dallo
        UserManager. Se il login è corretto e non viene restituito niente, allora il login è andato a buon fine e viene
        aggiornato il file, mostrata la LoginPage dicendo all'utente che ora può autenticarsi, e vegono azzerati tutti
        i campi in caso l'utente voglia registrare un'altro account. Altrimenti, grazie alle stringhe fornite dalla
        funzione add_user, si comunica all'utente che cosa ha sbagliato."""

        status = self._view_controller.controller.add_user(self.cb1.get(), self.e1.get(), self.e2.get(), self.e3.get(),
                                                           self.e4.get().lower(), self.e5.get())
        if not status:
            self._view_controller.controller.update_file()
            self._view_controller.show_frame(LoginPage)
            self._view_controller.get_frame(LoginPage).lb3['text'] = "Registration Successful! You can now log-in"

            self.cb1.current(0)
            self.e1.delete(0, END)
            self.e1.insert(0, "Name")
            self.e2.delete(0, END)
            self.e2.insert(0, "Surname")
            self.e3.delete(0, END)
            self.e3.insert(0, "Password")
            self.e4.delete(0, END)
            self.e4.insert(0, "Email")
            self.e5.delete(0, END)
            self.e5.insert(0, "Birthdate")

        elif isinstance(status, Error):
            self.lb6['text'] = status.get_message()


class LoginSuccessPage(Frame):

    """Questa pagina fornisce all'utente la possibilità di entrare nella CourseApplication, oppure di aprire una
    finestra per modificare alcune delle sue impostazioni"""

    def __init__(self, view_controller, id):

        """L'init di questa classe istanzia eventuali oggetti di tkinter e ttk

        :param view_controller: Viene passata un'istanza della LoginApplication, in modo che la pagina possia interagire
        con la view dell'utente, cambiandola ad esempio con un pulsante, e per istanziare altre finestre
        :type view_controller: LoginApplication
        :param id: l'ID dell'utente, in modo da prendere alcuni dati da visualizzare, in questo caso nome e cognome
        :type id: str"""

        super().__init__(view_controller)
        self.configure(background="#26a65b")

        self._view_controller = view_controller
        self._user = view_controller.controller.get_userdata(id, name=True, surname=True)
        image_size = 120

        pil_image = Image.open("media/logo.jpg").resize((image_size, image_size))
        self.img = ImageTk.PhotoImage(pil_image)

        lbimg = ttk.Label(self, image=self.img)
        lbimg.grid(row=1, column=1, rowspan=3)

        label = ttk.Label(self, text="Welcome, {} {}".format(self._user["name"], self._user["surname"]),
                          font="LARGE_FONT")
        label.grid(row=1, column=2, columnspan=2, padx=10, pady=20)

        button1 = ttk.Button(self, text="Start learning!")
        button1.grid(row=2, column=2, padx=10, sticky=EW)

        self.btn3 = ttk.Button(self, text="Edit user settings", command=lambda: self.start_edit_page(id))
        self.btn3.grid(row=2, column=3, padx=10, sticky=EW)

    def start_edit_page(self, id):

        """Questa funzione permette di inizializzare la EditSettingsPage, disabilitando il pulsante per evitare che
        l'utente ne apra più di una"""

        self._view_controller.add_window(EditSettingsPage, self._view_controller, id)
        self.btn3.config(state="disabled")


class EditSettingsPage(Toplevel):

    """Questa pagina permette all'utente di modificare la propria email, password, e tipo di account"""

    def __init__(self, view_controller, id):

        """L'init di questa classe istanzia eventuali oggetti di tkinter e ttk

        :param view_controller: Viene passata un'istanza della LoginApplication, in modo che la pagina possia interagire
        con la view dell'utente, cambiandola ad esempio con un pulsante, e per istanziare altre finestre
        :type view_controller: LoginApplication
        :param id: l'ID dell'utente, in modo da prendere alcuni dati da visualizzare, in questo caso email, pass. e tipo
        :type id: str"""

        super().__init__(view_controller)
        self.configure(background="#8c14fc")
        self.resizable(False, False)

        self._view_controller = view_controller
        self.protocol("WM_DELETE_WINDOW", lambda: self.close())
        self.user = view_controller.controller.get_userdata(id, email=True, type=True)

        image_size = 120

        pil_image = Image.open("media/logo.jpg").resize((image_size, image_size))
        self.img = ImageTk.PhotoImage(pil_image)
        lbimg = ttk.Label(self, image=self.img, anchor="c")
        lbimg.grid(row=1, column=1, columnspan=3, sticky=EW)

        self.lb1 = ttk.Label(self, text="Type: {}".format(self.user["type"]))
        self.lb1.grid(row=2, column=1, padx=10, pady=10, sticky=W)

        self.cb1 = ttk.Combobox(self, state="readonly", values=("User Type", "Student", "Teacher"))
        self.cb1.current(0)
        self.cb1.grid(row=3, column=1, sticky=EW, padx=5, pady=7)
        self.cb1.grid_remove()

        btn2 = ttk.Button(self, text="Confirm", command=lambda: self.modify_user(id, type=self.cb1.get()))
        btn2.grid(row=3, column=2, padx=10, sticky=EW)
        btn2.grid_remove()

        btn1 = ShowButton(self, self.cb1, btn2, text="Change Type")
        btn1.grid(row=2, column=2, padx=10, sticky=EW)

        self.lb2 = ttk.Label(self, text="Email: {}".format(self.user["email"]))
        self.lb2.grid(row=4, column=1, padx=10, pady=10, sticky=W)

        self.e1 = FormEntry(self, "New Email")
        self.e1.grid(row=5, column=1, sticky=EW, padx=5, pady=7)
        self.e1.grid_remove()

        btn4 = ttk.Button(self, text="Confirm", command=lambda: self.modify_user(id, email=self.e1.get()))
        btn4.grid(row=5, column=2, padx=10, sticky=EW)
        btn4.grid_remove()

        btn3 = ShowButton(self, self.e1, btn4, text="Change Email")
        btn3.grid(row=4, column=2, padx=10, sticky=EW)

        self.lb3 = ttk.Label(self, text="Password: ***")
        self.lb3.grid(row=6, column=1, padx=10, pady=10, sticky=W)

        self.e2 = FormEntry(self, "Password", show="*")
        self.e2.grid(row=7, column=1, sticky=EW, padx=5, pady=7)
        self.e2.grid_remove()

        btn6 = ttk.Button(self, text="Confirm", command=lambda: self.modify_user(id, password=self.e2.get()))
        btn6.grid(row=7, column=2, padx=10, sticky=EW)
        btn6.grid_remove()

        btn5 = ShowButton(self, self.e2, btn6, text="Change Password")
        btn5.grid(row=6, column=2, padx=10, sticky=EW)

        self.lb4 = Label(self, text="", bd=1, relief=SUNKEN)
        self.lb4.grid(row=8, column=1, columnspan=2, sticky=N + S + E + W)

    def close(self):
        """Questa funzione, invocata quando si preme la x della pagina, riabilita il pulsante della LoginSuccessPage"""

        self._view_controller.get_frame(LoginSuccessPage).btn3.config(state=NORMAL)
        self.destroy()

    def modify_user(self, id, **kwargs):
        """Questa funzione permette di modificare i dati dell'utente, dato un id e i vari attributi da modificare. Esso
        utilizza il metodo modify_user del UserManager. Se la modifica va a buon fine, viene detto all'utente e vengono
        refreshati i label in modo che rispecchino i dati appena modificati dall'utente. Altrimenti, grazie alle
        stringhe fornite dal metodo modify_user, si vede cosa l'utente a sbagliato e lo si informa andando a modificare
        un label.

        :param id: L'ID dell'utente da modificare
        :type id: str
        :param kwargs: Gli attributi dell'utente da modificare, a cui viene associato un valore
        :type kwargs: dict"""

        status = self._view_controller.controller.modify_user(id, **kwargs)
        if not status:
            self.lb4['text'] = "Changes have been successfully applied"
            self.refresh_userdata(id)
        elif isinstance(status, Error):
            self.lb4['text'] = status.get_message()

    def refresh_userdata(self, id):
        """Questa funzione permette di refreshare i label, andando a riprendere i dati dal database. Questa funzione
        torna utile quando l'utente ha appena cambiato i propri dati, ed essa torna utile per visualizzarli.

        :param id: L'ID dell'utente, i cui dati verranno appropriatamente visualizzati nei label
        :type id: str"""

        self.user = self._view_controller.controller.get_userdata(id, email=True, type=True)
        self.lb1['text'] = "Type: {}".format(self.user["type"])
        self.lb2['text'] = "Email: {}".format(self.user["email"])


class FormEntry(ttk.Entry):

    """Questa classe, che eredita ttk.Entry permette di visualizzare un testo quando la entry viene lasciata vuota, in
    modo molto simile al placeholder in html. Inoltre, è possibile associare un label, nel quale poter scrivere ad
    esempio il formato dell'input da inserire nella entry."""

    def __init__(self, master=None, text="", tklabel=None, show="", **kwargs):

        """L'init di questa classe, oltre a creare le variabili di istanza necessarie, effettua anche il binding degli
        eventi FocusIn e FocusOut alle corrette funzioni, in modo che esse vengano eseguite automaticamente in base
        alle azioni dell'utente nel form.

        :param master: Dove inserire il widget
        :type master: Frame o Tk
        :param text: Il testo da mostrare quando il widget non è selezionato e vuoto
        :type text: str
        :param tklabel: Un'istanza di label, da mostrare quando la entry viene cliccata
        :type tklabel: tk.Label o ttk.Label
        :param show: Che cosa mostrare quando l'utente inserisce dati nel campo al posto dei normali caratteri. Mettendo
        un asterisco, ogni lettera inserita verrà mostrata come asterisco. Utile per le password.
        :type show: str
        :param kwargs: Eventuale dizionario da passare nell'init di Entry
        :type kwargs: dict"""

        ttk.Entry.__init__(self, master, **kwargs)
        self.text = text
        self.tklabel = tklabel
        self.show = show

        self.unselected()
        self.bind('<FocusIn>', self.selected)
        self.bind('<FocusOut>', self.unselected)

    def selected(self, event=None):

        """Questa funzione, eseguita quando viene cliccata la Entry, rimuove il testo presente nella entry se l'utente
        non ne ha inserito alcuno, effettua il configure con la show presa in input e inoltre mostra la label, se ne
        è stata associata una al label"""

        if self.get() == self.text:
            self.delete(0, END)
            self.configure(show=self.show)
        if isinstance(self.tklabel, ttk.Label):
            self.tklabel.grid()

    def unselected(self, event=None):

        """Questa funzione, eseguita quando viene deselezionata la entry, se la entry è vuota, inserisce il testo
        preso come parametro nell'init, riporta la show al suo stato normale, e nasconde la label, se ne è stata
        associata una al label"""

        if not self.get():
            self.insert(0, self.text)
            self.configure(show="")
        if isinstance(self.tklabel, ttk.Label):
            self.tklabel.grid_remove()


class ShowButton(ttk.Button):

    """Questa classe, che eredita il pulsante di ttk offre la possibilità di mostrare e nascondere un numero variabile
    di widget quando viene cliccato."""

    def __init__(self, master=None, *args, **kwargs):

        """L'init di questa funzione inizializza il pulsante, e imposta il booleano showing, necessario per capire se
        mostrare o no i widget la prossima volta che il pulsante viene cliccato

        :param master: Dove inserire il widget
        :type master: Frame o Tk
        :param args: le istanze dei widget Tkinter da associare al pulsante
        :type args: list
        :param kwargs: Eventuali opzioni da passare all'init del ttk.Button
        :type kwargs: dict"""

        ttk.Button.__init__(self, master, command=lambda: self.show_hide_widgets(args), **kwargs)
        self.showing = False
        self.show_hide_widgets(args)

    def show_hide_widgets(self, widgets):

        """Questa funzione mostra i widget se showing è True, altrimenti li nasconde. Infine, inverte lo stato di
        showing

        :param widgets: I widgets da mostrare/nascondere
        :type widgets: list"""

        if self.showing:
            for widget in widgets:
                widget.grid()
        else:
            for widget in widgets:
                widget.grid_remove()

        self.showing = not self.showing
