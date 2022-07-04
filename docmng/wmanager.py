#!/usr/bin/python3

import sys
from operator import concat
import screeninfo
from tkinter import *
from tkinter import ttk
from tkcalendar import *
import psycopg2
from contextlib import closing
from datetime import datetime
import uuid

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

def get_all_children_list(node, result, flt=''):
    '''recursively get widgets with name by filter
       and get their columns name in DB'''
    
    for key, value in node.children.items():
        if flt == '':
            result.append((f'_{value._name}', value))
        elif key.find(flt) > -1:
            result.append((f'_{value._name[:(len(value._name) - len(flt))]}', value))

        get_all_children_list(value, result, flt)


def to_type(value, type_name):
    if type_name == 'str':
        return value

    if type_name == 'int':
        return int(value)
    elif type_name == 'float':
        return float(value)
    elif type_name == 'datetime':
        return datetime.strptime(value, '%d.%m.%Y')
    elif type_name == 'binary':
        return value.encode('ISO-8859-1')
    else:
        return value


def get_all_input_values(node, result, flt=''):
    '''recursively get columns name in DB
       and their input values'''
    
    for key, value in node.children.items():
        cur_name = ''
        
        if flt == '':
            cur_name = f'_{key}'
            val_type = 'str'   
        elif key.find(flt) > -1:
            chpos = key.rfind('_')
            val_name, val_type = key[:chpos], key[(chpos + 1):]
            cur_name = f'_{val_name[:(len(val_name) - len(flt))]}'

        if cur_name:
            if isinstance(value, Text):
                cur_val = value.get('1.0', END)
            else:
                cur_val = value.get()
            
            cur_val = to_type(cur_val, val_type)

            result[0].append(cur_name)
            result[1].append(cur_val)

        get_all_input_values(value, result, flt)        


def write_close_document(cur_window):
    write_document(cur_window)
    cur_window.destroy()

def write_document(cur_window):

    child_list = [[], []]
    get_all_input_values(cur_window, child_list, 'entry')
    get_all_input_values(cur_window, child_list, 'text')

    if not child_list[0]:
        return

    # first entry must be always idrref!!!
    is_new = False
    if not child_list[1][0]:
        # child_list[0].append('_idrref')
        child_list[1][0] = uuid.uuid4().bytes
        is_new = True
        

    # exec_str = 'INSERT INTO documents({:s}) VALUES'.format(([el[0] for el in child_list]).join(','))
    
    exec_str = ('''INSERT INTO
                documents('''
                + ','.join(child_list[0]) + ')' +
                ''' VALUES('''
                + ','.join(['%s' for x in child_list[0]]) + ')')

    with closing(psycopg2.connect(dbname='main', user='postgres', 
                        password='postgres', host='localhost', port=54322)) as conn:

        with closing(conn.cursor()) as cursor:


            try:
                cursor.execute(exec_str, child_list[1])
            
                conn.commit()

                if is_new:
                    cur_window.nametowidget('idrrefentry_binary').insert(0, child_list[1][0].decode('ISO-8859-1'))
            except:
                print(sys.exc_info())
                raise Exception('Can\'t write document to DB')

def create_document_widgets(cur_window):
    cur_window.geometry("1080x720")
    cur_window.title("New document")
    
    rel_lbl_width = 0.4
    rel_ent_width = 0.6
    rel_btn_width = 0.15
    
    com_menu_rel_height = 0.05
    cur_rel_height = 0.05

    main_font = ("Arial", 14)
    mn_btn_font = ('Times', 12)    
    
    # hidden elements
    cur_el = Entry(cur_window, name='idrrefentry_binary', font=main_font)

    # command menu
    com_menu_frm = Frame(cur_window, name='com_menu')
    com_menu_frm.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=com_menu_rel_height)

    mn_doc_button = Button(com_menu_frm,
                        command=lambda: write_close_document(cur_window),
                        name='doc_write_close',
                        text = "Write and close",
                        bg='yellow',
                        borderwidth=2,
                        relief='raised',
                        font=mn_btn_font)

    
    mn_doc_button.place(relx=0.0, rely=0.0, relwidth=rel_btn_width, relheight=1.0)

    mn_doc_button2 = Button(com_menu_frm,
                        command=lambda: write_document(cur_window),
                        name='doc_write',
                        image=img5,
                        borderwidth=2,
                        relief='raised')

    
    mn_doc_button2.place(relx=rel_btn_width, rely=0.0, relwidth=rel_btn_width, relheight=1.0)


    # left group
    frm1 = Frame(cur_window, name='left_group')
    frm1.place(relx=0.0, rely=com_menu_rel_height, relwidth=0.5, relheight=1.0)

    cur_lbl = Label(frm1, name='codelabel', text = "Code", font=main_font)
    cur_lbl.place(relx=0.0, rely=0.0, relwidth=rel_lbl_width, relheight=cur_rel_height)

    cur_lbl = Entry(frm1, name='codeentry_str', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=0.0, relwidth=rel_ent_width, relheight=cur_rel_height)
    cur_lbl.insert(0, 'DCODE-00000001')

    cur_lbl = Label(frm1, name='descriptionlabel', text = "Description", font=main_font)
    cur_lbl.place(relx=0.0, rely=cur_rel_height, relwidth=rel_lbl_width, relheight=cur_rel_height)

    cur_lbl = Entry(frm1, name='descriptionentry_str', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=cur_rel_height, relwidth=rel_ent_width, relheight=cur_rel_height)
    cur_lbl.insert(0, 'Document creation test')
    
    cur_lbl = Label(frm1, name='contentlabel', text = "Content", font=main_font)
    cur_lbl.place(relx=0.0, rely=(cur_rel_height + cur_rel_height), relwidth=1.0, relheight=cur_rel_height)

    cur_lbl = Text(frm1, name='contenttext_str', font=main_font, borderwidth=1, relief='groove')
    cur_lbl.place(relx=0.0, rely=(3.0*cur_rel_height), relwidth=1.0, relheight=(1.0 - 3.0*cur_rel_height))
    cur_lbl.insert(1.0, 'This is a TEST document')

    #right group
    frm2 = Frame(cur_window, name='right_group')
    frm2.place(relx=0.5, rely=com_menu_rel_height, relwidth=0.5, relheight=1.0)

    cur_lbl = Label(frm2, name='create_datelabel', text = "Create date", font=main_font)
    cur_lbl.place(relx=0.0, rely=0.0, relwidth=rel_lbl_width, relheight=cur_rel_height)

    cur_lbl = Entry(frm2, name='create_dateentry_datetime', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=0.0, relwidth=rel_ent_width, relheight=cur_rel_height)
    cur_lbl.insert(0, '04.07.2022')

    cur_lbl = Label(frm2, name='sumlabel', text = "Sum", font=main_font)
    cur_lbl.place(relx=0.0, rely=cur_rel_height, relwidth=rel_lbl_width, relheight=cur_rel_height)
    

    cur_lbl = Entry(frm2, name='sumentry_float', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=cur_rel_height, relwidth=rel_ent_width, relheight=cur_rel_height)
    cur_lbl.insert(0, '117574.05')
    

    


def open_document(main_window, mn_list, idrref=None):
    cur_window = Toplevel(main_window)
    
    create_document_widgets(cur_window)

    cur_window.focus()
    cur_window.grab_set()    

    if idrref == None:
        print('New doc')
    else:
        print('Read from DB')


if __name__ == '__main__':


    mntrs = screeninfo.get_monitors()
    mntrs_p = [x for x in mntrs if x.is_primary]

    if not mntrs_p:
        mntrs_p = [mntrs[0]]


    window = Tk()
    window.title("Document management")
    # window.geometry('800x600')
    window.geometry(f'{mntrs_p[0].width}x{mntrs_p[0].height}')

    window.configure(background = "grey");

    
    rel_width = 0.18
    rel_height = 0.1
    img_width = 35.0
    label_font = ("Arial", 14)
    h_m_font = ('Arial', 12)
    h_m_rel_width = 0.2
    h_m_rel_height = 0.04

    img1 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/text-file.png', width=int(img_width))

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


    mn_list = ttk.Treeview(window)

    # document list menu

    frm_doc_header = Frame(window, name='right_frame_header', background="blue")
    frm_doc_header.place(relx=rel_width, rely=0.0, relwidth=(1.0 - rel_width), relheight=h_m_rel_height)

    img2 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/add.png')

    mn_button = Button(frm_doc_header,
                        command=lambda: open_document(window,  mn_list),
                        name='list_add',
                        text = "add",
                        image=img2,
                        compound=LEFT,
                        borderwidth=1,
                        relief='groove',
                        font=h_m_font)

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

    
    


    mn_list['columns'] = ('_idrref'
                          ,'_code'
                          ,'_description'
                          ,'_create_date'
                          ,'_sum')

    # mn_list.winfo_width();

     # for itm in mn_list['columns']:
    #     mn_list.column(itm, anchor=CENTER, width=80)

    mn_list.column("#0", width=0,  stretch=NO)
    mn_list.column("_idrref",anchor=CENTER, width=0, stretch=False, minwidth=0)
    mn_list.column("_code",anchor=CENTER,width=80)
    mn_list.column("_description",anchor=CENTER,width=80)
    mn_list.column("_create_date",anchor=CENTER,width=80)
    mn_list.column("_sum",anchor=CENTER,width=80)

    # mn_list.heading("#0",text="",anchor=CENTER)
    # mn_list.heading("_idrref",text="Id",anchor=CENTER)
    mn_list.heading("_code",text="code",anchor=CENTER)
    mn_list.heading("_description",text="description",anchor=CENTER)
    mn_list.heading("_create_date",text="create date",anchor=CENTER)
    mn_list.heading("_sum",text="sum",anchor=CENTER)

    #############################################################

    # connect to psql 

    iid = 0
    with closing(psycopg2.connect(dbname='main', user='postgres', 
                        password='postgres', host='localhost', port=54322)) as conn:

        with closing(conn.cursor()) as cursor:


            cursor.execute('''SELECT
                                    _idrref
                                    ,_code
                                    ,_description
                                    ,_create_date
                                    ,_sum
                            FROM
                                    documents LIMIT 100''')

            for row in cursor:
                mn_list.insert(parent='',index='end',iid=iid,
                    values=row)
                iid += 1    



    #############################################################

    # mn_list.insert(parent='',index='end',iid=0,text='',
    #     values=('1','Ninja','101','Oklahoma', 'Moore'))
    # mn_list.insert(parent='',index='end',iid=1,text='',
    #     values=('2','Ranger','102','Wisconsin', 'Green Bay'))
    # mn_list.insert(parent='',index='end',iid=2,text='',
    #     values=('3','Deamon','103', 'California', 'Placentia'))
    # mn_list.insert(parent='',index='end',iid=3,text='',
    #     values=('4','Dragon','104','New York' , 'White Plains'))
    # mn_list.insert(parent='',index='end',iid=4,text='',
    #     values=('5','CrissCross','105','California', 'San Diego'))
    # mn_list.insert(parent='',index='end',iid=5,text='',
    #     values=('6','ZaqueriBlack','106','Wisconsin' , 'TONY'))

    mn_list.place(relx=rel_width, rely=h_m_rel_height, relwidth=(1.0 - rel_width), relheight=(1.0 - h_m_rel_height))

    # window.attributes('-fullscreen', True)
    tracker = Tracker(window)
    tracker.bind_config()

    img5 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/save-icon.png')

    window.mainloop()

    