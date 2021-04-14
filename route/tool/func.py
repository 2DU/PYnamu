import os
import sys
import platform
import hmac
import hashlib
import os
import time
import math
import base64
import urllib.parse
import random

import segno

for i in range(0, 2):
    try:
        from diff_match_patch import diff_match_patch
        import werkzeug.routing
        import werkzeug.debug
        import flask_reggie
        import tornado.ioloop
        import tornado.httpserver
        import tornado.wsgi
        import urllib.request
        import email.mime.text
        import email.utils
        import email.header
        import requests
        import sqlite3
        import pymysql
        import hashlib
        import smtplib
        import asyncio
        import zipfile
        import shutil
        import threading
        import PIL
        import logging
        import random
        import flask
        import json
        import html
        import re

        if sys.version_info < (3, 6):
            import sha3

        from .mark import *
    except ImportError as e:
        if i == 0:
            print(e)
            print('----')
            if platform.system() == 'Linux' or platform.system() == 'Windows':
                sys_pip_ins = os.system(
                    'python' + ('3' if platform.system() != 'Windows' else '') + ' ' + \
                    '-m pip install --user -r requirements.txt'
                )
                if sys_pip_ins == 0:
                    print('----')
                    try:
                        os.execl(sys.executable, sys.executable, *sys.argv)
                    except:
                        try:
                            os.execl(sys.executable, '"' + sys.executable + '"', *sys.argv)
                        except:
                            print('Error : restart failed')
                            raise
                else:
                    print('Error : library install failed')
                    raise
            
        print('----')
        print(e)
        raise

global_lang = {}

data_css_ver = '78'
data_css = ''

conn = ''
curs = ''

def load_conn(data):
    global conn
    global curs

    conn = data
    curs = conn.cursor()

    load_conn2(data)

def http_warring():
    return '''
        <div id="http_warring_text"></div>
        <script>
            if(window.location.protocol !== 'https:') {
                document.getElementById('http_warring_text').innerHTML = "''' + load_lang('http_warring') + '''";
                document.getElementById('http_warring_text').style.margin = "10px 0px 0px 0px";
            }
        </script>
    '''
    
def send_email(who, title, data):
    try:
        curs.execute(db_change('' + \
            'select name, data from other ' + \
            'where name = "smtp_email" or name = "smtp_pass" or name = "smtp_server" or name = "smtp_port" or name = "smtp_security"' + \
        ''))
        rep_data = curs.fetchall()

        smtp_email = ''
        smtp_pass = ''
        smtp_server = ''
        smtp_security = ''
        smtp_port = ''
        smtp = ''

        for i in rep_data:
            if i[0] == 'smtp_email':
                smtp_email = i[1]
            elif i[0] == 'smtp_pass':
                smtp_pass = i[1]
            elif i[0] == 'smtp_server':
                smtp_server = i[1]
            elif i[0] == 'smtp_security':
                smtp_security = i[1]
            elif i[0] == 'smtp_port':
                smtp_port = i[1]
        
        smtp_port = int(smtp_port)
        if smtp_security == 'plain':
            smtp = smtplib.SMTP(smtp_server, smtp_port)
        elif smtp_security == 'starttls':
            smtp = smtplib.SMTP(smtp_server, smtp_port)
            smtp.starttls()
        else:
            # if smtp_security == 'tls':
            smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
        
        smtp.login(smtp_email, smtp_pass)

        domain = load_domain()
        wiki_name = wiki_set()[0]
        
        msg = email.mime.text.MIMEText(data)
        msg['Subject'] = title
        msg['From'] = 'openNAMU <noreply@' + domain + '>'
        msg['To'] = who
        
        smtp.sendmail('openNAMU@' + domain, who, msg.as_string())
        smtp.quit()

        return 1
    except Exception as e:
        print('----')
        print('Error : email send error')
        print(e)

        return 0

def load_domain():
    curs.execute(db_change("select data from other where name = 'domain'"))
    domain = curs.fetchall()
    domain = domain[0][0] if domain and domain[0][0] != '' else flask.request.host_url

    return domain

def load_random_key(long = 64):
    return ''.join(random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(long))

def last_change(data):
    return data

def easy_minify(data, tool = None):
    return last_change(data)

def render_set(doc_name = '', doc_data = '', data_type = 'view', data_in = '', doc_acl = ''):
    # data_type in ['view', 'raw', 'api_view', 'backlink']
    doc_acl = acl_check(doc_name, 'render') if doc_acl == '' else doc_acl
    doc_data = 0 if not doc_data else doc_data
        
    if doc_acl == 1:
        return 'HTTP Request 401.3'
    else:
        if data_type == 'raw':
            return doc_data
        else:
            if doc_data != 0:
                return render_do(doc_name, doc_data, data_type, data_in)
            else:
                return 'HTTP Request 404'

def update(ver_num, set_data):
    print('----')
    # 업데이트 하위 호환 유지 함수

    if ver_num < 3160027:
        print('Add init set')
        set_init()

    if ver_num < 3170002:
        curs.execute(db_change("select html from html_filter where kind = 'extension'"))
        if not curs.fetchall():
            for i in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
                curs.execute(db_change("insert into html_filter (html, kind) values (?, 'extension')"), [i])

    if ver_num < 3170400:
        curs.execute(db_change("select title, sub, code from topic where id = '1'"))
        for i in curs.fetchall():
            curs.execute(db_change("update topic set code = ? where title = ? and sub = ?"), [i[2], i[0], i[1]])
            curs.execute(db_change("update rd set code = ? where title = ? and sub = ?"), [i[2], i[0], i[1]])

    if ver_num < 3171800:
        curs.execute(db_change("select data from other where name = 'recaptcha'"))
        change_rec = curs.fetchall()
        if change_rec and change_rec[0][0] != '':
            new_rec = re.search(r'data-sitekey="([^"]+)"', change_rec[0][0])
            if new_rec:
                curs.execute(db_change("update other set data = ? where name = 'recaptcha'"), [new_rec.group(1)])
            else:
                curs.execute(db_change("update other set data = '' where name = 'recaptcha'"))
                curs.execute(db_change("update other set data = '' where name = 'sec_re'"))
    
    if ver_num < 3172800 and set_data['db_type'] == 'mysql':
        get_data_mysql = json.loads(open('data/mysql.json').read())
        
        with open('data/mysql.json', 'w') as f:
            f.write('{ "user" : "' + get_data_mysql['user'] + '", "password" : "' + get_data_mysql['password'] + '", "host" : "localhost" }')

    if ver_num < 3183603:
        curs.execute(db_change("select block from ban where band = 'O'"))
        for i in curs.fetchall():
            curs.execute(db_change("update ban set block = ?, band = 'regex' where block = ? and band = 'O'"), [
                '^' + i[0].replace('.', '\\.'),
                i[0]
            ])

        curs.execute(db_change("select block from rb where band = 'O'"))
        for i in curs.fetchall():
            curs.execute(db_change("update rb set block = ?, band = 'regex' where block = ? and band = 'O'"), [
                '^' + i[0].replace('.', '\\.'),
                i[0]
            ])

    if ver_num < 3190201:
        today_time = get_time()

        curs.execute(db_change("select block, end, why, band, login from ban"))
        for i in curs.fetchall():
            curs.execute(db_change("insert into rb (block, end, today, why, band, login, ongoing) values (?, ?, ?, ?, ?, ?, ?)"), [
                i[0],
                i[1],
                today_time,
                i[2],
                i[3],
                i[4],
                '1'
            ])

    if ver_num < 3191301:
        curs.execute(db_change('' + \
            'select id, title, date from history ' + \
            'where not title like "user:%" ' + \
            'order by date desc ' + \
            'limit 50' + \
        ''))
        data_list = curs.fetchall()
        for get_data in data_list:
            curs.execute(db_change("insert into rc (id, title, date, type) values (?, ?, ?, 'normal')"), [
                get_data[0], 
                get_data[1],
                get_data[2]
            ])

    if ver_num < 3202400:
        curs.execute(db_change("select data from other where name = 'update'"))
        get_data = curs.fetchall()
        if get_data and get_data[0][0] == 'master':
            curs.execute(db_change("update other set data = 'beta' where name = 'update'"), [])

    if ver_num < 3202600:
        curs.execute(db_change("select name, regex, sub from filter"))
        for i in curs.fetchall():
            curs.execute(db_change("insert into html_filter (html, kind, plus, plus_t) values (?, 'regex_filter', ?, ?)"), [
                i[0], 
                i[1],
                i[2]
            ])

        curs.execute(db_change("select title, link, icon from inter"))
        for i in curs.fetchall():
            curs.execute(db_change("insert into html_filter (html, kind, plus, plus_t) values (?, 'inter_wiki', ?, ?)"), [
                i[0], 
                i[1],
                i[2]
            ])

    if ver_num < 3203400:
        curs.execute(db_change("select user, css from custom"))
        for i in curs.fetchall():
            curs.execute(db_change("insert into user_set (name, id, data) values ('custom_css', ?, ?)"), [
                re.sub(r' \(head\)$', '', i[0]), 
                i[1]
            ])

    if ver_num < 3205500:
        curs.execute(db_change("select title, decu, dis, view, why from acl"))
        for i in curs.fetchall():
            curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [i[0], i[1], 'decu'])
            curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [i[0], i[2], 'dis'])
            curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [i[0], i[3], 'view'])
            curs.execute(db_change("insert into acl (title, data, type) values (?, ?, ?)"), [i[0], i[4], 'why'])
          
    # 캐시 초기화
    if ver_num < 3300101:
        curs.execute(db_change('delete from cache_data'))
    
    conn.commit()

    print('Update completed')

def set_init():
    # 초기값 설정 함수    
    curs.execute(db_change("select html from html_filter where kind = 'email'"))
    if not curs.fetchall():
        for i in ['naver.com', 'gmail.com', 'daum.net', 'kakao.com']:
            curs.execute(db_change("insert into html_filter (html, kind) values (?, 'email')"), [i])

    curs.execute(db_change("select html from html_filter where kind = 'extension'"))
    if not curs.fetchall():
        for i in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            curs.execute(db_change("insert into html_filter (html, kind) values (?, 'extension')"), [i])

    curs.execute(db_change('select data from other where name = "smtp_server" or name = "smtp_port" or name = "smtp_security"'))
    if not curs.fetchall():
        for i in [['smtp_server', 'smtp.gmail.com'], ['smtp_port', '587'], ['smtp_security', 'starttls']]:
            curs.execute(db_change("insert into other (name, data) values (?, ?)"), [i[0], i[1]])

def pw_encode(data, type_d = ''):
    if type_d == '':
        curs.execute(db_change('select data from other where name = "encode"'))
        set_data = curs.fetchall()

        type_d = set_data[0][0]

    if type_d == 'sha256':
        return hashlib.sha256(bytes(data, 'utf-8')).hexdigest()
    else:
        if sys.version_info < (3, 6):
            return sha3.sha3_256(bytes(data, 'utf-8')).hexdigest()
        else:
            return hashlib.sha3_256(bytes(data, 'utf-8')).hexdigest()

def pw_check(data, data2, type_d = 'no', id_d = ''):
    curs.execute(db_change('select data from other where name = "encode"'))
    db_data = curs.fetchall()

    if type_d != 'no':
        if type_d == '':
            set_data = 'sha3'
        else:
            set_data = type_d
    else:
        set_data = db_data[0][0]

    re_data = 1 if pw_encode(data, set_data) == data2 else 0
    if db_data[0][0] != set_data and re_data == 1 and id_d != '':
        curs.execute(db_change("update user set pw = ?, encode = ? where id = ?"), [pw_encode(data), db_data[0][0], id_d])

    return re_data

def add_alarm(who, context):
    curs.execute(db_change('insert into alarm (name, data, date) values (?, ?, ?)'), [who, context, get_time()])

def captcha_get():
    data = ''

    if ip_or_user() != 0:
        curs.execute(db_change('select data from other where name = "recaptcha"'))
        recaptcha = curs.fetchall()
        if recaptcha and recaptcha[0][0] != '':
            curs.execute(db_change('select data from other where name = "sec_re"'))
            sec_re = curs.fetchall()
            if sec_re and sec_re[0][0] != '':
                curs.execute(db_change('select data from other where name = "recaptcha_ver"'))
                rec_ver = curs.fetchall()
                if not rec_ver or rec_ver[0][0] == '':
                    data += '' + \
                        '<script src="https://www.google.com/recaptcha/api.js" async defer></script>' + \
                        '<div class="g-recaptcha" data-sitekey="' + recaptcha[0][0] + '"></div>' + \
                        '<hr class="main_hr">' + \
                    ''
                else:
                    data += '' + \
                        '<script src="https://www.google.com/recaptcha/api.js?render=' + recaptcha[0][0] + '"></script>' + \
                        '<input type="hidden" id="g-recaptcha" name="g-recaptcha">' + \
                        '<script type="text/javascript">' + \
                            'grecaptcha.ready(function() {' + \
                                'grecaptcha.execute(\'' + recaptcha[0][0] + '\', {action: \'homepage\'}).then(function(token) {' + \
                                    'document.getElementById(\'g-recaptcha\').value = token;' + \
                                '});' + \
                            '});' + \
                        '</script>' + \
                    ''

    return data

def captcha_post(re_data, num = 1):
    if num == 1:
        curs.execute(db_change('select data from other where name = "sec_re"'))
        sec_re = curs.fetchall()
        if sec_re and sec_re[0][0] != '' and ip_or_user() != 0 and captcha_get() != '':
            try:
                data = urllib.request.urlopen('https://www.google.com/recaptcha/api/siteverify?secret=' + sec_re[0][0] + '&response=' + re_data)
            except:
                data = None

            if data and data.getcode() == 200:
                json_data = json.loads(data.read().decode(data.headers.get_content_charset()))
                if json_data['success'] == True:
                    return 0
                else:
                    return 1
            else:
                return 0
        else:
            return 0
    else:
        pass

def ua_plus(id, ip, ua, time):
    curs.execute(db_change("select data from other where name = 'ua_get'"))
    rep_data = curs.fetchall()
    if rep_data and rep_data[0][0] != '':
        pass
    else:
        curs.execute(db_change("insert into ua_d (name, ip, ua, today, sub) values (?, ?, ?, ?, '')"), [id, ip, ua, time])

def load_lang(data, num = 2, safe = 0):
    global global_lang

    for i in range(0, 2):
        if i == 0:
            ip = ip_check()
            if ip_or_user(ip) == 0:
                curs.execute(db_change('select data from user_set where name = "lang" and id = ?'), [ip])
                rep_data = curs.fetchall()
            else:
                if 'lang' in flask.session:
                    rep_data = [[flask.session['lang']]]
                else:
                    continue
        else:
            curs.execute(db_change("select data from other where name = 'language'"))
            rep_data = curs.fetchall()
        
        if rep_data and rep_data[0][0] != '' and rep_data[0][0] != 'default':
            try:
                if not rep_data[0][0] in global_lang:
                    lang = json.loads(open(os.path.join('language', rep_data[0][0] + '.json'), encoding='utf8').read())
                    global_lang[rep_data[0][0]] = lang
                else:
                    lang = global_lang[rep_data[0][0]]
            except:
                continue

            if data in lang:
                return lang[data] if safe == 1 else html.escape(lang[data])
            else:
                continue
        else:
            continue
    
    return html.escape(data + ' (' + rep_data[0][0] + ')')

def ip_or_user(data = ''):
    if data == '':
        data = ip_check()

    if re.search(r'(\.|:)', data):
        return 1
    else:
        return 0

def edit_button():
    insert_list = []

    curs.execute(db_change("select html, plus from html_filter where kind = 'edit_top'"))
    db_data = curs.fetchall()
    for get_data in db_data:
        insert_list += [[get_data[1], get_data[0]]]

    data = ''
    for insert_data in insert_list:
        data += '<a href="javascript:do_insert_data(\'content\', \'' + insert_data[0] + '\')">(' + insert_data[1] + ')</a> '

    if admin_check() == 1:
        data += (' ' if data != '' else '') + '<a href="/edit_top">(' + load_lang('add') + ')</a>'

    return data + '<hr class="main_hr">'

def ip_warring():
    if ip_or_user() != 0:
        curs.execute(db_change('select data from other where name = "no_login_warring"'))
        data = curs.fetchall()
        if data and data[0][0] != '':
            text_data = '' + \
                '<span>' + data[0][0] + '</span>' + \
                '<hr class="main_hr">' + \
            ''
        else:
            text_data = '' + \
                '<span>' + load_lang('no_login_warring') + '</span>' + \
                '<hr class="main_hr">' + \
            ''
    else:
        text_data = ''

    return text_data

def skin_check(set_n = 0):
    skin_list = load_skin('marisa', 1)
    skin = skin_list[0]
    check_list = []
    ip = ip_check()
    
    if ip_or_user(ip) == 0:
        curs.execute(db_change('select data from user_set where name = "skin" and id = ?'), [ip])
        skin_exist = curs.fetchall()
        check_list += skin_exist
    else:
        if 'skin' in flask.session:
            check_list += [[flask.session['skin']]]
            
    curs.execute(db_change('select data from other where name = "skin"'))
    skin_exist = curs.fetchall()
    check_list += skin_exist
    
    for i in check_list:
        if i[0] != '' and i[0] in skin_list:
            skin = i[0]
            
            break

    return './views/' + skin + '/index.html' if set_n == 0 else skin

def next_fix(link, num, page, end = 50):
    list_data = ''

    if num == 1:
        if len(page) == end:
            list_data += '' + \
                '<hr class="main_hr">' + \
                '<a href="' + link + str(num + 1) + '">(' + load_lang('next') + ')</a>' + \
            ''
    elif len(page) != end:
        list_data += '' + \
            '<hr class="main_hr">' + \
            '<a href="' + link + str(num - 1) + '">(' + load_lang('previous') + ')</a>' + \
        ''
    else:
        list_data += '' + \
            '<hr class="main_hr">' + \
            '<a href="' + link + str(num - 1) + '">(' + load_lang('previous') + ')</a> <a href="' + link + str(num + 1) + '">(' + load_lang('next') + ')</a>' + \
        ''

    return list_data

def other2(data):
    global data_css
    global data_css_ver

    data += ['' for _ in range(0, 3 - len(data))]

    if data_css == '':
        for i_data in os.listdir(os.path.join("views", "main_css", "css")):
            if i_data != 'sub':
                data_css += '<link rel="stylesheet" href="/views/main_css/css/' + i_data + '?ver=' + data_css_ver + '">'

        for i_data in os.listdir(os.path.join("views", "main_css", "js")):
            if i_data != 'sub':
                data_css += '<script src="/views/main_css/js/' + i_data + '?ver=' + data_css_ver + '"></script>'

    data = data[0:2] + ['', '''
        <link   rel="stylesheet"
                href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@10.1.2/build/styles/default.min.css">
        <link   rel="stylesheet"
                href="https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.css"
                integrity="sha384-AfEj0r4/OFrOo5t7NnNe46zW/tFgW6x/bCJG8FqQCEo3+Aro6EYUG4+cU+KJWu/X"
                crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/katex@0.12.0/dist/katex.min.js"
                integrity="sha384-g7c+Jr9ZivxKLnZTDUhnkOnsh30B4H0rpLUpJ4jAIKs4fnJI+sEnkvrMWph2EDg4"
                crossorigin="anonymous"></script>
        <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@10.1.2/build/highlight.min.js"></script>
    ''' + data_css + '<script>window.addEventListener(\'DOMContentLoaded\', main_css_skin_load);</script>'] + data[2:]

    return data

def cut_100(data):
    if re.search(r'^\/w\/', flask.request.path):
        data = re.sub(r'<script>((\n*(((?!<\/script>).)+)\n*)+)<\/script>', '', data)
        data = re.sub(r'<hr class="main_hr">((\n*((.+)\n*))+)$', '', data)
        data = re.sub(r'<div id="cate_all">((\n*((.+)\n*))+)$', '', data)        

        data = re.sub(r'<(((?!>).)*)>', ' ', data)
        data = re.sub(r'\n', ' ', data)
        data = re.sub(r'^ +', '', data)
        data = re.sub(r' +$', '', data)
        data = re.sub(r' {2,}', ' ', data)
    
        return data[0:100] + '...'
    else:
        return ''

def wiki_set(num = 1):
    if num == 1:
        skin_name = skin_check(1)
        data_list = []

        curs.execute(db_change('select data from other where name = ?'), ['name'])
        db_data = curs.fetchall()
        data_list += [db_data[0][0]] if db_data and db_data[0][0] != '' else ['Wiki']

        curs.execute(db_change('select data from other where name = "license"'))
        db_data = curs.fetchall()
        data_list += [db_data[0][0]] if db_data and db_data[0][0] != '' else ['ARR']

        data_list += ['', '']

        curs.execute(db_change('select data from other where name = "logo" and coverage = ?'), [skin_name])
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            data_list += [db_data[0][0]]
        else:
            curs.execute(db_change('select data from other where name = "logo" and coverage = ""'))
            db_data = curs.fetchall()
            data_list += [db_data[0][0]] if db_data and db_data[0][0] != '' else [data_list[0]]

        head_data = ''

        curs.execute(db_change("select data from other where name = 'head' and coverage = ''"))
        db_data = curs.fetchall()
        head_data += db_data[0][0] if db_data and db_data[0][0] != '' else ''

        curs.execute(db_change("select data from other where name = 'head' and coverage = ?"), [skin_name])
        db_data = curs.fetchall()
        head_data += db_data[0][0] if db_data and db_data[0][0] != '' else ''
            
        data_list += [head_data]
    elif num == 2:
        curs.execute(db_change('select data from other where name = "frontpage"'))
        db_data = curs.fetchall()
        data_list = db_data[0][0] if db_data and db_data[0][0] != '' else 'FrontPage'
    elif num == 3:
        curs.execute(db_change('select data from other where name = "upload"'))
        db_data = curs.fetchall()
        data_list = db_data[0][0] if db_data and db_data[0][0] != '' else '2'
    else:
        data_list = ''

    return data_list

def admin_check(num = None, what = None, name = ''):
    ip = ip_check() if name == '' else name
    time_data = get_time()

    curs.execute(db_change("select acl from user where id = ?"), [ip])
    user = curs.fetchall()
    if user:
        back_num = num
        while 1:
            if num == 1:
                check = 'ban'
            elif num == 2:
                check = 'nothing'
            elif num == 3:
                check = 'toron'
            elif num == 4:
                check = 'check'
            elif num == 5:
                check = 'acl'
            elif num == 6:
                check = 'hidel'
            elif num == 7:
                check = 'give'
            else:
                check = 'owner'

            curs.execute(db_change('select name from alist where name = ? and acl = ?'), [user[0][0], check])
            if curs.fetchall():
                if what:
                    curs.execute(db_change("insert into re_admin (who, what, time) values (?, ?, ?)"), [ip, what, time_data])
                    conn.commit()

                return 1
            else:
                if back_num == 'all':
                    if num == 'all':
                        num = 1
                    elif num != 8:
                        num += 1
                    else:
                        break
                elif num:
                    num = None
                else:
                    break

    return 0

def ip_pas(raw_ip, type_d = 0):
    hide = 0
    end_ip = {}

    if type(raw_ip) != type([]):
        get_ip = [raw_ip]
        return_ip = 1
    else:
        get_ip = raw_ip
        return_ip = 0

    for raw_ip in get_ip:
        if not raw_ip in end_ip:
            if ip_or_user(raw_ip) != 0:
                curs.execute(db_change("select data from other where name = 'ip_view'"))
                data = curs.fetchall()
                if data and data[0][0] != '':
                    ip = re.sub(r'\.([^.]*)\.([^.]*)$', '.*.*', raw_ip) if re.search(r'\.', raw_ip) else re.sub(r':([^:]*):([^:]*)$', ':*:*', raw_ip)
                    hide = 1 if not admin_check(1) else 0
                else:
                    ip = raw_ip
            else:
                if type_d == 0:
                    ip = '<a href="/w/' + url_pas('user:' + raw_ip) + '">' + raw_ip + '</a>'
                    ip = '<b>' + ip + '</b>' if admin_check('all', None, raw_ip) == 1 else ip
                else:
                    ip = raw_ip

            if type_d == 0:
                if ban_check(raw_ip) == 1:
                    ip = '<s>' + ip + '</s>'

                    if ban_check(raw_ip, 'login') == 1:
                        ip = '<i>' + ip + '</i>'

                ip = (ip + ' <a href="/tool/' + url_pas(raw_ip) + '">(' + load_lang('tool') + ')</a>') if hide == 0 else ip
        
            end_ip[raw_ip] = ip

    return ip if return_ip == 1 else end_ip

def custom():
    ip = ip_check()
    if ip_or_user(ip) == 0:
        user_icon = 1
        user_name = ip

        curs.execute(db_change("select data from user_set where id = ? and name = 'custom_css'"), [ip])
        user_head = curs.fetchall()
        user_head = user_head[0][0] if user_head else ''
        
        curs.execute(db_change('select data from user_set where name = "email" and id = ?'), [ip])
        email = curs.fetchall()
        email = email[0][0] if email else ''

        if admin_check('all') == 1:
            user_admin = '1'
            user_acl_list = []

            curs.execute(db_change("select acl from user where id = ?"), [ip])
            curs.execute(db_change('select acl from alist where name = ?'), [curs.fetchall()[0][0]])
            user_acl = curs.fetchall()
            for i in user_acl:
                user_acl_list += [i[0]]

            user_acl_list = user_acl_list if user_acl != [] else '0'
        else:
            user_admin = '0'
            user_acl_list = '0'

        curs.execute(db_change("select count(*) from alarm where name = ?"), [ip])
        count = curs.fetchall()
        user_notice = str(count[0][0]) if count else '0'
    else:
        user_icon = 0
        user_name = load_lang('user')
        email = ''
        user_admin = '0'
        user_acl_list = '0'
        user_notice = '0'
        user_head = flask.session['head'] if 'head' in flask.session else ''

    curs.execute(db_change("select title from rd where title = ? and stop = ''"), ['user:' + ip])
    user_topic = '1' if curs.fetchall() else '0'

    return [
        '',
        '',
        user_icon,
        user_head,
        email,
        user_name,
        user_admin,
        str(ban_check()),
        user_notice,
        user_acl_list,
        ip,
        user_topic
    ]

def load_skin(data = '', set_n = 0, default = 0):
    # data -> 가장 앞에 있을 스킨 이름
    # set_n == 0 -> 스트링으로 반환
    # set_n == 1 -> 리스트로 반환
    # default == 0 -> 디폴트 미포함
    # default == 1 -> 디폴트 포함

    skin_return_data = '' if set_n == 0 else []
    system_file = ['main_css']
    skin_list_get = os.listdir(os.path.abspath('views'))

    if default == 1:
        skin_list_get += ['default']

    if data == '':
        curs.execute(db_change('select data from user_set where name = "skin" and id = ?'), [ip_check()])
        data = curs.fetchall()
        if not data:
            curs.execute(db_change('select data from other where name = "skin"'))
            data = curs.fetchall()
            if not data or data[0][0] == '':
                if default == 1:
                    data = [['default']]
                else:
                    data = [['marisa']]
    else:
        data = [[data]]

    for skin_data in skin_list_get:
        see_data = skin_data if skin_data != 'default' else load_lang('default')

        if not skin_data in system_file:
            if data[0][0] == skin_data:
                if set_n == 0:
                    skin_return_data = '<option value="' + skin_data + '">' + see_data + '</option>' + skin_return_data
                else:
                    skin_return_data = [skin_data] + skin_return_data
            else:
                if set_n == 0:
                    skin_return_data += '<option value="' + skin_data + '">' + see_data + '</option>'
                else:
                    skin_return_data += [skin_data]                    

    return skin_return_data

def slow_edit_check():
    curs.execute(db_change("select data from other where name = 'slow_edit'"))
    slow_edit = curs.fetchall()
    if slow_edit and slow_edit != '0' and admin_check(5) != 1:
        slow_edit = slow_edit[0][0]

        curs.execute(db_change("select date from history where ip = ? order by date desc limit 1"), [ip_check()])
        last_edit_data = curs.fetchall()
        if last_edit_data:
            last_edit_data = int(re.sub(' |:|-', '', last_edit_data[0][0]))
            now_edit_data = int((datetime.datetime.now() - datetime.timedelta(seconds = int(slow_edit))).strftime("%Y%m%d%H%M%S"))

            if last_edit_data > now_edit_data:
                return 1

    return 0

def acl_check(name = 'test', tool = '', topic_num = '1'):
    ip = ip_check()
    get_ban = ban_check()
    acl_c = re.search(r"^user:((?:(?!\/).)*)", name) if name else None
    if tool == '' and acl_c:
        acl_n = acl_c.groups()

        if get_ban == 1:
            return 1

        if admin_check(5) == 1:
            return 0

        curs.execute(db_change("select data from acl where title = ? and type = 'decu'"), ['user:' + acl_n[0]])
        acl_data = curs.fetchall()
        if acl_data:
            if acl_data[0][0] == 'all':
                return 0
            elif acl_data[0][0] == 'user' and not ip_or_user(ip) == 1:
                return 0
            elif ip == acl_n[0] and not ip_or_user(ip) == 1:
                return 0
        else:
            if ip == acl_n[0] and not ip_or_user(ip) == 1 and not ip_or_user(acl_n[0]) == 1:
                return 0

        return 1

    if tool == 'topic':
        if not name:
            curs.execute(db_change("select title from rd where code = ?"), [topic_num])
            name = curs.fetchall()
            name = name[0][0] if name else 'test'
        
        end = 3
    elif tool == 'render' or tool == '' or tool == 'vote':
        if tool == '' and acl_check(name, 'render') == 1:
            return 1

        end = 2
    else:
        end = 1

    for i in range(0, end):
        if tool == '':
            if i == 0:
                curs.execute(db_change("select data from acl where title = ? and type = 'decu'"), [name])
            else:
                curs.execute(db_change('select data from other where name = "edit"'))

            num = 5
        elif tool == 'topic':
            if i == 0 and topic_num:
                curs.execute(db_change("select acl from rd where code = ?"), [topic_num])
            elif i == 1:
                curs.execute(db_change("select data from acl where title = ? and type = 'dis'"), [name])
            else:
                curs.execute(db_change('select data from other where name = "discussion"'))

            num = 3
        elif tool == 'upload':
            curs.execute(db_change("select data from other where name = 'upload_acl'"))

            num = 5
        elif tool == 'many_upload':
            curs.execute(db_change("select data from other where name = 'many_upload_acl'"))

            num = 5
        elif tool == 'vote':
            if i == 0:
                curs.execute(db_change('select acl from vote where id = ? and user = ""'), [topic_num])
            else:
                curs.execute(db_change('select data from other where name = "vote_acl"'))

            num = None
        else:
            # tool == 'render'
            if i == 0:
                curs.execute(db_change("select data from acl where title = ? and type = 'view'"), [name])
            else:
                curs.execute(db_change("select data from other where name = 'all_view_acl'"))

            num = 5

        acl_data = curs.fetchall()
        if  (i == (end - 1) and (not acl_data or acl_data[0][0] == '' or acl_data[0][0] == 'normal')) and \
            get_ban == 1 and \
            tool != 'render':
            return 1
        elif acl_data and acl_data[0][0] != 'normal' and acl_data[0][0] != '':
            if acl_data[0][0] != 'ban' and get_ban == 1 and tool != 'render':
                return 1

            if acl_data[0][0] == 'all' or acl_data[0][0] == 'ban':
                return 0
            elif acl_data[0][0] == 'user':
                if ip_or_user(ip) != 1:
                    return 0
            elif acl_data[0][0] == 'admin':
                if ip_or_user(ip) != 1:
                    if admin_check(num) == 1:
                        return 0
            elif acl_data[0][0] == '50_edit':
                if ip_or_user(ip) != 1:
                    if admin_check(num) == 1:
                        return 0
                    else:
                        curs.execute(db_change("select count(*) from history where ip = ?"), [ip])
                        count = curs.fetchall()
                        count = count[0][0] if count else 0
                        if count >= 50:
                            return 0
            elif acl_data[0][0] == 'before':
                if ip_or_user(ip) != 1:
                    if admin_check(num) == 1:
                        return 0
                
                curs.execute(db_change("select ip from history where title = ? and ip = ?"), [name, ip])
                if curs.fetchall():
                    return 0
            elif acl_data[0][0] == '30_day':
                if ip_or_user(ip) != 1:
                    if admin_check(num) == 1:
                        return 0
                    else:
                        curs.execute(db_change("select date from user where id = ?"), [ip])
                        user_date = curs.fetchall()[0][0]
                        
                        time_1 = datetime.datetime.strptime(user_date, '%Y-%m-%d %H:%M:%S') + datetime.timedelta(days = 30)
                        time_2 = datetime.datetime.strptime(get_time(), '%Y-%m-%d %H:%M:%S')
                        
                        if time_2 > time_1:
                            return 0
            elif acl_data[0][0] == 'email':
                if ip_or_user(ip) != 1:
                    if admin_check(num) == 1:
                        return 0
                    else:
                        curs.execute(db_change("select data from user_set where id = ? and name = 'email'"), [ip])
                        if curs.fetchall():
                            return 0
            elif acl_data[0][0] == 'owner':
                if admin_check() == 1:
                    return 0
            elif acl_data[0][0] == 'ban_admin':
                if admin_check(1) == 1 or ban_check() == 1:
                    return 0

            return 1
        else:
            if i == (end - 1):
                if tool == 'topic' and topic_num:
                    curs.execute(db_change("select title from rd where code = ? and stop != ''"), [topic_num])
                    if curs.fetchall():
                        if admin_check(3, 'topic (code ' + topic_num + ')') == 1:
                            return 0
                    else:
                        return 0
                else:
                    return 0

    return 1

def ban_check(ip = None, tool = None):
    ip = ip_check() if not ip else ip

    if admin_check(None, None, ip) == 1:
        return 0

    curs.execute(db_change("update rb set ongoing = '' where end < ? and end != '' and ongoing = '1'"), [get_time()])
    conn.commit()

    curs.execute(db_change("" + \
        "select login, block from rb " + \
        "where ((end > ? and end != '') or end = '') and band = 'regex' and ongoing = '1'" + \
    ""), [get_time()])
    regex_d = curs.fetchall()
    for test_r in regex_d:
        g_regex = re.compile(test_r[1])
        if g_regex.search(ip):
            if tool and tool == 'login':
                if test_r[0] != 'O':
                    return 1
            else:
                return 1

    curs.execute(db_change("" + \
        "select login from rb " + \
        "where ((end > ? and end != '') or end = '') and block = ? and band = '' and ongoing = '1'" + \
    ""), [get_time(), ip])
    ban_d = curs.fetchall()
    if ban_d:
        if tool and tool == 'login':
            if ban_d[0][0] != 'O':
                return 1
        else:
            return 1

    return 0

def ban_insert(name, end, why, login, blocker, type_d = None):
    now_time = get_time()
    band = type_d if type_d else ''

    curs.execute(db_change("update rb set ongoing = '' where end < ? and end != '' and ongoing = '1'"), [now_time])
    curs.execute(db_change("" + \
        "select block from rb where ((end > ? and end != '') or end = '') and block = ? and band = ? and ongoing = '1'" + \
    ""), [now_time, name, band])
    if curs.fetchall():
        curs.execute(db_change("insert into rb (block, end, today, blocker, why, band) values (?, ?, ?, ?, ?, ?)"), [
            name,
            'release',
            now_time,
            blocker,
            '',
            band
        ])
        curs.execute(db_change("update rb set ongoing = '' where block = ? and band = ? and ongoing = '1'"), [name, band])
    else:
        login = 'O' if login != '' else ''

        if end != '0':
            end = int(number_check(end))
            time = datetime.datetime.now()
            plus = datetime.timedelta(seconds = end)
            r_time = (time + plus).strftime("%Y-%m-%d %H:%M:%S")
        else:
            r_time = ''

        curs.execute(db_change("insert into rb (block, end, today, blocker, why, band, ongoing, login) values (?, ?, ?, ?, ?, ?, '1', ?)"), [
            name, 
            r_time, 
            now_time, 
            blocker, 
            why, 
            band,
            login
        ])

    conn.commit()

def rd_plus(topic_num, date, name = None, sub = None):
    curs.execute(db_change("select code from rd where code = ?"), [topic_num])
    if curs.fetchall():
        curs.execute(db_change("update rd set date = ? where code = ?"), [date, topic_num])
    else:
        curs.execute(db_change("insert into rd (title, sub, code, date) values (?, ?, ?, ?)"), [name, sub, topic_num, date])

    conn.commit()

def history_plus(title, data, date, ip, send, leng, t_check = '', mode = ''):
    if mode == 'add':
        curs.execute(db_change("select id from history where title = ? order by id + 0 asc limit 1"), [title])
        id_data = curs.fetchall()
        id_data = str(int(id_data[0][0]) - 1) if id_data else '0'
    else:
        curs.execute(db_change("select id from history where title = ? order by id + 0 desc limit 1"), [title])
        id_data = curs.fetchall()
        id_data = str(int(id_data[0][0]) + 1) if id_data else '1'
        
        mode = mode if not re.search('^user:', title) else 'user'

    send = re.sub(r'\(|\)|<|>', '', send)
    send = send[:128] if len(send) > 128 else send
    send = send + ' (' + t_check + ')' if t_check != '' else send

    if mode != 'add' and mode != 'user':
        curs.execute(db_change("select count(*) from rc where type = 'normal'"))
        if curs.fetchall()[0][0] >= 200:
            curs.execute(db_change("select id, title from rc where type = 'normal' order by date asc limit 1"))
            rc_data = curs.fetchall()
            if rc_data:
                curs.execute(db_change('delete from rc where id = ? and title = ? and type = "normal"'), [
                    rc_data[0][0],
                    rc_data[0][1]
                ])
    
        curs.execute(db_change("insert into rc (id, title, date, type) values (?, ?, ?, 'normal')"), [
            id_data,
            title,
            date
        ])
    
    if mode != 'add':
        curs.execute(db_change("select count(*) from rc where type = ?"), [mode])
        if curs.fetchall()[0][0] >= 200:
            curs.execute(db_change("select id, title from rc where type = ? order by date asc limit 1"), [mode])
            rc_data = curs.fetchall()
            if rc_data:
                curs.execute(db_change('delete from rc where id = ? and title = ? and type = ?'), [
                    rc_data[0][0],
                    rc_data[0][1],
                    mode
                ])
    
        curs.execute(db_change("insert into rc (id, title, date, type) values (?, ?, ?, ?)"), [
            id_data,
            title,
            date,
            mode
        ])
            
    curs.execute(db_change("insert into history (id, title, data, date, ip, send, leng, hide, type) values (?, ?, ?, ?, ?, ?, ?, '', ?)"), [
        id_data,
        title,
        data,
        date,
        ip,
        send,
        leng,
        mode
    ])

def leng_check(first, second):
    if first < second:
        all_plus = '+' + str(second - first)
    elif second < first:
        all_plus = '-' + str(first - second)
    else:
        all_plus = '0'

    return all_plus

def number_check(data):
    try:
        int(data)
        return data
    except:
        return '1'

def edit_filter_do(data):
    if admin_check(1) != 1:
        curs.execute(db_change("select plus, plus_t from html_filter where kind = 'regex_filter' and plus != ''"))
        for data_list in curs.fetchall():
            match = re.compile(data_list[0], re.I)
            if match.search(data):
                ban_insert(
                    ip_check(),
                    '0' if data_list[1] == 'X' else data_list[1],
                    'edit filter',
                    None,
                    'tool:edit filter'
                )

                return 1

    return 0

def redirect(data = '/'):
    return flask.redirect(flask.request.host_url[:-1] + data)
    
def get_acl_list(type_d = 'normal'):
    if type_d == 'user':
        return ['', 'user', 'all']
    else:
        return ['', 'all', 'user', 'admin', 'owner', '50_edit', 'email', 'ban', 'before', '30_day', 'ban_admin']

def re_error(data):
    conn.commit()

    if data == '/ban':
        if ban_check() == 1:
            end = '<div id="get_user_info"></div><script>load_user_info("' + ip_check() + '");</script>'
        else:
            end = '<ul class="inside_ul"><li>' + load_lang('authority_error') + '</li></ul>'

        return easy_minify(flask.render_template(skin_check(),
            imp = [load_lang('error'), wiki_set(1), custom(), other2([0, 0])],
            data = '<h2>' + load_lang('error') + '</h2>' + end,
            menu = 0
        )), 401
    else:
        num = int(number_check(data.replace('/error/', '')))
        if num == 1:
            data = load_lang('no_login_error')
        elif num == 2:
            data = load_lang('no_exist_user_error')
        elif num == 3:
            data = load_lang('authority_error')
        elif num == 4:
            data = load_lang('no_admin_block_error')
        elif num == 5:
            data = load_lang('skin_error')
        elif num == 6:
            data = load_lang('same_id_exist_error')
        elif num == 7:
            data = load_lang('long_id_error')
        elif num == 8:
            data = load_lang('id_char_error') + ' <a href="/name_filter">(' + load_lang('id_filter_list') + ')</a>'
        elif num == 9:
            data = load_lang('file_exist_error')
        elif num == 10:
            data = load_lang('password_error')
        elif num == 11:
            data = load_lang('topic_long_error')
        elif num == 12:
            data = load_lang('email_error')
        elif num == 13:
            data = load_lang('recaptcha_error')
        elif num == 14:
            data = load_lang('file_extension_error') + ' <a href="/extension_filter">(' + load_lang('extension_filter_list') + ')</a>'
        elif num == 15:
            data = load_lang('edit_record_error')
        elif num == 16:
            data = load_lang('same_file_error')
        elif num == 17:
            data = load_lang('file_capacity_error') + wiki_set(3)
        elif num == 18:
            data = load_lang('email_send_error')
        elif num == 19:
            data = load_lang('decument_exist_error')
        elif num == 20:
            data = load_lang('password_diffrent_error')
        elif num == 21:
            data = load_lang('edit_filter_error')
        elif num == 22:
            data = load_lang('file_name_error')
        elif num == 23:
            data = load_lang('regex_error')
        elif num == 24:
            curs.execute(db_change("select data from other where name = 'slow_edit'"))
            data = load_lang('fast_edit_error') + curs.fetchall()[0][0]
        elif num == 25:
            data = load_lang('too_many_dec_error')
        elif num == 26:
            data = load_lang('application_not_found')
        elif num == 27:
            data = load_lang("invalid_password_error")
        elif num == 28:
            data = load_lang('watchlist_overflow_error')
        elif num == 29:
            data = load_lang('copyright_disagreed')
        elif num == 30:
            data = load_lang('ie_wrong_callback')
        elif num == 33:
            data = load_lang('restart_fail_error')
        elif num == 34:
            data = load_lang("update_error") + ' <a href="https://github.com/2DU/opennamu">(Github)</a>'
        elif num == 35:
            data = load_lang('same_email_error')
        elif num == 36:
            data = load_lang('input_email_error')
        else:
            data = '???'

        if num == 5:
            get_url = flask.request.path
        
            return easy_minify(flask.render_template(skin_check(),
                imp = [(load_lang('skin_set') if get_url != '/main_skin_set' else load_lang('main_skin_set')), wiki_set(1), custom(), other2([0, 0])],
                data = '' + \
                    '<div id="main_skin_set">' + \
                        '<h2>' + load_lang('error') + '</h2>' + \
                        '<ul class="inside_ul">' + \
                            '<li>' + data + ' <a href="/main_skin_set">(' + load_lang('main_skin_set') + ')</a></li>' + \
                        '</ul>' + \
                    '</div>' + \
                    ('<script>main_css_skin_set();</script>' if get_url == '/main_skin_set' else ''),
                menu = ([['main_skin_set', load_lang('main_skin_set')]] if get_url != '/main_skin_set' else [['skin_set', load_lang('skin_set')]])
            ))
        else:
            return easy_minify(flask.render_template(skin_check(),
                imp = [load_lang('error'), wiki_set(1), custom(), other2([0, 0])],
                data = '<h2>' + load_lang('error') + '</h2><ul class="inside_ul"><li>' + data + '</li></ul>',
                menu = 0
            )), 400


def dev_2fa_totp(key):
    key = base64.b32decode(key)
    counter = math.floor(time.time()/30)
    b = counter.to_bytes(8, "big")
    #print(list(b))
    mac = hmac.new(key, digestmod=hashlib.sha1)
    mac.update(b)
    hmacResult = mac.digest()
    offset = int(hmacResult[19] & 0xf)
    bincode = int(
		(int(hmacResult[offset]&0x7f))<<24 |
		(int(hmacResult[offset+1]&0xff))<<16 |
		(int(hmacResult[offset+2]&0xff))<<8 |
		(int(hmacResult[offset+3] & 0xff)),
	)
    code = str(bincode%1000000)
    return (6-len(code)) * "0" + code

def dev_2fa_new_key():
    secret = os.urandom(20)
    key = base64.b32encode(secret)
    return key.decode("utf-8")

def dev_2fa_qrcode(provider,accountname,key):
    urlstr = urllib.parse.urlencode({"secret":key, "issuer":provider, "algorithm": "SHA1", "digits": "6", "period": "30"})
    #print(urlstr)
    qrstr = "otpauth://totp/{}:{}?{}".format(urllib.parse.quote(provider), urllib.parse.quote(accountname), urlstr)
    qr = segno.make_qr(qrstr, error="H")
    return qr.svg_data_uri(scale=2)
