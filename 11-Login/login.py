# -*- coding: utf-8 -*-

import requests
import sys
import os.path, time
import re

cookie_fn = 'cookie'

login_headers = {
    'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36",
    'content-type': "application/x-www-form-urlencoded",
    'accept': "*/*",
    'accept-encoding': "gzip, deflate, br",
    'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7",
    'cache-control': "no-cache"
}

login_url = 'http://localhost/login/login.php'

def login(username, password):
    payload = "username={}&password={}"
    if check_cookie_file() and (time.time() - os.path.getmtime(cookie_fn)) < 86400:
        load_cookie()
        return
    payload = payload.format(username, password)
    response = requests.request("POST", login_url, data=payload, headers=login_headers)
    cookie = ''

    for k,v in response.cookies.iteritems():
        cookie += k + '=' + v + ';'
    cookie = cookie[:-1]
    with open(cookie_fn, 'w') as f:
        f.write(cookie)
    login_headers['cookie'] = cookie
    print(cookie)

def check_cookie_file():
    return os.path.isfile(cookie_fn)

def load_cookie():
    with open(cookie_fn, 'r') as f:
        cookie = f.read()
    login_headers['cookie'] = cookie
    print('cookie loaded:', cookie)

if __name__ == "__main__":
    login('hadoop', 'c')