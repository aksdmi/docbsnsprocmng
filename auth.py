#!/usr/bin/python3

import sys
from getpass import getpass
from hashlib import sha256
from redis import Redis


def update_userdata(redis_conn, login, userdata={}):
    

    userkey = f'dbprocmng:user:{login}'

    pipeln = redis_conn.pipeline(True)
    pipeln.multi()
    for itm in userdata.items():
        pipeln.hset(userkey, key=itm[0], value=itm[1])

    pipeln.execute()

    return get_user_by_login(redis_conn, login)


def auth(username, password):
    pass


def get_user_by_login(redis_conn, login):
    
    return redis_conn.hgetall(f'dbprocmng:user:{login}')
    

if __name__ == '__main__':
    
    conn = Redis()
    
    userlog = input('Login:')

    userdata = get_user_by_login(conn, userlog)

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
            # userpass = input('Password:')
            userpasshash = sha256(userpass.encode('utf-8')).hexdigest()


            userdata = update_userdata(conn, userlog, userdata={'pass_hash' : userpasshash})
            print(userdata)

        else:
            print('Good bye')
    
    
    