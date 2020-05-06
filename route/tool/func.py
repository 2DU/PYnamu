import os
import sys
import platform

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
        import sqlite3
        import pymysql
        import hashlib
        import smtplib
        import zipfile
        import shutil
        import threading
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
            if platform.system() == 'Linux':
                ok = os.system('python3 -m pip install --user -r requirements.txt')
                if ok == 0:
                    print('----')
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    raise
            elif platform.system() == 'Windows':
                ok = os.system('python -m pip install --user -r requirements.txt')
                if ok == 0:
                    print('----')
                    os.execl(sys.executable, sys.executable, *sys.argv)
                else:
                    raise
            else:
                print('----')
                print(e)
                raise
        else:
            print('----')
            print(e)
            raise

app_var = json.loads(open('data/app_var.json', encoding='utf8').read())

def load_conn(data):
    global conn
    global curs

    conn = data
    curs = conn.cursor()

    load_conn2(data)

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

        if rep_data:
            smtp_email = ''
            smtp_pass = ''
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
            else: # if smtp_security == 'tls':
                smtp = smtplib.SMTP_SSL(smtp_server, smtp_port)
            
            smtp.login(smtp_email, smtp_pass)

        msg = email.mime.text.MIMEText(data)
        msg['Subject'] = title
        smtp.sendmail(smtp_email, who, msg.as_string())

        smtp.quit()
    except:
        print('----')
        print('Error : Email send error')

def last_change(data):
    json_address = re.sub(r"(((?!\.|\/).)+)\.html$", "set.json", skin_check())
    try:
        json_data = json.loads(open(json_address, encoding='utf8').read())
    except:
        json_data = 0

    if json_data != 0:
        for j_data in json_data:
            if "class" in json_data[j_data]:
                if "require" in json_data[j_data]:
                    re_data = re.compile("<((?:" + j_data + ")( (?:(?!>).)*)?)>")
                    s_data = re_data.findall(data)
                    for i_data in s_data:
                        e_data = 0

                        for j_i_data in json_data[j_data]["require"]:
                            re_data_2 = re.compile("( |^)" + j_i_data + " *= *[\'\"]" + json_data[j_data]["require"][j_i_data] + "[\'\"]")
                            if not re_data_2.search(i_data[1]):
                                re_data_2 = re.compile("( |^)" + j_i_data + "=" + json_data[j_data]["require"][j_i_data] + "(?: |$)")
                                if not re_data_2.search(i_data[1]):
                                    e_data = 1

                                    break

                        if e_data == 0:
                            re_data_3 = re.compile("<" + i_data[0] + ">")
                            data = re_data_3.sub("<" + i_data[0] + " class=\"" + json_data[j_data]["class"] + "\">", data)
                else:
                    re_data = re.compile("<(?P<in>" + j_data + "(?: (?:(?!>).)*)?)>")
                    data = re_data.sub("<\g<in> class=\"" + json_data[j_data]["class"] + "\">", data)

    return data

def easy_minify(data, tool = None):
    return last_change(data)

def render_set(title = '', data = '', num = 0, s_data = 0, include = None):
    if acl_check(title, 'render') == 1:
        return 'HTTP Request 401.3'
    elif s_data == 1:
        return data
    else:
        if data != None:
            return render_do(title, data, num, include)
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
        change_topic = curs.fetchall()
        for i in change_topic:
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
        change_band = curs.fetchall()
        for i in change_band:
            curs.execute(db_change("update ban set block = ?, band = 'regex' where block = ? and band = 'O'"), [
                '^' + i[0].replace('.', '\\.'),
                i[0]
            ])

        curs.execute(db_change("select block from rb where band = 'O'"))
        change_band = curs.fetchall()
        for i in change_band:
            curs.execute(db_change("update rb set block = ?, band = 'regex' where block = ? and band = 'O'"), [
                '^' + i[0].replace('.', '\\.'),
                i[0]
            ])
            
    if ver_num < 3184400:
        curs.execute(db_change('delete from cache_data'))

    conn.commit()

    print('Update pass')

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
        for i in [['smtp_server', 'imap.google.com'], ['smtp_port', '587'], ['smtp_security', 'tls']]:
            curs.execute(db_change("insert into other (name, data) values (?, ?)"), [i[0], i[1]])

def pw_encode(data, data2 = '', type_d = ''):
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

    if pw_encode(data = data, type_d = set_data) == data2:
        re_data = 1
    else:
        re_data = 0

    if db_data[0][0] != set_data and re_data == 1 and id_d != '':
        curs.execute(db_change("update user set pw = ?, encode = ? where id = ?"), [pw_encode(data), db_data[0][0], id_d])

    return re_data

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
                        '<hr class=\"main_hr\">' + \
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

def load_lang(data, num = 2, safe = 0):
    if num == 1:
        curs.execute(db_change("select data from other where name = 'language'"))
        rep_data = curs.fetchall()

        json_data = open(os.path.join('language', rep_data[0][0] + '.json'), encoding='utf8').read()
        lang = json.loads(json_data)

        if data in lang:
            if safe == 1:
                return lang[data]
            else:
                return html.escape(lang[data])
        else:
            return html.escape(data + ' (M)')
    else:
        curs.execute(db_change('select data from user_set where name = "lang" and id = ?'), [ip_check()])
        rep_data = curs.fetchall()
        if rep_data:
            try:
                json_data = open(os.path.join('language', rep_data[0][0] + '.json'), encoding='utf8').read()
                lang = json.loads(json_data)
            except:
                return load_lang(data, 1, safe)

            if data in lang:
                if safe == 1:
                    return lang[data]
                else:
                    return html.escape(lang[data])
            else:
                return load_lang(data, 1, safe)
        else:
            return load_lang(data, 1, safe)

def load_oauth(provider):
    oauth_supported = ["discord", "facebook", "naver", "kakao"]
    if(provider == '_README'):
        return { "support" : oauth_supported }
    else:
        try:
            oauth = json.loads(open(app_var['path_oauth_setting'], encoding='utf8').read())
        except:
            return_json_data = '{ "publish_url" : "", '

            for i in range(len(oauth_supported)):
                return_json_data += '"' + oauth_supported[i] + '" : { '
                for j in range(2):
                    if j == 0:
                        load_target = 'id'
                    elif j == 1:
                        load_target = 'secret'

                    return_json_data += '"client_' + load_target  + '" : ""' + (',' if j == 0 else '')

                return_json_data += ' }'

                try:
                    _ = oauth_supported[i + 1]

                    return_json_data += ', '
                except:
                    return_json_data += ' }'

            with open(app_var['path_oauth_setting'], 'w', encoding='utf-8') as f:
                f.write(return_json_data)

            oauth = json.loads(open(app_var['path_oauth_setting'], encoding='utf8').read())

        return oauth[provider]

def update_oauth(provider, target, content):
    oauth = json.loads(open(app_var['path_oauth_setting'], encoding='utf8').read())
    oauth[provider][target] = content

    with open(app_var['path_oauth_setting'], 'w', encoding='utf8') as f:
        f.write(json.dumps(oauth, sort_keys = True, indent = 4))

    return 'Done'

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

    return data + '<hr class=\"main_hr\">'

def ip_warring():
    if ip_or_user() != 0:
        curs.execute(db_change('select data from other where name = "no_login_warring"'))
        data = curs.fetchall()
        if data and data[0][0] != '':
            text_data = '<span>' + data[0][0] + '</span><hr class=\"main_hr\">'
        else:
            text_data = '<span>' + load_lang('no_login_warring') + '</span><hr class=\"main_hr\">'
    else:
        text_data = ''

    return text_data

def skin_check(set_n = 0):
    skin = 'marisa'

    curs.execute(db_change('select data from other where name = "skin"'))
    skin_exist = curs.fetchall()
    if skin_exist and skin_exist[0][0] != '':
        if os.path.exists(os.path.abspath('./views/' + skin_exist[0][0] + '/index.html')) == 1:
            skin = skin_exist[0][0]

    curs.execute(db_change('select data from user_set where name = "skin" and id = ?'), [ip_check()])
    skin_exist = curs.fetchall()
    if skin_exist and skin_exist[0][0] != '':
        if os.path.exists(os.path.abspath('./views/' + skin_exist[0][0] + '/index.html')) == 1:
            skin = skin_exist[0][0]

    if set_n == 0:
        return './views/' + skin + '/index.html'
    else:
        return skin

def next_fix(link, num, page, end = 50):
    list_data = ''

    if num == 1:
        if len(page) == end:
            list_data += '<hr class=\"main_hr\"><a href="' + link + str(num + 1) + '">(' + load_lang('next') + ')</a>'
    elif len(page) != end:
        list_data += '<hr class=\"main_hr\"><a href="' + link + str(num - 1) + '">(' + load_lang('previous') + ')</a>'
    else:
        list_data += '<hr class=\"main_hr\"><a href="' + link + str(num - 1) + '">(' + load_lang('previous') + ')</a> <a href="' + link + str(num + 1) + '">(' + load_lang('next') + ')</a>'

    return list_data

def other2(data):
    for _ in range(0, 3 - len(data)):
        data += ['']

    req_list = ''
    main_css_ver = 44

    if  not 'main_css_load' in flask.session or \
        not 'main_css_ver' in flask.session or \
        flask.session['main_css_ver'] != main_css_ver:
        for i_data in os.listdir(os.path.join("views", "main_css", "css")):
            req_list += '<link rel="stylesheet" href="/views/main_css/css/' + i_data + '?ver=' + str(main_css_ver) + '">'

        for i_data in os.listdir(os.path.join("views", "main_css", "js")):
            req_list += '<script src="/views/main_css/js/' + i_data + '?ver=' + str(main_css_ver) + '"></script>'

        flask.session['main_css_load'] = req_list
        flask.session['main_css_ver'] = main_css_ver
    else:
        req_list = flask.session['main_css_load']

    data = data[0:2] + ['', '''
        <link   rel="stylesheet"
                href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/styles/default.min.css">
        <link   rel="stylesheet"
                href="https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/katex.min.css"
                integrity="sha384-dbVIfZGuN1Yq7/1Ocstc1lUEm+AT+/rCkibIcC/OmWo5f0EA48Vf8CytHzGrSwbQ"
                crossorigin="anonymous">
        <script src="https://cdn.jsdelivr.net/npm/katex@0.10.1/dist/katex.min.js"
                integrity="sha384-2BKqo+exmr9su6dir+qCw08N2ZKRucY4PrGQPPWU1A7FtlCGjmEGFqXCv5nyM5Ij"
                crossorigin="anonymous"></script>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/9.18.1/highlight.min.js"></script>
    ''' + req_list + '<script>window.addEventListener(\'DOMContentLoaded\', function() { main_css_skin_load(); });</script>'] + data[2:]

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
        data_list = []
        skin_name = skin_check(1)

        curs.execute(db_change('select data from other where name = ?'), ['name'])
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            data_list += [db_data[0][0]]
        else:
            data_list += ['Wiki']

        curs.execute(db_change('select data from other where name = "license"'))
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            data_list += [db_data[0][0]]
        else:
            data_list += ['ARR']

        data_list += ['', '']

        curs.execute(db_change('select data from other where name = "logo" and coverage = ?'), [skin_name])
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            data_list += [db_data[0][0]]
        else:
            curs.execute(db_change('select data from other where name = "logo" and coverage = ""'))
            db_data = curs.fetchall()
            if db_data and db_data[0][0] != '':
                data_list += [db_data[0][0]]
            else:
                data_list += [data_list[0]]

        head_data = ''

        curs.execute(db_change("select data from other where name = 'head' and coverage = ''"))
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            head_data += db_data[0][0]

        curs.execute(db_change("select data from other where name = 'head' and coverage = ?"), [skin_name])
        db_data = curs.fetchall()
        if db_data and db_data[0][0] != '':
            head_data += db_data[0][0]
            
        data_list += [head_data]

        return data_list

    if num == 2:
        var_data = 'FrontPage'

        curs.execute(db_change('select data from other where name = "frontpage"'))
    elif num == 3:
        var_data = '2'

        curs.execute(db_change('select data from other where name = "upload"'))

    db_data = curs.fetchall()
    if db_data and db_data[0][0] != '':
        return db_data[0][0]
    else:
        return var_data

def admin_check(num = None, what = None, name = ''):
    if name == '':
        ip = ip_check()
    else:
        ip = name

    curs.execute(db_change("select acl from user where id = ?"), [ip])
    user = curs.fetchall()
    if user:
        reset = 0

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
                    curs.execute(db_change("insert into re_admin (who, what, time) values (?, ?, ?)"), [ip, what, get_time()])
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

    if ip_or_user(raw_ip) != 0:
        curs.execute(db_change("select data from other where name = 'ip_view'"))
        data = curs.fetchall()
        if data and data[0][0] != '':
            if re.search(r'\.', raw_ip):
                ip = re.sub(r'\.([^.]*)\.([^.]*)$', '.*.*', raw_ip)
            else:
                ip = re.sub(r':([^:]*):([^:]*)$', ':*:*', raw_ip)

            if not admin_check(1):
                hide = 1
        else:
            ip = raw_ip
    else:
        if type_d == 0:
            curs.execute(db_change("select title from data where title = ?"), ['user:' + raw_ip])
            if curs.fetchall():
                ip = '<a href="/w/' + url_pas('user:' + raw_ip) + '">' + raw_ip + '</a>'
            else:
                ip = '<a id="not_thing" href="/w/' + url_pas('user:' + raw_ip) + '">' + raw_ip + '</a>'

            if admin_check('all', None, raw_ip) == 1:
                ip = '<b>' + ip + '</b>'
        else:
            ip = raw_ip

    if type_d == 0:
        if ban_check(raw_ip) == 1:
            ip = '<s>' + ip + '</s>'

        if hide == 0:
            ip += ' <a href="/tool/' + url_pas(raw_ip) + '">(' + load_lang('tool') + ')</a>'

    return ip

def custom():
    if 'head' in flask.session:
        if len(re.findall('<', flask.session['head'])) % 2 != 1:
            user_head = flask.session['head']
        else:
            user_head = ''
    else:
        user_head = ''

    ip = ip_check()
    if ip_or_user(ip) == 0:
        user_icon = 1
        user_name = ip

        curs.execute(db_change('select data from user_set where name = "email" and id = ?'), [ip])
        data = curs.fetchall()
        if data:
            email = data[0][0]
        else:
            email = ''

        if admin_check('all') == 1:
            user_admin = '1'
            user_acl_list = []

            curs.execute(db_change("select acl from user where id = ?"), [ip])
            curs.execute(db_change('select acl from alist where name = ?'), [curs.fetchall()[0][0]])
            user_acl = curs.fetchall()
            for i in user_acl:
                user_acl_list += [i[0]]

            if user_acl != []:
                user_acl_list = user_acl_list
            else:
                user_acl_list = '0'
        else:
            user_admin = '0'
            user_acl_list = '0'

        curs.execute(db_change("select count(name) from alarm where name = ?"), [ip])
        count = curs.fetchall()
        if count:
            user_notice = str(count[0][0])
        else:
            user_notice = '0'
    else:
        user_icon = 0
        user_name = load_lang('user')
        email = ''
        user_admin = '0'
        user_acl_list = '0'
        user_notice = '0'

    curs.execute(db_change("select title from rd where title = ? and stop = ''"), ['user:' + ip])
    if curs.fetchall():
        user_topic = '1'
    else:
        user_topic = '0'

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

def load_skin(data = '', set_n = 0):
    skin_return_data = ''
    system_file = ['main_css']

    if data == '':
        ip = ip_check()

        curs.execute(db_change('select data from user_set where name = "skin" and id = ?'), [ip])
        data = curs.fetchall()

        if not data:
            curs.execute(db_change('select data from other where name = "skin"'))
            data = curs.fetchall()
            if not data or data[0][0] == '':
                data = [['marisa']]

        if set_n == 0:
            for skin_data in os.listdir(os.path.abspath('views')):
                if not skin_data in system_file:
                    if data[0][0] == skin_data:
                        skin_return_data = '<option value="' + skin_data + '">' + skin_data + '</option>' + skin_return_data
                    else:
                        skin_return_data += '<option value="' + skin_data + '">' + skin_data + '</option>'
        else:
            skin_return_data = []
            for skin_data in os.listdir(os.path.abspath('views')):
                if not skin_data in system_file:
                    if data[0][0] == skin_data:
                        skin_return_data = [skin_data] + skin_return_data
                    else:
                        skin_return_data += [skin_data]
    else:
        if set_n == 0:
            for skin_data in os.listdir(os.path.abspath('views')):
                if not skin_data in system_file:
                    if data == skin_data:
                        skin_return_data = '<option value="' + skin_data + '">' + skin_data + '</option>' + skin_return_data
                    else:
                        skin_return_data += '<option value="' + skin_data + '">' + skin_data + '</option>'
        else:
            skin_return_data = []
            for skin_data in os.listdir(os.path.abspath('views')):
                if not skin_data in system_file:
                    if data == skin_data:
                        skin_return_data = [skin_data] + skin_return_data
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

def tool_acl_check(tool = None):
    ip = ip_check()
    acl_data = None

    curs.execute(db_change("select acl from tool_acl where tool = 'all'"))
    acl_data = curs.fetchall()

    if tool != None:
        curs.execute(db_change("select acl from tool_acl where tool = ?"), [tool])
        tool_acl_data = curs.fetchall()
        if tool_acl_data and tool_acl_data[0][0]:
            acl_data = tool_acl_data

    if acl_data and acl_data[0][0] != 'normal':
        if acl_data[0][0] == 'user':
            if ip_or_user(ip) == 1:
                return 1

        if acl_data[0][0] == 'admin':
            if ip_or_user(ip) == 1:
                return 1

            if admin_check(1) != 1:
                return 1

        if acl_data[0][0] == '50_edit':
            if ip_or_user(ip) == 1:
                return 1

            curs.execute(db_change("select count(title) from history where ip = ?"), [ip])
            count = curs.fetchall()
            if count:
                count = count[0][0]
            else:
                count = 0

            if count < 50:
                return 1

        if acl_data[0][0] == 'email':
            if ip_or_user(ip) == 1:
                return 1

            curs.execute(db_change("select data from user_set where id = ? and name = 'email'"), [ip])
            email = curs.fetchall()
            if not email:
                return 1

        if acl_data[0][0] == 'owner':
            if admin_check() != 1:
                return 1
    return 0

def acl_check(name = 'test', tool = '', topic_num = '1'):
    ip = ip_check()
    get_ban = ban_check()
    
    if name:
        acl_c = re.search(r"^user:((?:(?!\/).)*)", name)
    else:
        acl_c = None

    if tool == '' and acl_c:
        acl_n = acl_c.groups()

        if get_ban == 1:
            return 1

        if admin_check(5) == 1:
            return 0

        curs.execute(db_change("select decu from acl where title = ?"), ['user:' + acl_n[0]])
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

    if tool == '' or tool == 'edit_req':
        if acl_check(name, 'render') == 1:
            return 1
    
    if tool == '':
        end = 3
    elif tool == 'topic':
        if not name:
            curs.execute(db_change("select title from rd where code = ?"), [topic_num])
            topic_data = curs.fetchall()
            if topic_data:
                name = topic_data[0][0]
            else:
                name = 'test'

        end = 3
    elif tool == 'render':
        end = 2
    else:
        end = 1

    for i in range(0, end):
        if tool == '':
            if i == 0:
                curs.execute(db_change("select decu from acl where title = ?"), [name])
            elif i == 1:
                curs.execute(db_change('select data from other where name = "edit"'))
            else:
                curs.execute(db_change("select view from acl where title = ?"), [name])

            num = 5
        elif tool == 'topic':
            if i == 0 and topic_num:
                curs.execute(db_change("select acl from rd where code = ?"), [topic_num])
            elif i == 1:
                curs.execute(db_change("select dis from acl where title = ?"), [name])
            else:
                curs.execute(db_change('select data from other where name = "discussion"'))

            num = 3
        elif tool == 'upload':
            curs.execute(db_change("select data from other where name = 'upload_acl'"))

            num = 5
        elif tool == 'many_upload':
            curs.execute(db_change("select data from other where name = 'many_upload_acl'"))

            num = 5
        elif tool == 'edit_req':
            curs.execute(db_change("select data from other where name = 'edit_req_acl'"))

            num = 5
        else:
            if i == 0:
                curs.execute(db_change("select view from acl where title = ?"), [name])
            if i == 1:
                curs.execute(db_change("select data from other where name = 'all_view_acl'"))

            num = 5

        acl_data = curs.fetchall()
        if (not acl_data and i == (end - 1)) and get_ban == 1 and tool != 'render':
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
                        curs.execute(db_change("select count(title) from history where ip = ?"), [ip])
                        count = curs.fetchall()
                        count = count[0][0] if count else 0
                        if count >= 50:
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

            return 1
        else:
            if i == (end - 1):
                if tool == 'topic':
                    if topic_num:
                        curs.execute(db_change("select title from rd where code = ? and stop != ''"), [topic_num])
                        if curs.fetchall():
                            if admin_check(3, 'topic (code ' + topic_num + ')') == 1:
                                return 0
                        else:
                            return 0
                    else:
                        return 0
                else:
                    return 0

    return 1

def ban_check(ip = None, tool = None):
    if not ip:
        ip = ip_check()

    if admin_check(None, None, ip) == 1:
        return 0

    curs.execute(db_change("delete from ban where (end < ? and end like '2%')"), [get_time()])
    conn.commit()

    curs.execute(db_change("select login, block from ban where ((end > ? and end like '2%') or end = '') and band = 'regex'"), [get_time()])
    regex_d = curs.fetchall()
    for test_r in regex_d:
        g_regex = re.compile(test_r[1])
        if g_regex.search(ip):
            if tool and tool == 'login':
                if test_r[0] != 'O':
                    return 1
            else:
                return 1

    curs.execute(db_change("select login from ban where ((end > ? and end like '2%') or end = '') and block = ? and band = ''"), [get_time(), ip])
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

    if type_d:
        band = type_d
    else:
        band = ''

    curs.execute(db_change("delete from ban where (end < ? and end like '2%')"), [get_time()])

    curs.execute(db_change("select block from ban where ((end > ? and end like '2%') or end = '') and block = ? and band = ?"), [get_time(), name, band])
    if curs.fetchall():
        curs.execute(db_change("insert into rb (block, end, today, blocker, why, band) values (?, ?, ?, ?, ?, ?)"), [
            name,
            'release',
            now_time,
            blocker,
            '',
            band
        ])
        curs.execute(db_change("delete from ban where block = ? and band = ?"), [name, band])
    else:
        if login != '':
            login = 'O'
        else:
            login = ''

        if end != '0':
            end = int(number_check(end))

            time = datetime.datetime.now()
            plus = datetime.timedelta(seconds = end)
            r_time = (time + plus).strftime("%Y-%m-%d %H:%M:%S")
        else:
            r_time = ''

        curs.execute(db_change("insert into rb (block, end, today, blocker, why, band) values (?, ?, ?, ?, ?, ?)"), [
            name, 
            r_time, 
            now_time, 
            blocker, 
            why, 
            band
        ])
        curs.execute(db_change("insert into ban (block, end, why, band, login) values (?, ?, ?, ?, ?)"), [
            name, 
            r_time, 
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

def history_plus(title, data, date, ip, send, leng, t_check = '', d_type = ''):
    curs.execute(db_change("select id from history where title = ? and type = '' order by id + 0 desc limit 1"), [title])
    id_data = curs.fetchall()
    id_data = str(int(id_data[0][0]) + 1) if id_data else '1'

    if d_type != 'req':
        curs.execute(db_change("select title from history where title = ? and id = ? and type = 'req'"), [title, id_data])
        if curs.fetchall():
            curs.execute(db_change("update history set type = 'req_close' where title = ? and id = ? and type = 'req'"), [
                title,
                id_data
            ])

    send = re.sub(r'\(|\)|<|>', '', send)
    send = send[:128] if len(send) > 128 else send
    send = send + ' (' + t_check + ')' if t_check != '' else send

    curs.execute(db_change("insert into history (id, title, data, date, ip, send, leng, hide, type) values (?, ?, ?, ?, ?, ?, ?, '', ?)"), [
        id_data,
        title,
        data,
        date,
        ip,
        send,
        leng,
        d_type
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
        curs.execute(db_change("select regex, sub from filter where regex != ''"))
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
    return flask.redirect(data)

def get_acl_list(type_d = None):
    acl_data = ['', 'all', 'user', 'admin', 'owner', '50_edit', 'email', 'ban']
    if type_d:
        if type_d == 'user':
            acl_data = ['', 'user', 'all']

    return acl_data

def re_error(data):
    conn.commit()

    if data == '/ban':
        if ban_check() == 1:
            end = '<div id="get_user_info"></div><script>load_user_info("' + ip_check() + '");</script>'
        else:
            end = load_lang('authority_error')

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
            slow_data = curs.fetchall()
            data = load_lang('fast_edit_error') + slow_data[0][0]
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
        else:
            data = '???'

        if num == 5:
            get_url = flask.request.path
        
            return easy_minify(flask.render_template(skin_check(),
                imp = [(load_lang('skin_set') if get_url != '/main_skin_set' else load_lang('main_skin_set')), wiki_set(1), custom(), other2([0, 0])],
                data = '' + \
                    '<div id="main_skin_set">' + \
                        '<h2>' + load_lang('error') + '</h2>' + \
                        '<ul>' + \
                            '<li>' + data + ' <a href="/main_skin_set">(' + load_lang('main_skin_set') + ')</a></li>' + \
                        '</ul>' + \
                    '</div>' + \
                    ('<script>window.addEventListener(\'DOMContentLoaded\', function() { main_css_skin_set(); });</script>' if get_url == '/main_skin_set' else ''),
                menu = ([['main_skin_set', load_lang('main_skin_set')]] if get_url != '/main_skin_set' else [['skin_set', load_lang('skin_set')]])
            ))
        else:
            return easy_minify(flask.render_template(skin_check(),
                imp = [load_lang('error'), wiki_set(1), custom(), other2([0, 0])],
                data = '<h2>' + load_lang('error') + '</h2><ul><li>' + data + '</li></ul>',
                menu = 0
            )), 400
