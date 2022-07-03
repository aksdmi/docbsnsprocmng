#!/usr/bin/python3

import sys
from getpass import getpass
from hashlib import sha256
from redis import Redis

class Auth():
    def __init__(self) -> None:
        self.redis_conn = Redis()

    

    def update_userdata(self, login, userdata={}):
        

        userkey = f'dbprocmng:user:{login}'

        pipeln = self.redis_conn.pipeline(True)
        pipeln.multi()
        for itm in userdata.items():
            pipeln.hset(userkey, key=itm[0], value=itm[1])

        pipeln.execute()

        return self.get_user_by_login(login)


    def get_user_by_login(self, login):
        
        return self.redis_conn.hgetall(f'dbprocmng:user:{login}')

    def user_dialog(self):
        userlog = input('Login:')

        userdata = self.get_user_by_login(userlog)

        if userdata:
            # print(userdata)
            userpass = getpass('Password:')
            userpasshash = sha256(userpass.encode('utf-8')).hexdigest().encode('utf-8')

            count = 0

            while userpasshash != userdata[b'pass_hash']:
                if count > 3:
                    print(f'Login FAILED! Attempts count ({count - 1}) exceed! Try again later.')
                    sys.exit(1)
                count += 1
                userpass = getpass(f'Password ({3 - count} attemts remain):')
                userpasshash = sha256(userpass.encode('utf-8')).hexdigest().encode('utf-8')

            
            print('Login SUCCESS')
        
        else:

            print('You seems to be not registered yet')
            res = input('Would you like to sign up? [Y]/n:')
            res = res.lower()

            chk_ans = ('y', 'n', '')

            while res not in chk_ans:
                res = input('[y|n]?:')
                res = res.lower()


            if res == '' or res == 'y':
                # press enter so = y
                userpass = getpass('Password:')
                userpasshash = sha256(userpass.encode('utf-8')).hexdigest()

                userdata = self.update_userdata(userlog, userdata={'pass_hash' : userpasshash})
                print(userdata)

            else:
                print('Good bye')
    

if __name__ == '__main__':
    
    auth = Auth()
    auth.user_dialog()