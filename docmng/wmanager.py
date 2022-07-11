#!/usr/bin/python3

from cgitb import text
from curses import window
from tkinter import font
import screeninfo
from tkinter import *
from tkinter import ttk
import psycopg2, psycopg2.extras
from contextlib import closing
from datetime import datetime
import uuid
import sys
import json

from producer import publish


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

def get_all_input_widgets(node, result_dict):
    '''recursively get input widgets'''
    for key, value in node.children.items():
        
        if key.startswith('_'):
            result_dict[key] = value
            
        get_all_input_widgets(value, result_dict)
    
def get_all_input_values(node, result, flt=''):
    '''recursively get input fields names
       and their input values'''
    
    for key, value in node.children.items():
        cur_name = ''
        
        if flt == '':
            cur_name = key
            val_type = 'str'   
        elif key.startswith(flt):
            chpos = key.rfind('_')
            cur_name, val_type = key[:chpos], key[(chpos + 1):]
            # cur_name = f'{val_name[:(len(val_name) - len(flt))]}'

        if cur_name:
            if isinstance(value, Text):
                cur_val = value.get('1.0', END)
            else:
                cur_val = value.get()
            
            result[0].append(cur_name)
            result[1].append(to_type(cur_val, val_type))
            

        get_all_input_values(value, result, flt)        

def write_close_document(cur_window):
    write_document(cur_window)
    cur_window.destroy()

def write_document(cur_window):

    child_list = [[], []]
    get_all_input_values(cur_window, child_list, '_')
    
    if not child_list[0]:
        return

    # first entry must be always idrref!!!
    is_new = False
    if not child_list[1][0]:
        child_list[1][0] = uuid.uuid4().bytes
        is_new = True
        
    
    query_pack = []
    if is_new:
        exec_str = ('''INSERT INTO
                    documents('''
                    + ','.join(child_list[0]) + ')' +
                    ''' VALUES('''
                    + ','.join(['%s' for x in child_list[0]]) + ')')
        
        query_pack.append([exec_str, child_list[1]])

    else:
        for i in range(1, len(child_list[0])):
            exec_str = ('''UPDATE
                                documents
                            SET
                                {}=%s
                            WHERE
                                {}=%s'''.format(child_list[0][i], child_list[0][0]))
            
            query_pack.append([exec_str, [child_list[1][i], child_list[1][0]]])


    exec_query_pack(query_pack)
    
    child_list[1][0] = child_list[1][0].decode('ISO-8859-1')

    # '_idrref'
    # ,'_code'
    # ,'_description'
    # ,'_create_date'
    # ,'_sum'

    update_master_list(cur_window, child_list[1][0], new_values=[child_list[1][0],
                                                child_list[1][1],
                                                child_list[1][2],
                                                child_list[1][4],
                                                child_list[1][5]])

    if is_new:
        cur_window.nametowidget('_idrref_binary').insert(0, child_list[1][0])
        child_list[0].append('_operation')
        child_list[1].append('insert')
        msg_method = 'document_created'
    else:
        child_list[0].append('_operation')
        child_list[1].append('update')
        msg_method = 'document_updated'

    # tell other app about changes with rabbitmq
    child_list[1][4] = child_list[1][4].strftime('%d.%m.%Y')
    
    publish(msg_method, dict(zip(child_list[0], child_list[1])))

def remove_document(mn_list):
    idrref_str = mn_list.set(mn_list.focus())['_idrref']
    idrref_b = idrref_str.encode('ISO-8859-1')
    
    query_pack = []

    exec_str = ('''DELETE FROM
                        documents
                    WHERE
                        _idrref=%s''')
    
    query_pack.append([exec_str, [idrref_b]])
    exec_query_pack(query_pack)
        
    update_master_list(mn_list, idrref_str, remove=True)

    publish({'_idrref' : idrref_str,
            '_opearation' : 'delete'})

def create_document_widgets(cur_window):
    main_font = ("Arial", 14)
    
    cur_window.geometry("1080x720")
    cur_window.title("New document")
    
    rel_lbl_width = 0.4
    rel_ent_width = 0.6
    rel_btn_width = 0.15
    
    com_menu_rel_height = 0.05
    cur_rel_height = 0.05

    
    mn_btn_font = ('Times', 12)    
    
    # hidden elements
    cur_el = Entry(cur_window, name='_idrref_binary', font=main_font)

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
                        image=cur_window.master.img5,
                        borderwidth=2,
                        relief='raised')

    
    mn_doc_button2.place(relx=rel_btn_width, rely=0.0, relwidth=rel_btn_width, relheight=1.0)


    # left group
    frm1 = Frame(cur_window, name='left_group')
    frm1.place(relx=0.0, rely=com_menu_rel_height, relwidth=0.5, relheight=1.0)

    cur_lbl = Label(frm1, name='codelabel', text = "Code", font=main_font)
    cur_lbl.place(relx=0.0, rely=0.0, relwidth=rel_lbl_width, relheight=cur_rel_height)

    cur_lbl = Entry(frm1, name='_code_str', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=0.0, relwidth=rel_ent_width, relheight=cur_rel_height)
    # cur_lbl.insert(0, 'DCODE-00000001')

    cur_lbl = Label(frm1, name='descriptionlabel', text = "Description", font=main_font)
    cur_lbl.place(relx=0.0, rely=cur_rel_height, relwidth=rel_lbl_width, relheight=cur_rel_height)

    cur_lbl = Entry(frm1, name='_description_str', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=cur_rel_height, relwidth=rel_ent_width, relheight=cur_rel_height)
    # cur_lbl.insert(0, 'Document creation test')
    
    cur_lbl = Label(frm1, name='contentlabel', text = "Content", font=main_font)
    cur_lbl.place(relx=0.0, rely=(cur_rel_height + cur_rel_height), relwidth=1.0, relheight=cur_rel_height)

    cur_lbl = Text(frm1, name='_content_str', font=main_font, borderwidth=1, relief='groove')
    cur_lbl.place(relx=0.0, rely=(3.0*cur_rel_height), relwidth=1.0, relheight=(1.0 - 3.0*cur_rel_height))
    # cur_lbl.insert(1.0, 'This is a TEST document')

    #right group
    frm2 = Frame(cur_window, name='right_group')
    frm2.place(relx=0.5, rely=com_menu_rel_height, relwidth=0.5, relheight=1.0)

    cur_lbl = Label(frm2, name='create_datelabel', text = "Create date", font=main_font)
    cur_lbl.place(relx=0.0, rely=0.0, relwidth=rel_lbl_width, relheight=cur_rel_height)

    cur_lbl = Entry(frm2, name='_create_date_datetime', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=0.0, relwidth=rel_ent_width, relheight=cur_rel_height)
    # cur_lbl.insert(0, '04.07.2022')

    cur_lbl = Label(frm2, name='sumlabel', text = "Sum", font=main_font)
    cur_lbl.place(relx=0.0, rely=cur_rel_height, relwidth=rel_lbl_width, relheight=cur_rel_height)
    

    cur_lbl = Entry(frm2, name='_sum_float', font=main_font)
    cur_lbl.place(relx=rel_lbl_width, rely=cur_rel_height, relwidth=rel_ent_width, relheight=cur_rel_height)

def update_master_list(cur_window, doc_id, new_values=None, remove=False):
    cur_mn_list = cur_window.master.nametowidget('main_list')
    iid = 0
    for child in cur_mn_list.get_children():
        cur_values = cur_mn_list.item(child)['values']
        if cur_values[0] == doc_id:
            if remove:
                cur_mn_list.delete(str(iid))
            else:
                cur_mn_list.item(child, values=new_values)
            break
        iid += 1
    else:
        if not remove:
            cur_mn_list.insert(parent='',index='end',iid=iid,
                                values=new_values)

def fill_doc_from_db(cur_window, doc_id):
    
    fields_tuple = (('_code', '_description', '_create_date', '_content', '_sum'),
                    ('_code_str', '_description_str', '_create_date_datetime', '_content_str', '_sum_float'))
    
    query_pack = []

    exec_str = ('''SELECT
                        {}
                    FROM
                        documents
                    WHERE
                        _idrref = %s'''.format(', '.join(fields_tuple[0])))

    query_pack.append([exec_str, [doc_id.encode('ISO-8859-1')]])

    exec_query_pack(query_pack, need_result=True)
    
    wdict = {}
    get_all_input_widgets(cur_window, wdict)

    for query in query_pack:
        for row in query[2]:
            for i in range(len(fields_tuple[0])):
                if isinstance(row[i], datetime):
                    row[i] = row[i].strftime('%d.%m.%Y')
                
                widg = wdict[fields_tuple[1][i]]
                if isinstance(widg, Text):
                    widg.insert(1.0, row[i])
                else:
                    widg.insert(0, row[i])
    
    wdict['_idrref_binary'].insert(0, doc_id)
    cur_window.title('Document {}'.format(wdict['_code_str'].get()))

def open_document(main_window, mn_list, edit=False):
    
    cur_window = Toplevel(main_window)   


    create_document_widgets(cur_window)
    

    if not edit:
        cur_window.wait_visibility()
        cur_window.grab_set()
        return
    
    # read from DB
    cur_window.title("New document")
    fill_doc_from_db(cur_window, mn_list.set(mn_list.focus())['_idrref'])
    cur_window.wait_visibility()
    cur_window.grab_set()

def mn_list_doubleclick(event):
    tree = event.widget
    open_document(tree.master, tree, edit=True)        

def show_text_section(cur_window, rel_width, btn_name):
    
    #hide menu and list
    cur_window.nametowidget('main_list_header').place_forget()

    cur_window.nametowidget('main_list').place_forget()

    cur_window.nametowidget('main_text').place(relx=rel_width, rely=0.0, relwidth=(1.0 - rel_width), relheight=1.0)    

def show_list_section(cur_window, rel_width, h_m_rel_height):
    cur_window.nametowidget('main_list_header').place(relx=rel_width, rely=0.0, relwidth=(1.0 - rel_width), relheight=h_m_rel_height)
    cur_window.nametowidget('main_list').place(relx=rel_width, rely=h_m_rel_height, relwidth=(1.0 - rel_width), relheight=(1.0 - h_m_rel_height))

    cur_window.nametowidget('main_text').place_forget()

def create_left_section(window, rel_width, h_m_rel_height):
    rel_height = 0.1
    label_font = ("Arial", 12)


    frm = Frame(window, name='left_frame', background="grey")
    frm.place(relx=0.0, rely=0.0, relwidth=rel_width, relheight=1.0)
    
    aa = Button(frm,
                name='documents_button',
                command=lambda: show_list_section(window, rel_width, h_m_rel_height),
                text="Documents",
                image=window.img1,
                compound=LEFT,
                borderwidth=2,
                relief="raised",
                font=label_font)

    aa.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=rel_height)
    
    cc = Button(frm,
                name='about_btn',
                command=lambda: show_text_section(window, rel_width, 'about_btn'),
                text = "About",
                borderwidth=2,
                relief="raised",
                font=label_font)
    cc.place(relx=0.0, rely=rel_height, relwidth=1.0, relheight=rel_height)

    dd = Label(frm)
    dd.place(relx=0.0, rely=2.0*rel_height, relwidth=1.0, relheight=(1.0 - 2.0*rel_height))

def create_list_menu_widgets(window, rel_width, h_m_rel_height):
    mn_list = window.nametowidget('main_list')
    
    h_m_font = ('Arial', 12)
    h_m_rel_width = 0.2
        
    frm_doc_header = Frame(window, name='main_list_header', background="blue")
    frm_doc_header.place(relx=rel_width, rely=0.0, relwidth=(1.0 - rel_width), relheight=h_m_rel_height)

    mn_button = Button(frm_doc_header,
                        command=lambda: open_document(window, mn_list),
                        name='list_add',
                        text = "add",
                        image=window.img2,
                        compound=LEFT,
                        borderwidth=1,
                        relief='groove',
                        font=h_m_font)

    mn_button.place(relx=0.0, rely=0.0, relwidth=h_m_rel_width, relheight=1.0)

    mn_button = Button(frm_doc_header,
                       command=lambda: open_document(window, mn_list, edit=True),
                       name='list_edit',
                       text = "edit",
                       image=window.img3,
                       compound=LEFT,
                       borderwidth=1,
                       relief='groove',
                       font=h_m_font)

    mn_button.place(relx=h_m_rel_width, rely=0.0, relwidth=h_m_rel_width, relheight=1.0)

    mn_button = Button(frm_doc_header,
                       command=lambda: remove_document(mn_list),
                       name='list_remove',
                       text = "remove",
                       image=window.img4,
                       compound=LEFT,
                       borderwidth=1,
                       relief='groove',
                       font=h_m_font)

    mn_button.place(relx=(h_m_rel_width + h_m_rel_width), rely=0.0, relwidth=h_m_rel_width, relheight=1.0)

    mn_label = Label(frm_doc_header)
    mn_label.place(relx=(3.0 * h_m_rel_width), rely=0.0, relwidth=(1.0 - 3.0 * h_m_rel_width), relheight=1.0)

def create_list_widgets(mn_list, rel_width, h_m_rel_height):
    
    mn_list['columns'] = ('_idrref'
                          ,'_code'
                          ,'_description'
                          ,'_create_date'
                          ,'_sum')
    
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

    mn_list.bind('<Double-Button-1>', mn_list_doubleclick)
    mn_list.place(relx=rel_width, rely=h_m_rel_height, relwidth=(1.0 - rel_width), relheight=(1.0 - h_m_rel_height))

def create_text_section(window):
    main_font = ("Arial", 16)
    
    cur_text = '''
            Test project
            \"Document and process management\"
            Two document systems connected
            with RabbitMQ.
            Authentification and cache implemented by Redis service.
            
            \'aksdmi\' Dmitry Aksenov'''

    cur_elm = Text(window, name='main_text', font=main_font, borderwidth=1, background='white')
    cur_elm.insert(1.0, cur_text)
    cur_elm.tag_add("center", 1.0, "end")
    cur_elm.tag_configure("center", justify='center')
    


def create_main_window_widgets(window, mn_list):
    mntrs = screeninfo.get_monitors()
    mntrs_p = [x for x in mntrs if x.is_primary]

    if not mntrs_p:
        mntrs_p = [mntrs[0]]

    window.title("Document management")
    
    window.geometry(f'{mntrs_p[0].width}x{mntrs_p[0].height}')

    window.configure(background = "grey")

    
    rel_width = 0.18
    
    # img_width = 35.0
    
    h_m_rel_height = 0.04
       
    # left section
    create_left_section(window, rel_width, h_m_rel_height)

    # right section

    # document list menu
    create_list_menu_widgets(window, rel_width, h_m_rel_height)
    

    # document list
    create_list_widgets(mn_list, rel_width, h_m_rel_height)
    
    # hidden text sectiob
    create_text_section(window)


def exec_query_pack(query_pack, need_result=False):
   
    with closing(psycopg2.connect(dbname='main', user='postgres', 
                        password='postgres', host='localhost', port=54322)) as conn:

        with closing(conn.cursor(cursor_factory=psycopg2.extras.DictCursor)) as cursor:

            # try:
            for query in query_pack:
                cursor.execute(query[0], query[1])
            
                if need_result:
                    query.append(cursor.fetchall())

            if not need_result:
                conn.commit()

def fill_list_from_db(mn_list):
    
    query_pack = []

    exec_str = ('''SELECT
                        _idrref
                        ,_code
                        ,_description
                        ,_create_date
                        ,_sum
                    FROM
                        documents LIMIT 100''')

    query_pack.append([exec_str, []])

    exec_query_pack(query_pack, need_result=True)

    iid = 0
    
    # mn_list.configure(padding=2)
    for query in query_pack:
        for row in query[2]:
            row[0] = row[0].tobytes().decode('ISO-8859-1')
            mn_list.insert(parent='',index='end',iid=iid,
                values=row)
            iid += 1

def init_app():

    window = Tk()

    window.img1 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/assets/text-file.png')
    window.img2 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/assets/add.png')
    window.img3 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/assets/edit.png')
    window.img4 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/assets/delete.png')
    
    # style = ttk.Style()
    # style.configure('mystyle.Treeview', relief = 'flat', borderwidth = 1)
    # style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])

    tree_style = ttk.Style()
    tree_style.configure("mystyle.Treeview", highlightthickness=0, bd=0, font=('Arial', 12)) # Modify the font of the body
    tree_style.configure("mystyle.Treeview.Heading", font=('Arial', 14)) # Modify the font of the headings

    mn_list = ttk.Treeview(window, name='main_list', style="mystyle.Treeview")

    create_main_window_widgets(window, mn_list)
        
    fill_list_from_db(mn_list)

    #############################################################
        
    tracker = Tracker(window)
    tracker.bind_config()

    window.img5 = PhotoImage(file='/home/aksdmi/Python/docbsnsprocmng/docmng/assets/save-icon.png')

    window.mainloop()



if __name__ == '__main__':

    init_app()