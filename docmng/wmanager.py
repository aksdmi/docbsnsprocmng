#!/usr/bin/python3

from cmath import sqrt
from tkinter import *
from tkinter import ttk
from tkinter import font

class Tracker:
    """ Toplevel windows resize event tracker. """

    def __init__(self, toplevel):
        self.toplevel = toplevel
        self.width, self.height = toplevel.winfo_width(), toplevel.winfo_height()
        self._func_id = None

    def bind_config(self):
        self._func_id = self.toplevel.bind("<Configure>", self.resize)

    def unbind_config(self):  # Untested.
        if self._func_id:
            self.toplevel.unbind("<Configure>", self._func_id)
            self._func_id = None

    def resize(self, event):
        if(event.widget == self.toplevel and
           (self.width != event.width or self.height != event.height)):
                # print(f'{event.widget=}: {event.height=}, {event.width=}\n')
                
                if self.width != 1:
                    new_font = int(event.width*event.height*14/960000)
                    for itm in self.toplevel.children['left_frame'].children.values():

                        itm.config(font=("Arial", new_font))
                
                self.width, self.height = event.width, event.height

if __name__ == '__main__':

    window = Tk()
    window.title("Document management")
    window.geometry('800x600')
    window.configure(background = "grey");

    # window.bind("<Configure>", func=resize)

    rel_width = 0.24
    rel_height = 0.15
    img_width = 35.0
    label_font = ("Arial", 14)

    img = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/text-file.png', width=int(img_width))

    

    # a = Label(window ,text = "First Name", image=img, width=100, height=5, font=("Arial", 14)).grid(row = 0,column = 0)
    # a = Label(window, image=img, width=int(img_width))
    # # a.grid(row = 0,column = 0)
    # a.place(relx=0.0, rely=0.0, width=img_width, relheight=rel_height)

    frm = Frame(window, name='left_frame', background="grey")
    frm.place(relx=0.0, rely=0.0, relwidth=rel_width, relheight=1.0)


    aa = Button(frm, text="First Name", image=img, compound=LEFT, borderwidth=2, relief="raised", font=label_font)
    aa.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=rel_height)

    bb = Button(frm ,text = "Last Name", borderwidth=2, relief="raised", font=label_font)
    # .grid(row = 1,column = 0)
    bb.place(relx=0.0, rely=rel_height, relwidth=1.0, relheight=rel_height)
   
    cc = Button(frm ,text = "Email", borderwidth=2, relief="raised", font=label_font)
    # .grid(row = 2,column = 0)
    cc.place(relx=0.0, rely=(rel_height+rel_height), relwidth=1.0, relheight=rel_height)

    dd = Label(frm)
    dd.place(relx=0.0, rely=3.0*rel_height, relwidth=1.0, relheight=(1.0 - 3.0*rel_height))

    # d = Label(window ,text = "Contact Number").grid(row = 3,column = 0)
    # a1 = Entry(window).grid(row = 0,column = 1)
    # b1 = Entry(window).grid(row = 1,column = 1)
    # c1 = Entry(window).grid(row = 2,column = 1)
    # d1 = Entry(window).grid(row = 3,column = 1)




    # btn = ttk.Button(window ,text="Submit").grid(row=4,column=0)

    # window.attributes('-fullscreen', True)
    tracker = Tracker(window)
    tracker.bind_config()

    window.mainloop()

    