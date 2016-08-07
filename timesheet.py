"""
Simple timesheet tool to keep track of clients worked
on during the day.
"""
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from collections import defaultdict
import csv
import os
import json

CLIENTS = ("Boathouse Row I", "Boathouse Row II",
           "PMSMF", "PMSF", "PMSF(L)", "PMSF US LP", "Tewks",
           "CitcoOne", "Admin", "Training", "AOL", "NPIC")

# If 'tmp_save.json' exists, the system must have crashed on exit
# and not deleted the file. Restore the contents to get an up to date WORKLIST
try:
    with open('tmp_save.json', 'r') as fp:
        WORKLIST = json.load(fp)
        WORKLIST = defaultdict(float, WORKLIST)
except FileNotFoundError:
    WORKLIST = defaultdict(float)


class Timer:
    """
    Returns the elapsed time in seconds between
    2 datetime objects
    """
    timer_running = False

    def __init__(self):
        self.start = None
        self.stop = None

    def time_start(self):
        """Starts the timer"""
        self.start = datetime.now()
        self.timer_running = True

    def time_stop(self):
        """Stops the timer, resets the state time to zero"""
        self.stop = datetime.now()
        self.timer_running = False

    @property
    def elapsed_time(self):
        """Return the time between start and stop in seconds"""
        return (self.stop - self.start).seconds

    @property
    def split_time(self):
        """Return the between start and now in seconds. Does not stop the clock"""
        return (datetime.now() - self.start).seconds


class MyWindow(Tk, Timer):
    """
    Main Tkinter window. Probably. Don't really know much
    Tkinter yet.
    """

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.top_menu()
        self.c = ttk.Combobox(self, state=NORMAL)
        self.c['values'] = sorted(CLIENTS)
        self.c.bind('<<ComboboxSelected>>', self.client)
        self.b1 = Button(self, text="Start", command=self.time_start)
        self.b2 = Button(self, text="Stop", state=DISABLED, command=self.time_stop)
        self.c.grid(columnspan=2)
        self.b1.grid(sticky=W, row=1, column=0)
        self.b2.grid(sticky=E, row=1, column=1)
        self.config(menu=self.menubar)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def top_menu(self):
        self.menubar = Menu(self.parent)
        self.filemenu = Menu(self, tearoff=False)
        self.editbar = Menu(self, tearoff=False)
        self.menubar.add_cascade(label='File', menu=self.filemenu)
        self.filemenu.add_command(label='New Timesheet', command=self.write)
        self.filemenu.add_command(label='Save Timesheet', command=self.write)
        self.menubar.add_cascade(label='Edit', menu=self.editbar)
        self.editbar.add_command(label='Manual adjustment', command=self.manual_entry_window)
        self.editbar.add_command(label='Current timesheet', command=self.view_timesheet_window)

    def manual_entry_window(self):
        """Creates the child window for Manual Entries"""
        t = Toplevel(self, width=250, height=100)
        t.title = 'Change time'
        self.c1 = ttk.Combobox(t, state=NORMAL)
        self.c1['values'] = sorted(CLIENTS)
        self.c1.bind('<<ComboboxSelected>>', self.client_manual)
        self.my_label = Label(t, text="Enter time")
        self.my_entry = Entry(t, width=4)
        b3 = Button(t, text='Update', command=self.update_worklist_helper)
        b4 = Button(t, text='Close', command=t.destroy)
        self.c1.pack(side='top')
        self.my_label.pack(side='left')
        self.my_entry.pack(side='left')
        b3.pack(side='left')
        b4.pack(side='right')

    def view_timesheet_window(self):
        """Creates the child window for Current Timesheet"""
        w = Toplevel()
        box = Listbox(w)
        box.pack()
        temp_dict = self.get_current_timesheet()
        for key, val in temp_dict.items():
            entry = '{} {}'.format(key, val)
            box.insert(END, entry)
        # Include a total time at the bottom
        total = '{} {}'.format('Total Time', sum(temp_dict.values()))
        box.insert(END, total)

    def update_worklist_helper(self):
        """
        Wrapper to pass function update_worklist to tkinter command
        Tkinter won't allow parameters
        """
        time = None
        customer = None
        self.update_worklist(time, customer)

    def update_worklist(self, time, customer):
        """
        Update the WORKLIST with a manual entry
        """
        time = self.my_entry.get()
        customer = self.client_manual(self)
        try:
            float(time)
            WORKLIST[customer] += float(time)
        except ValueError:
            messagebox.showinfo(title="Warning", message="Please enter a number")

    def get_current_timesheet(self):
        """
        If a Timer is running, returns an up-to-date WORKLIST
        If there is no current Timer running, returns the WORKLIST
        """
        if self.timer_running:
            temp_workist = WORKLIST.copy()
            temp_client = self.client(self)
            temp_time = round(self.split_time / 3600, 1)
            temp_workist[temp_client] += temp_time
            return temp_workist
        return WORKLIST

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
        """Returns the value from Combobox"""
        return self.c.get()

    def client_manual(self, args):
        """Returns the value from Manual Entry Combobox"""
        return self.c1.get()

    def write(self):
        """Save the contents of WORKLIST to a new or existing file"""
        is_new_file = False
        # If a Timer is running, don't allow a save
        if self.timer_running:
            return messagebox.showwarning("Save Error", "You have a timer running. Please stop the timer to proceed")
        file_path = str(filedialog.asksaveasfilename(defaultextension='.csv', initialdir=os.getcwd()))
        """
        Format explainer:
        %A = Weekday full name
        %d = Day with padded zero eg (01,02,...,30,31)
        %B = Month full name
        """
        day = datetime.now().strftime("%A %d %B")
        if file_path:
            if not os.path.isfile(file_path):
                is_new_file = True
            with open(file_path, 'a', newline='') as csvfile:
                writer = csv.writer(csvfile, delimiter=",")
                if is_new_file:
                    writer.writerow(["Day", "Client", "Time"])
                for key, val in WORKLIST.items():
                    writer.writerow([day, key, val])
            WORKLIST.clear()

    def on_close(self):
        """Ensure that WORKLIST is empty i.e. all data has been saved"""
        if WORKLIST:
            if messagebox.askokcancel("Exit?", "You have not saved. Do you want to exit"):
                self.destroy()
        else:
            self.destroy()


def main():
    app = MyWindow(None)
    app.title("Time Manager")
    app.grid()
    app.mainloop()


main()
#TODO Current timesheet window: Rounding & Expandable