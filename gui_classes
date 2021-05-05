import tkinter as tk


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
