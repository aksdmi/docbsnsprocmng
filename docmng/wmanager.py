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

    
    rel_width = 0.24
    rel_height = 0.1
    img_width = 35.0
    label_font = ("Arial", 14)
    h_m_font = ('Arial', 12)
    h_m_rel_width = 0.2
    h_m_rel_height = 0.04

    img1 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/text-file.png', width=int(img_width))

    

    # a = Label(window ,text = "First Name", image=img, width=100, height=5, font=("Arial", 14)).grid(row = 0,column = 0)
    # a = Label(window, image=img, width=int(img_width))
    # # a.grid(row = 0,column = 0)
    # a.place(relx=0.0, rely=0.0, width=img_width, relheight=rel_height)

    frm = Frame(window, name='left_frame', background="grey")
    frm.place(relx=0.0, rely=0.0, relwidth=rel_width, relheight=1.0)


    aa = Button(frm, text="Documents", image=img1, compound=LEFT, borderwidth=2, relief="raised", font=label_font)
    aa.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=rel_height)

    bb = Button(frm ,text = "Settings", borderwidth=2, relief="raised", font=label_font)
    # .grid(row = 1,column = 0)
    bb.place(relx=0.0, rely=rel_height, relwidth=1.0, relheight=rel_height)
    
    cc = Button(frm ,text = "About", borderwidth=2, relief="raised", font=label_font)
    # .grid(row = 2,column = 0)
    cc.place(relx=0.0, rely=(rel_height+rel_height), relwidth=1.0, relheight=rel_height)

    dd = Label(frm)
    dd.place(relx=0.0, rely=3.0*rel_height, relwidth=1.0, relheight=(1.0 - 3.0*rel_height))

    # document list menu

    frm_doc_header = Frame(window, name='right_frame_header', background="blue")
    frm_doc_header.place(relx=rel_width, rely=0.0, relwidth=(1.0 - rel_width), relheight=h_m_rel_height)

    img2 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/add.png')

    mn_button = Button(frm_doc_header, name='list_add', text = "add", image=img2, compound=LEFT, borderwidth=1, relief='groove', font=h_m_font)
    mn_button.place(relx=0.0, rely=0.0, relwidth=h_m_rel_width, relheight=1.0)

    img3 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/edit.png')
    mn_button = Button(frm_doc_header, name='list_edit', text = "edit", image=img3, compound=LEFT, borderwidth=1, relief='groove', font=h_m_font)
    mn_button.place(relx=h_m_rel_width, rely=0.0, relwidth=h_m_rel_width, relheight=1.0)

    img4 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/delete.png')
    mn_button = Button(frm_doc_header, name='list_remove', text = "remove", image=img4, compound=LEFT, borderwidth=1, relief='groove', font=h_m_font)
    mn_button.place(relx=(h_m_rel_width + h_m_rel_width), rely=0.0, relwidth=h_m_rel_width, relheight=1.0)

    mn_label = Label(frm_doc_header)
    mn_label.place(relx=(3.0 * h_m_rel_width), rely=0.0, relwidth=(1.0 - 3.0 * h_m_rel_width), relheight=1.0)

    # document list

    mn_list = ttk.Treeview(window)
    

    mn_list['columns'] = ('player_id', 'player_name', 'player_Rank', 'player_states', 'player_city')

    mn_list.column("#0", width=0,  stretch=NO)
    mn_list.column("player_id",anchor=CENTER, width=80)
    mn_list.column("player_name",anchor=CENTER,width=80)
    mn_list.column("player_Rank",anchor=CENTER,width=80)
    mn_list.column("player_states",anchor=CENTER,width=80)
    mn_list.column("player_city",anchor=CENTER,width=80)

    mn_list.heading("#0",text="",anchor=CENTER)
    mn_list.heading("player_id",text="Id",anchor=CENTER)
    mn_list.heading("player_name",text="Name",anchor=CENTER)
    mn_list.heading("player_Rank",text="Rank",anchor=CENTER)
    mn_list.heading("player_states",text="States",anchor=CENTER)
    mn_list.heading("player_city",text="States",anchor=CENTER)

    mn_list.insert(parent='',index='end',iid=0,text='',
    values=('1','Ninja','101','Oklahoma', 'Moore'))
    mn_list.insert(parent='',index='end',iid=1,text='',
    values=('2','Ranger','102','Wisconsin', 'Green Bay'))
    mn_list.insert(parent='',index='end',iid=2,text='',
    values=('3','Deamon','103', 'California', 'Placentia'))
    mn_list.insert(parent='',index='end',iid=3,text='',
    values=('4','Dragon','104','New York' , 'White Plains'))
    mn_list.insert(parent='',index='end',iid=4,text='',
    values=('5','CrissCross','105','California', 'San Diego'))
    mn_list.insert(parent='',index='end',iid=5,text='',
    values=('6','ZaqueriBlack','106','Wisconsin' , 'TONY'))

    mn_list.place(relx=rel_width, rely=h_m_rel_height, relwidth=(1.0 - rel_width), relheight=(1.0 - h_m_rel_height))

    # window.attributes('-fullscreen', True)
    tracker = Tracker(window)
    tracker.bind_config()

    window.mainloop()

    