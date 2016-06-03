"""
Simple timesheet tool to keep track of clients worked
on during the day.
"""
from tkinter import *
from tkinter import ttk, filedialog
from datetime import datetime
from collections import defaultdict
import csv
import os

CLIENTS = ("Boathouse Row I", "Boathouse Row II",
           "PMSMF", "PMSF", "PMSF(L)", "PMSF US LP", "Tewks",
           "CitcoOne", "Admin", "Training", "AOL", "NPIC")
WORKLIST = defaultdict(float)


class Timer:
    """
    Calcuates the elapsed time in increments of 0.1 hours
    between 2 datetime objects
    """

    def __init__(self):
        self.start = None
        self.elapsed_time = None

    def time_start(self):
        """Starts the timer"""
        self.start = datetime.now()

    def time_stop(self):
        """Stops the timer"""
        self.elapsed_time = (datetime.now() - self.start).seconds
        self.start = None


class MyWindow(Frame, Timer):
    """
    Main Tkinter window. Probably. Don't really know much
    Tkinter yet.
    """

    def __init__(self, master):
        Frame.__init__(self, master)
        self.menubar = Menu(self)
        self.filemenu = Menu(self, tearoff=False)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label='New Timesheet', command=self.write)
        self.filemenu.add_command(label='Update Timesheet', command=self.append)
        self.b1 = Button(self, text="Start", command=self.time_start)
        self.b2 = Button(self, text="Stop", state=DISABLED, command=self.time_stop)
        self.c = ttk.Combobox(self, state=NORMAL)
        self.c['values'] = sorted(CLIENTS)
        self.c.bind('<<ComboboxSelected>>', self.client)
        self.c.grid(columnspan=2)
        self.b1.grid(sticky=W, row=1, column=0)
        self.b2.grid(sticky=E, row=1, column=1)
        master.configure(menu=self.menubar)

    def time_start(self):
        """
        Starts the timer.
        Disables to the Start button to prevent resetting the clock
        Disables the Combobox to prevent changing the client
        Enables to Stop button
        """
        super().time_start()
        self.b1.config(state=DISABLED)
        self.c.config(state=DISABLED)
        self.b2.config(state=NORMAL)

    def time_stop(self):
        """
        Stops the timer.
        Enables the Combobox to allow the next choice
        Enables the Start button
        Disables the Stop button
        """
        super().time_stop()
        self.c.config(state=NORMAL)
        self.b1.config(state=NORMAL)
        self.b2.config(state=DISABLED)
        WORKLIST[self.client(self)] += round(self.elapsed_time / 3600, 1)

    def client(self, args):
        return self.c.get()

    @staticmethod
    def write():
        open_file = str(filedialog.asksaveasfilename(defaultextension='.csv', initialdir=os.getcwd()))
        if open_file:
            day = datetime.now().strftime("%A %d %B")
            with open(open_file, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=",")
                for key, val in WORKLIST.items():
                    writer.writerow([day, key, val])

    @staticmethod
    def append():
        open_file = str(filedialog.askopenfilename(defaultextension='.csv', initialdir=os.getcwd()))
        if open_file:
            day = datetime.now().strftime("%A %d %B")
            with open(open_file, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=",")
                for key, val in WORKLIST.items():
                    writer.writerow([day, key, val])


def main():
    top = Tk()
    top.title("Time Manager")
    top = MyWindow(top)
    top.grid()
    top.mainloop()


main()
