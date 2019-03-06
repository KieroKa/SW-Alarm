from tkinter import *
from tkinter import messagebox
import tkinter as tk
import asyncio
import threading
import sqlite3

koniec = 0
tryb = 1
rozpoczeto = False

root = Tk()
var = StringVar()
var.set('Program systemu alarmowego\n Żeby włączyć alarm kliknij na przycisk "Włącz alarm"')

uzytkownicy = {
    20: "Kinga",
    66: "Robert"
}

class Page(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
    def show(self):
        self.lift()

class Page1(Page):
   def __init__(self, *args, **kwargs):
       global var
       Page.__init__(self, *args, **kwargs)
       label = tk.Label(self, textvariable = var)
       label.pack()
       label.pack(side="top", fill="both", expand=True)

class MainView(tk.Frame):
    def __init__(self, *args, **kwargs):
        tk.Frame.__init__(self, *args, **kwargs)
        p1 = Page1(self)

        buttonframe = tk.Frame(self)
        container = tk.Frame(self)
        buttonframe.pack(side="top", fill="x", expand=False)
        container.pack(side="top", fill="both", expand=True)

        p1.place(in_=container, x=0, y=0, relwidth=1, relheight=1)

        b1 = tk.Button(buttonframe, text='Włącz alarm', command=lambda: [p1.lift,do_tasks(async_loop)])
        b2 = tk.Button(buttonframe, text="Baza danych logowań", command=self.gotorecords)
        b3 = tk.Button(buttonframe, text="Baza danych czujnika", command=self.gotorecords1)

        b1.pack(side="left")
        b2.pack(side="left")
        b3.pack(side="left")

        p1.show()

    def gotorecords(self):
        root2=Toplevel(self.master)
        mygui=Records(root2)

    def gotorecords1(self):
        root2=Toplevel(self.master)
        mygui=Records1(root2)

class Records:
    def __init__(self, master):
        self.master = master
        self.master.geometry('200x200+100+200')
        self.master.title('Wyniki')
        self.connection = sqlite3.connect('Alarm')
        self.cur = self.connection.cursor()
        self.intLabel = Label(self.master, text="Osoba", width=10)
        self.intLabel.grid(row=0, column=1)
        self.textLabel1 = Label(self.master, text="Data", width=10)
        self.textLabel1.grid(row=0, column=2)
        self.showallrecords()

    def showallrecords(self):
        Data = self.readfromdatabase()
        for index, dat in enumerate(Data):
            Label(self.master, text=dat[1]).grid(row=index+1, column=1)
            Label(self.master, text=dat[2]).grid(row=index + 1, column=2)

    def readfromdatabase(self):
        self.cur.execute("SELECT * FROM 'log'")
        return self.cur.fetchall()

class Records1:
    def __init__(self, master):
        self.master = master
        self.master.geometry('200x200+100+200')
        self.master.title('Wyniki')
        self.connection = sqlite3.connect('Alarm')
        self.cur = self.connection.cursor()
        self.textLabel1 = Label(self.master, text="Data wykrycia ruchu", width=15)
        self.textLabel1.grid(row=0)
        self.showallrecords()

    def showallrecords(self):
        Data = self.readfromdatabase()
        for index, dat in enumerate(Data):
            Label(self.master, text=dat[1]).grid(row=index+1)

    def readfromdatabase(self):
        self.cur.execute("SELECT * FROM 'CZUJNIK'")
        return self.cur.fetchall()

def _asyncio_thread(async_loop):
    global koniec
    global rozpoczeto
    if rozpoczeto == False:
        koniec = 0
        async_loop.run_until_complete(do_urls())


def do_tasks(async_loop):
    threading.Thread(target=_asyncio_thread, args=(async_loop,)).start()

async def do_urls():
    global koniec
    global tryb
    global rozpoczeto
    global var
    global root
    con = sqlite3.connect('Alarm')
    cur = con.cursor()
    print("Wysłano do arduino: a")
    var.set('Alarm działa')
    root.update_idletasks()
    rozpoczeto = True
    while koniec != 1:
        if tryb == 1:
            tryb = int(input("Co zrobic?"))  # ser.read()
        if tryb == 2:  # Ruch Wykryty
            var.set('Wykryto ruch')
            root.update_idletasks()
            cur.execute('''INSERT INTO czujnik DEFAULT VALUES''')
            con.commit()
            tryb = 1
        if tryb == 3:  # Przycisk Reset
            var.set('Reset manualny')
            root.update_idletasks()
            l1 = messagebox.askokcancel("Uwaga!", "Kontynuować alarm?")
            if(l1==1):
                var.set('Alarm działa')
                root.update_idletasks()
                print("Wysłano do arduino: a")
            else:
                koniec = 1
                print("Wysłano do arduino: b")
                var.set('Alarm zakończono\n Dziekujemy za skorzystanie z programu.')
                root.update_idletasks()
            tryb = 1
        if tryb == 4:  # Znaleziono Karte
            karta = int(input("Numer karty?"))
            if karta in uzytkownicy:
                user = uzytkownicy[karta]
                cur.execute('''INSERT INTO log(nazwa)
                                              VALUES(?)''', (user,))
                con.commit()
                var.set('Karta poprawna. Witaj ' + user)
                root.update_idletasks()
                l1 = messagebox.askokcancel("Uwaga!", "Kontynuować alarm?")
                if(l1==True):
                    print("Wysłano do arduino: a")
                    var.set('Alarm działa')
                    root.update_idletasks()
                else:
                    koniec = 1
                    print("Wysłano do arduino: b")
                    var.set('Alarm zakończono\n Dziekujemy za skorzystanie z programu.')
                    root.update_idletasks()
                tryb = 1
            else:
                print("Wysłano do arduino: b")
                var.set('Karta niepoprawna. Sprawdź czy przyłożyłeś dobrą kartę.')
                root.update_idletasks()
                cur.execute('''INSERT INTO log(nazwa)
                                                          VALUES(?)''', (str(karta),))
                con.commit()
                tryb = 1

        if tryb == 5:  # Brak Karty
            print("Wysłano do arduino: b")
            var.set('Alarm')
            root.update_idletasks()
            tryb = 1
        if tryb == 6:  # Niezdefiniowany Blad
            print("Wysłano do arduino: b")
            var.set('Nastapil niezdefiniowany blad. Prosze zresetowac uklad.')
            root.update_idletasks()
            koniec = 1
            tryb = 1
    rozpoczeto = False
    con.close()

def main(async_loop):
    global root
    main = MainView(root)
    main.pack(side="top", fill="both", expand=True)
    root.wm_geometry("320x100")
    root.title("Alarm")
    root.mainloop()

if __name__ == '__main__':
    async_loop = asyncio.get_event_loop()
    main(async_loop)