import tkinter as tk
from tkinter import Menu


# file-like object
class StdoutRedirector:
    def __init__(self, textbox):
        self.textbox = textbox

    def write(self, text):
        # enable textbox before writing
        self.textbox.config(state='normal')
        # write to textbox
        self.textbox.insert(tk.END, text)
        # autoscroll to end of textbox
        self.textbox.see('end')
        # disable textbox after writing
        self.textbox.config(state='disabled')

    # needed for file-like objects
    def flush(self):
        pass


class DTEntry(tk.Entry):
    def __init__(self, master=None, default_text='default', **kwargs):
        # create instance of tk.Entry
        tk.Entry.__init__(self, master, **kwargs)
        # set default text
        self.default_text = default_text
        # execute focus_out() by default because there's
        # no focus on any widget when the program is launched
        self.focus_out()
        # set FocusIn behavior
        self.bind('<FocusIn>', self.focus_in)
        # set FocusOut behavior
        self.bind('<FocusOut>', self.focus_out)

    def focus_in(self, event=None):
        # if text field contains the default text
        if self.get() == self.default_text:
            # delete default text
            self.delete(0, tk.END)
            # set text color to black
            self.config(fg='black')

    def focus_out(self, event=None):
        # if text field is empty
        if self.get() == '':
            # set text color to grey
            self.config(fg='grey')
            # insert default text
            self.insert(0, self.default_text)


class ContextMenu:
    def __init__(self, widgets, master=None, tearoff=False):
        # create context menu
        self.menu = Menu(master, tearoff=tearoff)

        # add commands
        self.menu.add_command(label="Cut")
        self.menu.add_command(label="Copy")
        self.menu.add_command(label="Paste")

        # bind right click to show() method
        for widget in widgets:
            widget.bind("<Button-3><ButtonRelease-3>", self.show)

    def show(self, event):
        # master becomes the widget that triggered the event
        master = event.widget

        # add functionality to commands
        self.menu.entryconfigure("Cut", command=lambda: master.event_generate("<<Cut>>"))
        self.menu.entryconfigure("Copy", command=lambda: master.event_generate("<<Copy>>"))
        self.menu.entryconfigure("Paste", command=lambda: master.event_generate("<<Paste>>"))

        # draw context menu on screen
        self.menu.tk_popup(event.x_root, event.y_root)
