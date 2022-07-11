#!/usr/bin/python3

from getpass import getpass
from hashlib import sha256
from time import sleep
from redis import Redis
import screeninfo
from tkinter import *
from tkinter import ttk
import sys

class Auth():
    def __init__(self) -> None:
        self.redis_conn = Redis()
        self.window = Tk()
        self.attmts_count = 0
        self.max_attmts_count = 3
        self.want_register = False

    def update_userdata(self, login, userdata={}):
        

        userkey = f'dbprocmng:user:{login}'

        pipeln = self.redis_conn.pipeline(True)
        pipeln.multi()
        for itm in userdata.items():
            pipeln.hset(userkey, key=itm[0], value=itm[1])

        pipeln.execute()

        # return self.get_user_by_login(login)


    def get_user_by_login(self, login):
        
        return self.redis_conn.hgetall(f'dbprocmng:user:{login}')
    
    def get_and_respond(self):
        
        userlogin = self.window.nametowidget('_login_str').get()
        

        userdata = self.get_user_by_login(userlogin)
        
        if userdata:
            # print(userdata)
            userpass = self.window.nametowidget('_password_str').get()
            userpasshash = sha256(userpass.encode('utf-8')).hexdigest().encode('utf-8')

            if userpasshash != userdata[b'pass_hash']:
                
                self.attmts_count += 1
                
                if self.attmts_count == self.max_attmts_count:
                    self.window.nametowidget('feedbacklabel').configure(
                            text=f'Login FAILED! Attempts count ({self.attmts_count}) exceed! Try again later.')
                    sleep(1)
                    sys.exit(0)
                
                self.window.nametowidget('feedbacklabel').configure(
                        text=f'Incorrect password ({self.max_attmts_count - self.attmts_count} attemts remain)')
                return
            
                            
            
            self.window.nametowidget('feedbacklabel').configure(
                        text='Login SUCCESS')
            
            sleep(1)
            self.window.destroy()
            # from docmng import wmanager
            import wmanager

            wmanager.init_app()

            

        else:
            if not self.want_register:
                self.window.nametowidget('feedbacklabel').configure(
                        text=('You seems to be not registered yet\n' +
                                'Would you like to register?'))
                self.want_register = True
                return

            # press enter so = y
            userpass = self.window.nametowidget('_password_str').get()
            userpasshash = sha256(userpass.encode('utf-8')).hexdigest()

            self.update_userdata(userlogin, userdata={'pass_hash' : userpasshash})
            self.window.nametowidget('feedbacklabel').configure(
                        text='Register SUCCESS')

    def polite_exit(self):
        self.window.nametowidget('feedbacklabel').configure(
                        text='Good bye')
        sleep(1)
        sys.exit(0)

    def user_dialog(self):

        self.window.title("Authentification")
        rel_lbl_width = 0.3
        rel_entry_width = 1.0 - rel_lbl_width
        rel_btn_width = 0.3
        rel_resp_height = 0.3
        rel_inpt_height = 0.2
        rel_btn_height = 1.0 - rel_resp_height - rel_inpt_height - rel_inpt_height
        main_font = ("Arial", 12)
        btn_font = ('Times', 12)

        mntrs = screeninfo.get_monitors()
        mntrs_p = [x for x in mntrs if x.is_primary]

        if not mntrs_p:
            mntrs_p = [mntrs[0]]

        # we' ll take 2 columns and 4 rows for auth form
        self.window.geometry(
            '{}x{}'.format(int(mntrs_p[0].width * 0.25),
                           int(mntrs_p[0].height * 0.2)))

        self.window.configure(background = "grey")
        # self.window.eval('tk::PlaceWindow . center')
        # user's response field

        cur_el = Label(self.window, name='feedbacklabel', anchor=CENTER, text = "Insert credentials to login", font=("Arial", 13), foreground='green')
        cur_el.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=rel_resp_height)


        cur_el = Label(self.window, name='loginlabel', text = "Login", anchor='e', font=main_font)
        cur_el.place(relx=0.0, rely=rel_resp_height, relwidth=rel_lbl_width, relheight=rel_inpt_height)

        cur_el = Entry(self.window, name='_login_str', font=main_font)
        cur_el.place(relx=rel_lbl_width, rely=rel_resp_height, relwidth=rel_entry_width, relheight=rel_inpt_height)


        cur_el = Label(self.window, name='passwordlabel', text = "Password", anchor='e', font=main_font)
        cur_el.place(relx=0.0, rely=(rel_resp_height + rel_inpt_height), relwidth=rel_lbl_width, relheight=rel_inpt_height)

        cur_el = Entry(self.window, show='*', name='_password_str', font=main_font)
        cur_el.place(relx=rel_lbl_width, rely=(rel_resp_height + rel_inpt_height), relwidth=rel_entry_width, relheight=rel_inpt_height)

        com_menu_frm = Frame(self.window, name='com_btm_menu')
        com_menu_frm.place(relx=0.0,
                     rely=(rel_resp_height + rel_inpt_height + rel_inpt_height),
                     relwidth=1.0,
                     relheight=rel_btn_height)


        cur_el = Label(com_menu_frm)
        cur_el.place(relx=0.0, rely=0.0, relwidth=1.0, relheight=1.0)

        mn_button = Button(com_menu_frm,
                        command=self.get_and_respond,
                        name='submitbutton',
                        text = "OK",
                        borderwidth=2,
                        relief='raised',
                        font=btn_font)

    
        mn_button.place(relx=(1.0 - rel_btn_width - rel_btn_width),
                        rely=0.0,
                        relwidth=rel_btn_width,
                        relheight=1.0)


        mn_button = Button(com_menu_frm,
                        command=self.polite_exit,
                        name='cancelbutton',
                        text = "Cancel",
                        borderwidth=2,
                        relief='raised',
                        font=btn_font)

    
        mn_button.place(relx=(1.0 - rel_btn_width),
                        rely=0.0,
                        relwidth=rel_btn_width,
                        relheight=1.0)


        self.window.mainloop()       


        
    
    # def __del__(self):
    #     self.window.destroy()
    

if __name__ == '__main__':
    
    auth = Auth()
    auth.user_dialog()
