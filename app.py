﻿from bottle import *
from bottle.ext import beaker
import json
import sqlite3
import bcrypt
import os
import difflib

try:
    json_data = open('set.json').read()
    set_data = json.loads(json_data)
except:
    new_json = []

    print('DB 이름 : ', end = '')
    new_json += [input()]

    print('포트 : ', end = '')
    new_json += [input()]

    with open("set.json", "w") as f:
        f.write('{ "db" : "' + new_json[0] + '", "port" : "' + new_json[1] + '" }')
    
    json_data = open('set.json').read()
    set_data = json.loads(json_data)

conn = sqlite3.connect(set_data['db'] + '.db')
curs = conn.cursor()

session_opts = {
    'session.type': 'dbm',
    'session.data_dir': './app_session/',
    'session.auto': 1
}

app = beaker.middleware.SessionMiddleware(app(), session_opts)

from func import *

BaseRequest.MEMFILE_MAX = 1000 ** 4

r_ver = '2.3.6'

# 스킨 불러오기 부분
try:
    curs.execute('select data from other where name = "skin"')
    skin_exist = curs.fetchall()
    if(skin_exist):
        if(os.path.exists(os.path.abspath('./views/' + skin_exist[0][0] + '/index.tpl')) == 1):
            TEMPLATE_PATH.insert(0, './views/' + skin_exist[0][0] + '/')
        else:
            TEMPLATE_PATH.insert(0, './views/acme/')
    else:
        TEMPLATE_PATH.insert(0, './views/acme/')
except:
    TEMPLATE_PATH.insert(0, './views/acme/')

# 테이블 생성 부분
try:
    curs.execute("select title from data limit 1")

    try:
        curs.execute('select new from move limit 1')
    except:
        curs.execute("create table move(origin text, new text, date text, who text, send text)")
        print('move 테이블 생성')

    try:
        curs.execute('select name from alarm limit 1')
    except:
        curs.execute("create table alarm(name text, data text, date text)")
        print('alarm 테이블 생성')

    try:
        curs.execute('select name from ua_d limit 1')
    except:
        curs.execute("create table ua_d(name text, ip text, ua text, today text, sub text)")
        print('ua_d 테이블 생성')

    try:
        curs.execute('select user, ip, today from login')
        lo_d = curs.fetchall()
        for m_lo in lo_d:
            curs.execute("insert into ua_d (name, ip, ua, today, sub) values (?, ?, '', ?, '')", [m_lo[0], m_lo[1], m_lo[2]])

        curs.execute("drop table login")
        print('login 테이블 삭제')
    except:
        pass

    try:
        curs.execute('select title, cat from cat')
        lo_d = curs.fetchall()
        for m_lo in lo_d:
            curs.execute("insert into back (title, link, type) values (?, ?, 'cat')", [m_lo[0], m_lo[1]])

        curs.execute("drop table cat")
        print('cat 테이블 삭제')
    except:
        pass

    conn.commit()
except:
    pass

# 이미지 폴더 생성
if(not os.path.exists('image')):
    os.makedirs('image')
    
# 스킨 폴더 생성
if(not os.path.exists('views')):
    os.makedirs('views')
    
@route('/setup', method=['GET', 'POST'])
def setup():
    try:
        curs.execute("select title from data limit 1")
    except:
        try:
            curs.execute("create table data(title text, data text, acl text)")
        except:
            pass

        try:
            curs.execute("create table history(id text, title text, data text, date text, ip text, send text, leng text)")
        except:
            pass

        try:
            curs.execute("create table rd(title text, sub text, date text)")
        except:
            pass

        try:
            curs.execute("create table user(id text, pw text, acl text)")
        except:
            pass

        try:
            curs.execute("create table ban(block text, end text, why text, band text)")
        except:
            pass

        try:
            curs.execute("create table topic(id text, title text, sub text, data text, date text, ip text, block text, top text)")
        except:
            pass

        try:
            curs.execute("create table stop(title text, sub text, close text)")
        except:
            pass

        try:
            curs.execute("create table rb(block text, end text, today text, blocker text, why text)")
        except:
            pass

        try:
            curs.execute("create table back(title text, link text, type text)")
        except:
            pass

        try:
            curs.execute("create table hidhi(title text, re text)")
        except:
            pass

        try:
            curs.execute("create table agreedis(title text, sub text)")
        except:
            pass

        try:
            curs.execute("create table custom(user text, css text)")
        except:
            pass

        try:
            curs.execute("create table other(name text, data text)")
        except:
            pass

        try:
            curs.execute("create table alist(name text, acl text)")
            curs.execute("insert into alist (name, acl) values ('소유자', 'owner')")
        except:
            pass

        try:
            curs.execute("create table re_admin(who text, what text, time text)")
        except:
            pass

        try:
            curs.execute("create table move(origin text, new text, date text, who text, send text)")
        except:
            pass

        try:
            curs.execute("create table alarm(name text, data text, date text)")
        except:
            pass

        try:
            curs.execute("create table ua_d(name text, ip text, ua text, today text, sub text)")
        except:
            pass

        conn.commit()

    return(redirect('/'))

@route('/del_alarm')
def del_alarm():
    curs.execute("delete from alarm where name = ?", [ip_check()])
    conn.commit()

    return(redirect('/alarm'))

@route('/alarm')
def alarm():
    ip = ip_check()
    if(re.search('(?:\.|:)', ip)):
        return(redirect('/login'))    

    da = '<ul>'    
    curs.execute("select data, date from alarm where name = ? order by date desc", [ip])
    dt = curs.fetchall()
    if(dt):
        da = '<a href="/del_alarm">(알람 삭제)</a><br><br>' + da

        for do in dt:
            da += '<li>' + do[0] + ' / ' + do[1] + '</li>'
    else:
        da += '<li>알림이 없습니다.</li>'
    da += '</ul>'

    return(
        html_minify(
            template('index', 
                imp = ['알림', wiki_set(1), custom(), other2([0, 0])],
                data = da,
                menu = [['user', '사용자']]
            )
        )
    )

@route('/edit_set', method=['POST', 'GET'])
@route('/edit_set/<num:int>', method=['POST', 'GET'])
def edit_set(num = 0):
    if(num != 0 and admin_check(None, 'edit_set') != 1):
        return(redirect('/ban'))

    if(num == 0):
        li_list = ['기본 설정', '문구 관련', '전역 CSS', '전역 JS']
        x = 0
        li_data = ''
        for li in li_list:
            x += 1
            li_data += '<li>' + str(x) + '. <a href="/edit_set/' + str(x) + '">' + li + '</a></li>'

        return(
            html_minify(
                template('index', 
                    imp = ['설정 편집', wiki_set(1), custom(), other2([0, 0])],
                    data = '<ul>' + li_data + '</ul>',
                    menu = [['manager', '관리자']]
                )
            )
        )
    elif(num == 1):
        if(request.method == 'POST'):
            curs.execute("update other set data = ? where name = ?", [request.forms.name, 'name'])
            curs.execute("update other set data = ? where name = ?", [request.forms.logo, 'logo'])
            curs.execute("update other set data = ? where name = 'frontpage'", [request.forms.frontpage])
            curs.execute("update other set data = ? where name = 'license'", [request.forms.license])
            curs.execute("update other set data = ? where name = 'upload'", [request.forms.upload])
            curs.execute("update other set data = ? where name = 'skin'", [request.forms.skin])
            curs.execute("update other set data = ? where name = 'edit'", [request.forms.edit])
            curs.execute("update other set data = ? where name = 'reg'", [request.forms.reg])
            conn.commit()

            return(redirect('/edit_set/1'))
        else:
            i_list = ['name', 'logo', 'frontpage', 'license', 'upload', 'skin', 'edit', 'reg']
            n_list = ['무명위키', '', '위키:대문', 'CC 0', '2', '', 'normal', '']
            d_list = []
            
            x = 0
            for i in i_list:
                curs.execute('select data from other where name = ?', [i])
                sql_d = curs.fetchall()
                if(sql_d):
                    d_list += [sql_d[0][0]]
                else:
                    curs.execute('insert into other (name, data) values (?, ?)', [i, n_list[x]])
                    d_list += [n_list[x]]

                x += 1
            conn.commit()

            div = ''
            if(d_list[6] == 'login'):
                div += '<option value="login">가입자</option>'
                div += '<option value="normal">일반</option>'
                div += '<option value="admin">관리자</option>'
            elif(d_list[5] == 'admin'):
                div += '<option value="admin">관리자</option>'
                div += '<option value="login">가입자</option>'
                div += '<option value="normal">일반</option>'
            else:
                div += '<option value="normal">일반</option>'
                div += '<option value="admin">관리자</option>'
                div += '<option value="login">가입자</option>'

            if(d_list[7]):
                ch_1 = 'checked="checked"'
            else:
                ch_1 = ''

            return(
                html_minify(
                    template('index', 
                        imp = ['기본 설정', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <span>위키 이름 (기본 : 무명위키)</span> \
                                    <br> \
                                    <br> \
                                    <input placeholder="위키 이름" style="width: 100%;" type="text" name="name" value="' + html.escape(d_list[0]) + '"> \
                                    <br> \
                                    <br> \
                                    <span>로고 HTML (있으면 이름 대신 로고 사용)</span> \
                                    <br> \
                                    <br> \
                                    <input placeholder="로고" style="width: 100%;" type="text" name="logo" value="' + html.escape(d_list[1]) + '"> \
                                    <br> \
                                    <br> \
                                    <span>시작 페이지 (기본 : 위키:대문)</span> \
                                    <br> \
                                    <br> \
                                    <input placeholder="시작 페이지" style="width: 100%;" type="text" name="frontpage" value="' + html.escape(d_list[2]) + '"> \
                                    <br> \
                                    <br> \
                                    <span>라이선스 (기본 : CC 0)</span> \
                                    <br> \
                                    <br> \
                                    <input placeholder="라이선스" style="width: 100%;" type="text" name="license" value="' + html.escape(d_list[3]) + '"> \
                                    <br> \
                                    <br> \
                                    <span>파일 용량 한도 (기본 : 2)</span> \
                                    <br> \
                                    <br> \
                                    <input placeholder="파일 용량 한도" style="width: 100%;" type="text" name="upload" value="' + html.escape(d_list[4]) + '"> \
                                    <br> \
                                    <br> \
                                    <span>스킨 (기본 : acme) (재시작 필요)</span> \
                                    <br> \
                                    <br> \
                                    <input placeholder="스킨" style="width: 100%;" type="text" name="skin" value="' + html.escape(d_list[5]) + '"> \
                                    <br> \
                                    <br> \
                                    <span>기본 ACL 설정 (기본 : 일반)</span> \
                                    <br> \
                                    <br> \
                                    <select name="edit"> \
                                        ' + div + ' \
                                    </select> \
                                    <br> \
                                    <br> \
                                    <input type="checkbox" name="reg" ' + ch_1 + '> 가입불가 \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">저장</button> \
                                </form>',
                        menu = [['edit_set', '설정 편집']]
                    )
                )
            )
    elif(num == 2):
        if(request.method == 'POST'):
            curs.execute("update other set data = ? where name = ?", [request.forms.contract, 'contract'])
            conn.commit()

            return(redirect('/edit_set/2'))
        else:
            i_list = ['contract']
            n_list = ['']
            d_list = []
            
            x = 0
            for i in i_list:
                curs.execute('select data from other where name = ?', [i])
                sql_d = curs.fetchall()
                if(sql_d):
                    d_list += [sql_d[0][0]]
                else:
                    curs.execute('insert into other (name, data) values (?, ?)', [i, n_list[x]])
                    d_list += [n_list[x]]

                x += 1
            conn.commit()

            return(
                html_minify(
                    template('index', 
                        imp = ['문구 관련', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <span>가입 약관</span> \
                                    <br> \
                                    <br> \
                                    <input placeholder="가입 약관" style="width: 100%;" type="text" name="contract" value="' + html.escape(d_list[0]) + '"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">저장</button> \
                                </form>',
                        menu = [['edit_set', '설정 편집']]
                    )
                )
            )
    elif(num == 3):
        session = request.environ.get('beaker.session')
        if(request.method == 'POST'):
            curs.execute("select name from other where name = 'css'")
            if(curs.fetchall()):
                curs.execute("update other set data = ? where name = 'css'", [request.forms.content])
            else:
                curs.execute("insert into other (name, data) values ('css', ?)", [request.forms.content])
            conn.commit()

            return(redirect('/edit_set/3'))
        else:
            curs.execute("select data from other where name = 'css'")
            css = curs.fetchall()
            if(css):
                data = css[0][0]
            else:
                data = ''

            return(
                html_minify(
                    template('index', 
                        imp = ['전역 CSS', wiki_set(1), custom(), other2([0, 0])],
                        data =  '<form method="post"> \
                                    <textarea rows="30" cols="100" name="content">'\
                                        + html.escape(data) + \
                                    '</textarea> \
                                    <br> \
                                    <br> \
                                    <div class="form-actions"> \
                                        <button class="btn btn-primary" type="submit">저장</button> \
                                    </div> \
                                </form>',
                        menu = [['edit_set', '설정 편집']]
                    )
                )
            )
    elif(num == 4):
        session = request.environ.get('beaker.session')
        if(request.method == 'POST'):
            curs.execute("select name from other where name = 'js'")
            if(curs.fetchall()):
                curs.execute("update other set data = ? where name = 'js'", [request.forms.content])
            else:
                curs.execute("insert into other (name, data) values ('js', ?)", [request.forms.content])
            conn.commit()

            return(redirect('/edit_set/4'))
        else:
            curs.execute("select data from other where name = 'js'")
            js = curs.fetchall()
            if(js):
                data = js[0][0]
            else:
                data = ''

            return(
                html_minify(
                    template('index', 
                        imp = ['전역 JS', wiki_set(1), custom(), other2([0, 0])],
                        data =  '<form method="post"> \
                                    <textarea rows="30" cols="100" name="content">'\
                                        + html.escape(data) + \
                                    '</textarea> \
                                    <br> \
                                    <br> \
                                    <div class="form-actions"> \
                                        <button class="btn btn-primary" type="submit">저장</button> \
                                    </div> \
                                </form>',
                        menu = [['edit_set', '설정 편집']]
                    )
                )
            )
    else:
        return(redirect('/'))

@route('/not_close_topic')
def not_close_topic():
    div = '<ul>'
    i = 1

    curs.execute('select title, sub from rd order by date desc')
    n_list = curs.fetchall()
    for data in n_list:
        curs.execute('select * from stop where title = ? and sub = ? and close = "O"', [data[0], data[1]])
        is_close = curs.fetchall()
        if(not is_close):
            div += '<li>' + str(i) + '. <a href="/topic/' + url_pas(data[0]) + '/sub/' + url_pas(data[1]) + '">' + data[0] + ' (' + data[1] + ')</a></li>'
            i += 1
            
    div += '</ul>'

    return(
        html_minify(
            template('index', 
                imp = ['열린 토론 목록', wiki_set(1), custom(), other2([0, 0])],
                data = div,
                menu = [['manager', '관리자']]
            )
        )
    )

@route('/image/<name:path>')
def static(name = None):
    if(os.path.exists(os.path.join('image', name))):
        return(static_file(name, root = 'image'))
    else:
        return(redirect('/'))

@route('/acl_list')
def acl_list():
    div = '<ul>'
    i = 0

    curs.execute("select title, acl from data where acl = 'admin' or acl = 'user' order by acl desc")
    list_data = curs.fetchall()
    for data in list_data:
        if(not re.search('^사용자:', data[0])):
            if(data[1] == 'admin'):
                acl = '관리자'
            else:
                acl = '가입자'

            div += '<li>' + str(i + 1) + '. <a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a> (' + acl + ')</li>'
            
            i += 1
        
    div += '</ul>'
    
    return(
        html_minify(
            template('index', 
                imp = ['ACL 문서 목록', wiki_set(1), custom(), other2([0, 0])],
                data = div,
                menu = [['other', '기타']]
            )
        )
    )
    
@route('/list_acl')
def list_acl():
    div = '<ul>'
    i = 0

    curs.execute("select name, acl from alist order by name desc")
    list_data = curs.fetchall()
    for data in list_data:
        if(data[1] == 'ban'):
            acl = '차단'
        elif(data[1] == 'mdel'):
            acl = '많은 문서 삭제'
        elif(data[1] == 'toron'):
            acl = '토론 관리'
        elif(data[1] == 'check'):
            acl = '사용자 검사'
        elif(data[1] == 'acl'):
            acl = '문서 ACL'
        elif(data[1] == 'hidel'):
            acl = '역사 숨김'
        elif(data[1] == 'owner'):
            acl = '소유자'
            
        div += '<li>' + str(i + 1) + '. <a href="/admin_plus/' + url_pas(data[0]) + '">' + data[0] + '</a> (' + acl + ')</li>'
        
        i += 1
    
    div += '</ul><br><a href="/manager/8">(생성)</a>'

    return(
        html_minify(
            template('index',    
                imp = ['ACL 목록', wiki_set(1), custom(), other2([0, 0])],
                data = re.sub('^<ul></ul><br>', '', div),
                menu = [['manager', '관리자']]
            )
        )
    )

@route('/admin_plus/<name:path>', method=['POST', 'GET'])
def admin_plus(name = None):
    if(admin_check(None, 'admin_plus (' + name + ')') != 1):
        return(re_error('/error/3'))

    if(request.method == 'POST'):
        curs.execute("delete from alist where name = ?", [name])
        
        if(request.forms.ban):
            curs.execute("insert into alist (name, acl) values (?, 'ban')", [name])

        if(request.forms.mdel):
            curs.execute("insert into alist (name, acl) values (?, 'mdel')", [name])   

        if(request.forms.toron):
            curs.execute("insert into alist (name, acl) values (?, 'toron')", [name])
            
        if(request.forms.check):
            curs.execute("insert into alist (name, acl) values (?, 'check')", [name])

        if(request.forms.acl):
            curs.execute("insert into alist (name, acl) values (?, 'acl')", [name])

        if(request.forms.hidel):
            curs.execute("insert into alist (name, acl) values (?, 'hidel')", [name])

        if(request.forms.owner):
            curs.execute("insert into alist (name, acl) values (?, 'owner')", [name])
            
        conn.commit()
        
        return(redirect('/admin_plus/' + url_pas(name)))
    else:
        curs.execute('select acl from alist where name = ?', [name])
        test = curs.fetchall()
        
        data = '<ul>'
        exist_list = ['', '', '', '', '', '', '']

        for go in test:
            if(go[0] == 'ban'):
                exist_list[0] = 'checked="checked"'
            elif(go[0] == 'mdel'):
                exist_list[1] = 'checked="checked"'
            elif(go[0] == 'toron'):
                exist_list[2] = 'checked="checked"'
            elif(go[0] == 'check'):
                exist_list[3] = 'checked="checked"'
            elif(go[0] == 'acl'):
                exist_list[4] = 'checked="checked"'
            elif(go[0] == 'hidel'):
                exist_list[5] = 'checked="checked"'
            elif(go[0] == 'owner'):
                exist_list[6] = 'checked="checked"'

        data += '<li><input type="checkbox" name="ban" ' + exist_list[0] + '> 차단</li>'
        data += '<li><input type="checkbox" name="mdel" ' + exist_list[1] + '> 많은 문서 삭제</li>'
        data += '<li><input type="checkbox" name="toron" ' + exist_list[2] + '> 토론 관리</li>'
        data += '<li><input type="checkbox" name="check" ' + exist_list[3] + '> 사용자 검사</li>'
        data += '<li><input type="checkbox" name="acl" ' + exist_list[4] + '> 문서 ACL</li>'
        data += '<li><input type="checkbox" name="hidel" ' + exist_list[5] + '> 역사 숨김</li>'
        data += '<li><input type="checkbox" name="owner" ' + exist_list[6] + '> 소유자</li></ul>'

        return(
            html_minify(
                template('index', 
                    imp = ['관리 그룹 추가', wiki_set(1), custom(), other2([0, 0])],
                    data = '<form method="post">' \
                                + data + \
                                '<div class="form-actions"> \
                                    <button class="btn btn-primary" type="submit">저장</button> \
                                </div> \
                            </form>',
                    menu = [['manager', '관리자']]
                )
            )
        )        
        
@route('/admin_list')
def admin_list():
    i = 1
    div = '<ul>'
    
    curs.execute("select id, acl from user where not acl = 'user'")
    user_data = curs.fetchall()

    for data in user_data:
        name = ip_pas(data[0]) + ' (' + data[1] + ')'

        div += '<li>' + str(i) + '. ' + name + '</li>'
        
        i += 1
        
    div += '</ul>'
                
    return(
        html_minify(
            template('index', 
                imp = ['관리자 목록', wiki_set(1), custom(), other2([0, 0])],
                data = div,
                menu = [['other', '기타']]
            )
        )
    )
        
@route('/record/<name:path>')
@route('/record/<name:path>/n/<num:int>')
@route('/recent_changes')
def recent_changes(name = None, num = 1):
    ydmin = admin_check(1, None)
    zdmin = admin_check(6, None)
    ban = ''
    send = '<br>'
    div =  '<table style="width: 100%; text-align: center;"> \
                <tbody> \
                    <tr> \
                        <td style="width: 33.3%;">문서명</td> \
                        <td style="width: 33.3%;">기여자</td> \
                        <td style="width: 33.3%;">시간</td> \
                    </tr>'
    
    if(name):
        if(num * 50 <= 0):
            v = 50
        else:
            v = num * 50
            
        i = v - 50

        div = '<a href="/user/' + url_pas(name) + '/topic">(토론 기록)</a><br><br>' + div

        curs.execute("select id, title, date, ip, send, leng from history where ip = ? order by date desc limit ?, ?", [name, str(i), str(v)])
    else:
        curs.execute("select id, title, date, ip, send, leng from history where not date = 'Dump' order by date desc limit 50")

    for data in curs.fetchall():         
        send = '<br>'
        if(data[4]):
            if(not re.search("^(?: *)$", data[4])):
                send = data[4]
    
        title = html.escape(data[1])
        
        if(re.search("\+", data[5])):
            leng = '<span style="color:green;">' + data[5] + '</span>'
        elif(re.search("\-", data[5])):
            leng = '<span style="color:red;">' + data[5] + '</span>'
        else:
            leng = '<span style="color:gray;">' + data[5] + '</span>'
            
        if(ydmin == 1):
            curs.execute("select * from ban where block = ?", [data[3]])
            if(curs.fetchall()):
                ban = ' <a href="/ban/' + url_pas(data[3]) + '">(해제)</a>'
            else:
                ban = ' <a href="/ban/' + url_pas(data[3]) + '">(차단)</a>'            
            
        ip = ip_pas(data[3])
                
        if((int(data[0]) - 1) == 0):
            revert = ''
        else:
            revert = '<a href="/w/' + url_pas(data[1]) + '/r/' + str(int(data[0]) - 1) + '/diff/' + data[0] + '">(비교)</a> <a href="/revert/' + url_pas(data[1]) + '/r/' + str(int(data[0]) - 1) + '">(되돌리기)</a>'
        
        style = ''
        curs.execute("select title from hidhi where title = ? and re = ?", [data[1], data[0]])
        h = curs.fetchall()
        if(zdmin == 1):    
            if(h):                            
                ip += ' (숨김)'                            
                hidden = ' <a href="/history/' + url_pas(data[1]) + '/r/' + data[0] + '/hidden">(공개)'
            else:
                hidden = ' <a href="/history/' + url_pas(data[1]) + '/r/' + data[0] + '/hidden">(숨김)'
        else:
            if(h):
                ip = '숨김'
                hidden = ''
                send = '숨김'
                ban = ''
                style = 'display:none;'
            else:
                hidden = ''      
            
        div += '<tr style="' + style + '"> \
                    <td> \
                        <a href="/w/' + url_pas(data[1]) + '">' + title + '</a> (<a href="/history/' + url_pas(data[1]) + '">' + data[0] + '판</a>) ' + revert + ' (' + leng + ') \
                    </td> \
                    <td>' + ip + ban + hidden + '</td> \
                    <td>' + data[2] + '</td> \
                </tr> \
                <tr> \
                    <td colspan="3">' + send + '</td> \
                </tr>'
    else:
        div += '</tbody></table>'

    if(name):
        curs.execute("select end, why from ban where block = ?", [name])
        ban_it = curs.fetchall()
        if(ban_it):
            sub = '(차단)'
        else:
            sub = 0

        title = '기여 기록'
        menu = [['other', '기타'], ['user', '사용자']]
        div += '<br><a href="/record/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/record/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'
    else:
        sub = 0
        menu = 0
        title = '최근 변경내역'
            
    return(
        html_minify(
            template('index', 
                imp = [title, wiki_set(1), custom(), other2([sub, 0])],
                data = div,
                menu = menu
            )
        )
    )
        
@route('/history/<name:path>/r/<num:int>/hidden')
def history_hidden(name = None, num = None):
    if(admin_check(6, 'history_hidden (' + name + '#' + str(num) + ')') == 1):
        curs.execute("select * from hidhi where title = ? and re = ?", [name, str(num)])
        exist = curs.fetchall()
        if(exist):
            curs.execute("delete from hidhi where title = ? and re = ?", [name, str(num)])
        else:
            curs.execute("insert into hidhi (title, re) values (?, ?)", [name, str(num)])
            
        conn.commit()
    
    return(redirect('/history/' + url_pas(name)))
        
@route('/user_log')
@route('/user_log/n/<num:int>')
def user_log(num = 1):
    if(num * 50 <= 0):
         i = 50
    else:
        i = num * 50
        
    j = i - 50
    list_data = '<ul>'
    ydmin = admin_check(1, None)
    
    curs.execute("select id from user limit ?, ?", [str(j), str(i)])
    user_list = curs.fetchall()
    for data in user_list:
        if(ydmin == 1):
            curs.execute("select block from ban where block = ?", [data[0]])
            ban_exist = curs.fetchall()
            if(ban_exist):
                ban_button = ' <a href="/ban/' + url_pas(data[0]) + '">(해제)</a>'
            else:
                ban_button = ' <a href="/ban/' + url_pas(data[0]) + '">(차단)</a>'
        else:
            ban_button = ''
            
        ip = ip_pas(data[0])
            
        list_data += '<li>' + str(j + 1) + '. ' + ip + ban_button + '</li>'
        
        j += 1
    else:
        list_data += '</ul><br><a href="/user_log/n/' + str(num - 1) + '">(이전)</a> <a href="/user_log/n/' + str(num + 1) + '">(이후)</a>'

    return(
        html_minify(
            template('index', 
                imp = ['사용자 가입 기록', wiki_set(1), custom(), other2([0, 0])],
                data = list_data,
                menu = [['other', '기타']]
            )
        )
    )

@route('/admin_log')
@route('/admin_log/n/<num:int>')
def user_log(num = 1):
    if(num * 50 <= 0):
         i = 50
    else:
        i = num * 50
        
    j = i - 50
    list_data = '<ul>'
    
    curs.execute("select who, what, time from re_admin order by time desc limit ?, ?", [str(j), str(i)])
    get_list = curs.fetchall()
    for data in get_list:            
        ip = ip_pas(data[0])
            
        list_data += '<li>' + str(j + 1) + '. ' + ip + ' / ' + data[1] + ' / ' + data[2] + '</li>'
        
        j += 1
    else:
        list_data +=    '</ul><br> \
                        <span>주의 : 권한 사용 안하고 열람만 해도 기록되는 경우도 있습니다.</span> \
                        <br> \
                        <br> \
                        <a href="/admin_log/n/' + str(num - 1) + '">(이전)</a> <a href="/admin_log/n/' + str(num + 1) + '">(이후)</a>'

    return(
        html_minify(
            template('index', 
                imp = ['관리자 권한 기록', wiki_set(1), custom(), other2([0, 0])],
                data = list_data,
                menu = [['other', '기타']]
            )
        )
    )

@route('/give_log')
@route('/give_log/n/<num:int>')
def give_log(num = 1):
    if(num * 50 <= 0):
         i = 50
    else:
        i = num * 50
        
    j = i - 50
    list_data = '<ul>'
    back = ''

    curs.execute("select name, acl from alist order by name asc limit ?, ?", [str(j), str(i)])
    get_list = curs.fetchall()
    for data in get_list:                      
        if(back != data[0]):
            back = data[0]
            j += 1

        list_data += '<li>' + str(j) + '. ' + data[0] + ' ('
        
        if(data[1] == 'ban'):
            d = '차단'
        elif(data[1] == 'mdel'):
            d = '많은 문서 삭제'
        elif(data[1] == 'toron'):
            d = '토론'
        elif(data[1] == 'check'):
            d = '사용자 검사'
        elif(data[1] == 'acl'):
            d = 'ACL'
        elif(data[1] == 'hidel'):
            d = '역사 가리기'
        else:
            d = '소유자'
            
        list_data += d + ')</li>'
    else:
        list_data += '</ul><br><a href="/give_log/n/' + str(num - 1) + '">(이전)</a> <a href="/give_log/n/' + str(num + 1) + '">(이후)</a>'

    return(
        html_minify(
            template('index', 
                imp = ['권한 목록', wiki_set(1), custom(), other2([0, 0])],
                data = list_data,
                menu = [['other', '기타']]
            )
        )
    )

@route('/indexing')
def indexing():
    if(admin_check(None, 'indexing') != 1):
        return(re_error('/error/3'))

    curs.execute("select name from sqlite_master where type in ('table', 'view') and name not like 'sqlite_%' union all select name from sqlite_temp_master where type in ('table', 'view') order by 1;")
    data = curs.fetchall()
    for table in data:
        print('----- ' + table[0] + ' -----')
        curs.execute('select sql from sqlite_master where name = ?', [table[0]])
        cul = curs.fetchall()
        r_cul = re.findall('(?:([^ (]*) text)', str(cul[0]))
        for n_cul in r_cul:
            print(n_cul)
            sql = 'create index index_' + table[0] + '_' + n_cul + ' on ' + table[0] + '(' + n_cul + ')'
            try:
                curs.execute(sql)
            except:
                pass
    conn.commit()
    return(redirect('/'))        
        
@route('/xref/<name:path>')
@route('/xref/<name:path>/n/<num:int>')
def xref(name = None, num = 1):
    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
        
    i = v - 50
    div = '<ul>'
    
    curs.execute("select link, type from back where title = ? and not type = 'cat' and not type = 'no' order by link asc limit ?, ?", [name, str(i), str(v)])
    for data in curs.fetchall():
        div += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a>'
        
        if(data[1]):
            if(data[1] == 'include'):
                d = '포함'
            elif(data[1] == 'file'):
                d = '파일'
            else:
                d = '넘겨주기'
                
            div += ' (' + d + ')'
        
        div += '</li>'
        
        if(re.search('^틀:', data[0])):
            div += '<li><a id="inside" href="/xref/' + url_pas(data[0]) + '">' + data[0] + ' [역링크]</a></li>'
      
    div += '</ul><br><a href="/xref/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/xref/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'
    
    return(
        html_minify(
            template('index', 
                imp = [name, wiki_set(1), custom(), other2([' (역링크)', 0])],
                data = div,
                menu = [['w/' + url_pas(name), '문서']]
            )
        )
    )

@route('/please')
@route('/please/<num:int>')
def please(num = 1):
    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
        
    i = v - 50
    div = '<ul>'
    var = ''
    
    i += 1
    curs.execute("select distinct title from back where type = 'no' order by title asc limit ?, ?", [str(i), str(v)])
    for data in curs.fetchall():
        if(var != data[0]):
            div += '<li>' + str(i) + '. <a class="not_thing" href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a></li>'        
            i += 1
            var = data[0]
        
    div += '</ul><br><a href="/please/' + str(num - 1) + '">(이전)</a> <a href="/please/' + str(num + 1) + '">(이후)</a>'
    
    return(
        html_minify(
            template('index', 
                imp = ['필요한 문서', wiki_set(1), custom(), other2([0, 0])],
                data = div,
                menu = [['other', '기타']]
            )
        )
    )
        
@route('/recent_discuss')
@route('/recent_discuss/<tools:path>')
def recent_discuss(tools = 'normal'):
    if(tools == 'normal' or tools == 'close'):
        div = ''
        
        if(tools == 'normal'):
            div += '<a href="/recent_discuss/close">(닫힌 토론)</a>'
            m_sub = 0
        else:
            div += '<a href="/recent_discuss">(열린 토론)</a>'
            m_sub = ' (닫힘)'

        div +=  '<br> \
                <br> \
                <table style="width: 100%; text-align: center;"> \
                <tbody> \
                    <tr> \
                        <td style="width: 50%;">토론명</td> \
                        <td style="width: 50%;">시간</td> \
                    </tr>'
    else:
        return(redirect('/'))
    
    curs.execute("select title, sub, date from rd order by date desc limit 50")
    for data in curs.fetchall():
        title = html.escape(data[0])
        sub = html.escape(data[1])

        close = 0
        if(tools == 'normal'):
            curs.execute("select title from stop where title = ? and sub = ? and close = 'O'", [data[0], data[1]])
            if(curs.fetchall()):
                close = 1
        else:
            curs.execute("select title from stop where title = ? and sub = ? and close = 'O'", [data[0], data[1]])
            if(not curs.fetchall()):
                close = 1

        if(close == 0):
            div += '<tr> \
                        <td> \
                            <a href="/topic/' + url_pas(data[0]) + '/sub/' + url_pas(data[1]) + '">' + title + '</a> (' + sub + ') \
                        </td> \
                        <td>' + data[2] + '</td> \
                    </tr>'
    else:
        div +=      '</tbody> \
                </table>'
            
    return(
        html_minify(
            template('index', 
                imp = ['최근 토론내역', wiki_set(1), custom(), other2([m_sub, 0])],
                data = div,
                menu = 0
            )
        )
    )

@route('/block_log')
@route('/block_log/n/<num:int>')
def block_log(num = 1):
    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
    
    i = v - 50
    div =   '<table style="width: 100%; text-align: center;"> \
                <tbody> \
                    <tr> \
                        <td style="width: 33.3%;">차단자</td> \
                        <td style="width: 33.3%;">관리자</td> \
                        <td style="width: 33.3%;">기간</td> \
                    </tr> \
                    <tr> \
                        <td colspan="2">이유</td> \
                        <td>시간</td> \
                    </tr>'
    
    curs.execute("select why, block, blocker, end, today from rb order by today desc limit ?, ?", [str(i), str(v)])
    for data in curs.fetchall():
        why = html.escape(data[0])
        
        b = re.search("^([0-9]{1,3}\.[0-9]{1,3})$", data[1])
        if(b):
            ip = data[1] + ' (대역)'
        else:
            ip = ip_pas(data[1])

        if(data[3] != ''):
            end = data[3]
        else:
            end = '무기한'
            
        div += '<tr> \
                    <td>' + ip + '</td> \
                    <td>' + ip_pas(data[2]) + '</td> \
                    <td>' + end + '</td> \
                </tr> \
                <tr> \
                    <td colspan="2">' + why + '</td> \
                    <td>' + data[4] + '</td> \
                </tr>'
    else:
        div +=      '</tbody> \
                </table> \
                <br> \
                <a href="/block_log/n/' + str(num - 1) + '">(이전)</a> <a href="/block_log/n/' + str(num + 1) + '">(이후)</a>'
                
    return(
        html_minify(
            template('index', 
                imp = ['차단 기록', wiki_set(1), custom(), other2([0, 0])],
                data = div,
                menu = [['other', '기타']]
            )
        )
    )

@route('/history/<name:path>', method=['POST', 'GET'])    
@route('/history/<name:path>/n/<num:int>', method=['POST', 'GET'])
def history_view(name = None, num = 1):
    if(request.method == 'POST'):
        return(redirect('/w/' + url_pas(name) + '/r/' + request.forms.b + '/diff/' + request.forms.a))
    else:
        select = ''
        if(num * 50 <= 0):
            i = 50
        else:
            i = num * 50
            
        j = i - 50
 
        admin1 = admin_check(1, None)
        admin2 = admin_check(6, None)
        
        div =   '<table style="width: 100%; text-align: center;"> \
                    <tbody> \
                        <tr> \
                            <td style="width: 33.3%;">판</td> \
                            <td style="width: 33.3%;">기여자</td> \
                            <td style="width: 33.3%;">시간</td> \
                        </tr>'
        
        curs.execute("select send, leng, ip, date, title, id from history where title = ? order by id + 0 desc limit ?, ?", [name, str(j), str(i)])
        all_data = curs.fetchall()
        for data in all_data:
            select += '<option value="' + data[5] + '">' + data[5] + '</option>'
            
            if(data[0]):
                send = data[0]
            else:
                send = '<br>'
                
            if(re.search("^\+", data[1])):
                leng = '<span style="color:green;">' + data[1] + '</span>'
            elif(re.search("^\-", data[1])):
                leng = '<span style="color:red;">' + data[1] + '</span>'
            else:
                leng = '<span style="color:gray;">' + data[1] + '</span>'
                
            ip = ip_pas(data[2])
            
            curs.execute("select block from ban where block = ?", [data[2]])
            ban_it = curs.fetchall()
            if(ban_it):
                if(admin1 == 1):
                    ban = ' <a href="/ban/' + url_pas(data[2]) + '">(해제)</a>'
                else:
                    ban = ' (X)'
            else:
                if(admin1 == 1):
                    ban = ' <a href="/ban/' + url_pas(data[2]) + '">(차단)</a>'
                else:
                    ban = ''
            
            curs.execute("select * from hidhi where title = ? and re = ?", [name, data[5]])
            hid_it = curs.fetchall()
            if(hid_it):
                if(admin2):
                    hidden = ' <a href="/history/' + url_pas(name) + '/r/' + url_pas(data[5]) + '/hidden">(공개)'
                    hid = 0
                else:
                    hid = 1
            else:
                if(admin2):
                    hidden = ' <a href="/history/' + url_pas(name) + '/r/' + url_pas(data[5]) + '/hidden">(숨김)'
                    hid = 0
                else:
                    hidden = ''
                    hid = 0
            
            if(hid == 1):
                div += '<tr> \
                            <td colspan="3">숨김</td> \
                        </tr>'
            else:
                div += '<tr> \
                            <td> \
                                ' + data[5] + '판</a> <a href="/w/' + url_pas(name) + '/r/' + url_pas(data[5]) + '">(보기)</a> \
                                    <a href="/raw/' + url_pas(name) + '/r/' + url_pas(data[5]) + '">(원본)</a> \
                                    <a href="/revert/' + url_pas(name) + '/r/' + url_pas(data[5]) + '">(되돌리기)</a> (' + leng + ') \
                            </td> \
                            <td>' + ip + ban + hidden + '</td> \
                            <td>' + data[3] + '</td> \
                        </tr> \
                        <tr> \
                            <td colspan="3">' + send + '</td> \
                        </tr>'
        else:
            div +=      '</tbody> \
                    </table> \
                    <br> \
                    <a href="/history/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/history/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'

        div =   '<form method="post"> \
                    <select name="a"> \
                        ' + select + ' \
                    </select> \
                    <select name="b"> \
                        ' + select + ' \
                    </select> \
                    <button class="btn btn-primary" type="submit">비교</button> \
                </form>' + div

        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), custom(), other2([' (역사)', 0])],
                    data = div,
                    menu = [['w/' + url_pas(name), '문서'], ['move_data/' + url_pas(name), '이동 기록']]
                )
            )
        )
            
@route('/search', method=['POST'])
def search():
    return(redirect('/search/' + url_pas(request.forms.search)))

@route('/goto', method=['POST'])
def goto():
    curs.execute("select title from data where title = ?", [request.forms.search])
    data = curs.fetchall()
    if(data):
        return(redirect('/w/' + url_pas(request.forms.search)))
    else:
        return(redirect('/search/' + url_pas(request.forms.search)))

@route('/search/<name:path>')
@route('/search/<name:path>/n/<num:int>')
def deep_search(name = None, num = 1):
    if(num * 50 <= 0):
        v = num * 50
    else:
        v = 50

    i = v - 50

    div = '<ul>'
    div_plus = ''
    end = ''

    curs.execute("select title from data where title like ?", ['%' + name + '%'])
    title_list = curs.fetchall()

    curs.execute("select title from data where data like ?", ['%' + name + '%'])
    data_list = curs.fetchall()

    curs.execute("select title from data where title = ?", [name])
    exist = curs.fetchall()
    if(exist):
        div = '<ul><li>문서로 <a href="/w/' + url_pas(name) + '">바로가기</a></li><br><br>'
    else:
        div = '<ul><li>문서가 없습니다. <a class="not_thing" href="/w/' + url_pas(name) + '">바로가기</a></li><br><br>'

    if(title_list):
        no = 0

        if(data_list):
            all_list = title_list + data_list
        else:
            all_list = title_list
    else:
        if(data_list):
            no = 1

            all_list = data_list
        else:
            all_list = ''
    
    if(all_list != ''):
        for data in all_list:
            try:
                var_re = re.search(name, data[0])
            except:
                var_re = re.search('\\' + name, data[0])
                
            if(var_re):
                if(no == 0):
                    div += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a> (제목)</li>'
                else:
                    div_plus += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a> (내용)</li>'
            else:
                no = 1

                div_plus += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a> (내용)</li>'
    else:
        div += '<li>검색 결과 없음</li>'

    div += div_plus + end

    div += '</ul><br><a href="/search/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/search/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'
    
    return(
        html_minify(
            template('index', 
                imp = [name, wiki_set(1), custom(), other2([' (검색)', 0])],
                data = div,
                menu = 0
            )
        )
    )
         
@route('/raw/<name:path>')
@route('/raw/<name:path>/r/<num:int>')
@route('/topic/<name:path>/sub/<sub_t:path>/raw/<num:int>')
def raw_view(name = None, sub_t = None, num = None):
    v_name = name
    sub = ' (원본)'
    
    if(not sub_t and num):
        curs.execute("select title from hidhi where title = ? and re = ?", [name, str(num)])
        hid = curs.fetchall()
        if(hid and admin_check(6, None) != 1):
            return(re_error('/error/3'))
        
        curs.execute("select data from history where title = ? and id = ?", [name, str(num)])

        sub += ' (' + str(num) + '판)'
        menu = [['history/' + url_pas(name), '역사']]
    elif(sub_t):
        curs.execute("select data from topic where id = ? and title = ? and sub = ? and block = ''", [str(num), name, sub_t])

        v_name = '토론 원본'
        sub = ' (' + str(num) + '번)'
        menu = [['topic/' + url_pas(name) + '/sub/' + url_pas(sub_t) + '#' + str(num), '토론']]
    else:
        curs.execute("select data from data where title = ?", [name])
        
        menu = [['w/' + url_pas(name), '문서']]

    data = curs.fetchall()
    if(data):
        p_data = html.escape(data[0][0])
        
        p_data = '<textarea readonly style="height: 80%;">' + p_data + '</textarea>'
        
        return(
            html_minify(
                template('index', 
                    imp = [v_name, wiki_set(1), custom(), other2([sub, 0])],
                    data = p_data,
                    menu = menu
                )
            )
        )
    else:
        return(redirect('/w/' + url_pas(name)))
        
@route('/revert/<name:path>/r/<num:int>', method=['POST', 'GET'])
def revert(name = None, num = None):
    ip = ip_check()
    can = acl_check(name)
    today = get_time()
    
    if(request.method == 'POST'):
        curs.execute("select title from hidhi where title = ? and re = ?", [name, str(num)])
        if(curs.fetchall() and admin_check(6, None) != 1):
            return(re_error('/error/3'))

        if(can == 1):
            return(re_error('/ban'))

        curs.execute("delete from back where link = ?", [name])
        conn.commit()

        curs.execute("select data from history where title = ? and id = ?", [name, str(num)])
        data = curs.fetchall()
        if(data):                                
            curs.execute("select data from data where title = ?", [name])
            d = curs.fetchall()
            if(d):
                leng = leng_check(len(d[0][0]), len(data[0][0]))
                curs.execute("update data set data = ? where title = ?", [data[0][0], name])
            else:
                leng = '+' + str(len(data[0][0]))
                curs.execute("insert into data (title, data, acl) values (?, ?, '')", [name, data[0][0]])
                
            history_plus(name, data[0][0], today, ip, request.forms.send + ' (' + str(num) + '판)', leng)
            
            namumark(name, data[0][0], 1, 0, 0)
            conn.commit()
            
            return(redirect('/w/' + url_pas(name)))
    else:
        curs.execute("select title from hidhi where title = ? and re = ?", [name, str(num)])
        hid = curs.fetchall()
        if(hid and admin_check(6, None) != 1):
            return(re_error('/error/3'))    
                          
        if(can == 1):
            return(re_error('/ban'))

        curs.execute("select title from history where title = ? and id = ?", [name, str(num)])
        if(not curs.fetchall()):
            return(redirect('/w/' + url_pas(name)))

        l = custom()
        if(l[2] == 0):
            plus = '<span>비 로그인 상태입니다. 비 로그인으로 작업 시 아이피가 역사에 기록됩니다.</span><br><br>'
        else:
            plus = ''

        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), l, other2([' (되돌리기)', 0])],
                    data =  plus + ' \
                            <form method="post"> \
                                <input placeholder="사유" style="width: 100%;" class="form-control input-sm" name="send" type="text"> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">되돌리기</button> \
                            </form>',
                    menu = [['history/' + url_pas(name), '역사'], ['recent_changes', '최근 변경']]
                )
            )
        )            
                    
@route('/m_del', method=['POST', 'GET'])
def m_del():
    if(admin_check(2, 'm_del') != 1):
        return(re_error('/error/3'))

    if(request.method == 'POST'):
        today = get_time()
        ip = ip_check()

        data = request.forms.content + '\r\n'
        m = re.findall('(.*)\r\n', data)
        for g in m:
            curs.execute("select data from data where title = ?", [g])
            d = curs.fetchall()
            if(d):
                curs.execute("delete from back where title = ?", [g])

                leng = '-' + str(len(d[0][0]))
                curs.execute("delete from data where title = ?", [g])
                history_plus(g, '', today, ip, request.forms.send + ' (대량 삭제)', leng)
            data = re.sub('(.*)\r\n', '', data, 1)
        conn.commit()

        return(redirect('/'))
    else:
        return(
            html_minify(
                template('index', 
                    imp = ['많은 문서 삭제', wiki_set(1), custom(), other2([0, 0])],
                    data = '<span> \
                                문서명 A \
                                <br> \
                                문서명 B \
                                <br> \
                                문서명 C \
                                <br> \
                                <br> \
                                이런 식으로 적으세요. \
                            </span> \
                            <br> \
                            <br> \
                            <form method="post"> \
                                <textarea style="height: 80%;" name="content"></textarea> \
                                <br> \
                                <br> \
                                <input placeholder="사유" style="width: 100%;" class="form-control input-sm" name="send" type="text"> \
                                <br> \
                                <br> \
                                <div class="form-actions"> \
                                    <button class="btn btn-primary" type="submit">삭제</button> \
                                </div> \
                            </form>',
                    menu = [['manager', '관리자']]
                )
            )
        )
                
@route('/edit/<name:path>', method=['POST', 'GET'])
@route('/edit/<name:path>/from/<name2:path>', method=['POST', 'GET'])
@route('/edit/<name:path>/section/<num:int>', method=['POST', 'GET'])
def edit(name = None, name2 = None, num = None):
    ip = ip_check()
    can = acl_check(name)

    if(can == 1):
        return(re_error('/ban'))
    
    if(request.method == 'POST'):
        if(len(request.forms.send) > 500):
            return(re_error('/error/15'))

        if(request.forms.otent == request.forms.content):
            return(re_error('/error/18'))

        today = get_time()
        content = savemark(request.forms.content)

        curs.execute("select data from data where title = ?", [name])
        old = curs.fetchall()
        if(old):
            if(not num and request.forms.otent != old[0][0]):
                return(re_error('/error/12'))

            leng = leng_check(len(request.forms.otent), len(content))
            
            if(num):
                content = old[0][0].replace(request.forms.otent, content)
                
            curs.execute("update data set data = ? where title = ?", [content, name])
        else:
            leng = '+' + str(len(content))

            curs.execute("insert into data (title, data, acl) values (?, ?, '')", [name, content])
        
        history_plus(name, content, today, ip, send_p(request.forms.send), leng)

        curs.execute("delete from back where link = ?", [name])
        namumark(name, content, 1, 0, 0)
        conn.commit()
        
        return(redirect('/w/' + url_pas(name)))
    else:            
        curs.execute("select data from data where title = ?", [name])
        new = curs.fetchall()
        if(new):
            if(num):
                i = 0
                j = 0
                
                data = new[0][0] + '\r\n'
                while(1):
                    m = re.search("((?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n(?:(?:(?:(?!(?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n).)*)(?:\n)?)+)", data)
                    if(m):
                        if(i == num - 1):
                            g = m.groups()
                            data = re.sub("\r\n$", "", g[0])
                            
                            break
                        else:
                            data = re.sub("((?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n(?:(?:(?:(?!(?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n).)*)(?:\n)?)+)", "", data, 1)
                            
                            i += 1
                    else:
                        j = 1
                        
                        break
                        
                if(j == 0):
                    data = re.sub("\r\n$", "", data)
            else:
                data = new[0][0]
        else:
            data = ''

        if(num):
            action = '/section/' + str(num)
        else:
            action = ''
            
        data2 = data
        if(not num):
            p = '<form method="post" id="get_edit" action="/edit_get/' + url_pas(name) + '"> \
                    <input placeholder="불러 올 문서" name="name" style="width: 50%;" type="text"> \
                    <button id="preview" class="btn" type="submit">불러오기</button> \
                </form>'
        else:
            p = ''
            
        if(name2):
            curs.execute("select data from data where title = ?", [name2])
            d1 = curs.fetchall()
            if(d1):
                data = d1[0][0]
                p = ''

        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), custom(), other2([' (수정)', 0])],
                    data = p + '<form method="post" action="/edit/' + url_pas(name) + action + '"> \
                                    <textarea style="height: 80%;" name="content">' + html.escape(data) + '</textarea> \
                                    <textarea style="display: none; height: 80%;" name="otent">' + html.escape(data2) + '</textarea> \
                                    <br> \
                                    <br> \
                                    <input placeholder="사유" name="send" style="width: 100%;" type="text"> \
                                    <br> \
                                    <br> \
                                    <div class="form-actions"> \
                                        <button id="preview" class="btn btn-primary" type="submit">저장</button> \
                                        <button id="preview" class="btn" type="submit" formaction="/preview/' + url_pas(name) + action + '">미리보기</button> \
                                    </div> \
                                </form>',
                    menu = [['w/' + url_pas(name), '문서']]
                )
            )
        )
        
@route('/edit_get/<name:path>', method=['POST'])
def edit_get(name = None):
    return(redirect('/edit/' + url_pas(name) + '/from/' + url_pas(request.forms.name)))

@route('/preview/<name:path>', method=['POST'])
@route('/preview/<name:path>/section/<num:int>', method=['POST'])
def preview(name = None, num = None):
    ip = ip_check()
    can = acl_check(name)
    
    if(can == 1):
        return(re_error('/ban'))
         
    newdata = request.forms.content
    newdata = re.sub('^#(?:redirect|넘겨주기) (?P<in>[^\n]*)', ' * [[\g<in>]] 문서로 넘겨주기', newdata)
    enddata = namumark(name, newdata, 0, 0, 0)

    if(num):
        action = '/section/' + str(num)
    else:
        action = ''

    return(
        html_minify(
            template('index', 
                imp = [name, wiki_set(1), custom(), other2([' (미리보기)', 0])],
                data = '<form method="post" action="/edit/' + url_pas(name) + action + '"> \
                            <textarea style="height: 80%;" name="content">' + html.escape(request.forms.content) + '</textarea> \
                            <textarea style="display: none; height: 80%;" name="otent">' + html.escape(request.forms.otent) + '</textarea> \
                            <br> \
                            <br> \
                            <input placeholder="사유" name="send" style="width: 100%;" type="text"> \
                            <br> \
                            <br> \
                            <div class="form-actions"> \
                                <button id="save" class="btn btn-primary" type="submit">저장</button> \
                                <button id="preview" class="btn" type="submit" formaction="/preview/' + url_pas(name) + action + '">미리보기</button> \
                            </div> \
                        </form> \
                        <br><br>' + enddata,
                menu = [['w/' + url_pas(name), '문서']]
            )
        )
    )
        
@route('/delete/<name:path>', method=['POST', 'GET'])
def delete(name = None):
    ip = ip_check()
    can = acl_check(name)

    if(can == 1):
        return(re_error('/ban'))
    
    if(request.method == 'POST'):
        curs.execute("select data from data where title = ?", [name])
        data = curs.fetchall()
        if(data):
            today = get_time()
            
            leng = '-' + str(len(data[0][0]))
            history_plus(name, '', today, ip, request.forms.send + ' (삭제)', leng)
            
            curs.execute("delete from back where link = ?", [name])
            curs.execute("delete from data where title = ?", [name])
            conn.commit()
            
        return(redirect('/w/' + url_pas(name)))
    else:
        curs.execute("select title from data where title = ?", [name])
        if(not curs.fetchall()):
            return(redirect('/w/' + url_pas(name)))

        l = custom()
        if(l[2] == 0):
            plus = '<span>비 로그인 상태입니다. 비 로그인으로 작업 시 아이피가 역사에 기록됩니다.</span><br><br>'
        else:
            plus = ''

        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), l, other2([' (삭제)', 0])],
                    data = '<form method="post"> \
                                ' + plus + ' \
                                <input placeholder="사유" style="width: 100%;" class="form-control input-sm" name="send" type="text"> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">삭제</button> \
                            </form>',
                    menu = [['w/' + url_pas(name), '문서']]
                )
            )
        )            
            
@route('/move_data/<name:path>')
@route('/move_data/<name:path>/<n:int>')
def move_data(name = None, n = 1):
    if(n > 0):
        i = n
    else:
        i = 1
       
    j = i * 50
    da = '<ul>'
    
    curs.execute("select origin, new, date, who, send from move where origin = ? or new = ? limit ?, ?", [name, name, j - 50, j])
    for d in curs.fetchall():
        if(d[4] == ''):
            sn = '(없음)'
        else:
            sn = d[4]
        da += '<li><a href="/move_data/' + url_pas(d[0]) + '">' + d[0] + '</a> >> <a href="/move_data/' + url_pas(d[1]) + '">' + d[1] + '</a> / ' + d[2] + ' / ' + d[3] + ' / ' + sn + '</li>'
    da += '</ul><br><a href="/move_data/' + name + '/' + str(n - 1) + '">(이전)</a> <a href="/move_data/' + name + '/' + str(n + 1) + '">(이후)</a>'
    
    return(
        html_minify(
            template('index', 
                imp = [name, wiki_set(1), custom(), other2([' (이동)', 0])],
                data = da,
                menu = [['w/' + url_pas(name), '문서']]
            )
        )
    )        
            
@route('/move/<name:path>', method=['POST', 'GET'])
def move(name = None):
    ip = ip_check()
    can = acl_check(name)
    today = get_time()

    if(can == 1):
        return(re_error('/ban'))
    
    if(request.method == 'POST'):
        curs.execute("select title from history where title = ?", [request.forms.title])
        if(curs.fetchall()):
            return(re_error('/error/19'))
        
        curs.execute("select data from data where title = ?", [name])
        data = curs.fetchall()

        leng = '0'
        if(data):            
            curs.execute("update data set title = ? where title = ?", [request.forms.title, name])
            curs.execute("update back set link = ? where link = ?", [request.forms.title, name])
            
            d = data[0][0]
        else:
            d = ''
            
        history_plus(name, d, today, ip, request.forms.send + ' (<a href="/w/' + url_pas(name) + '">' + name + '</a> - <a href="/w/' + url_pas(request.forms.title) + '">' + request.forms.title + '</a> 이동)', leng)
            
        curs.execute('insert into move (origin, new, date, who, send) values (?, ?, ?, ?, ?)', [name, request.forms.title, today, ip, request.forms.send])
        curs.execute("update history set title = ? where title = ?", [request.forms.title, name])
        conn.commit()
        
        return(redirect('/w/' + url_pas(request.forms.title)))
    else:
        c = custom()
        if(c[2] == 0):
            plus = '<span>비 로그인 상태입니다. 비 로그인으로 작업 시 아이피가 역사에 기록됩니다.</span><br><br>'
        else:
            plus = ''
            
        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), c, other2([' (이동)', 0])],
                    data = '<form method="post"> \
                                ' + plus + ' \
                                <input placeholder="문서명" class="form-control input-sm" value="' + name + '" name="title" type="text"> \
                                <br> \
                                <br> \
                                <input placeholder="사유" style="width: 100%;" class="form-control input-sm" name="send" type="text"> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">이동</button> \
                            </form>',
                    menu = [['w/' + url_pas(name), '문서']]
                )
            )
        )
            
@route('/other')
def other():
    return(
        html_minify(
            template('index', 
                imp = ['기타 메뉴', wiki_set(1), custom(), other2([0, 0])],
                data = namumark('', '[목차(없음)]\r\n' + \
                                    '== 기록 ==\r\n' + \
                                    ' * [[wiki:block_log|차단 기록]]\r\n' + \
                                    ' * [[wiki:user_log|가입 기록]]\r\n' + \
                                    ' * [[wiki:admin_log|권한 기록]]\r\n' + \
                                    ' * [[wiki:manager/6|기여 기록]]\r\n' + \
                                    ' * [[wiki:not_close_topic|열린 토론 목록]]\r\n' + \
                                    '== 기타 ==\r\n' + \
                                    ' * [[wiki:title_index|모든 문서]]\r\n' + \
                                    ' * [[wiki:acl_list|ACL 문서]]\r\n' + \
                                    ' * [[wiki:admin_list|관리자 목록]]\r\n' + \
                                    ' * [[wiki:give_log|권한 목록]]\r\n' + 
                                    ' * [[wiki:please|필요한 문서]]\r\n' + \
                                    ' * [[wiki:upload|파일 올리기]]\r\n' + \
                                    '== 관리자 ==\r\n' + \
                                    ' * [[wiki:manager/1|관리자 메뉴]]\r\n' + \
                                    '== 버전 ==\r\n' + \
                                    '이 오픈나무는 [[https://github.com/2DU/openNAMU/blob/SQLite/version.md|' + r_ver + ']]판 입니다.', 0, 0, 0),
                menu = 0
            )
        )
    )
    
@route('/manager', method=['POST', 'GET'])
@route('/manager/<num:int>', method=['POST', 'GET'])
def manager(num = 1):
    if(num == 1):
        return(
            html_minify(
                template('index', 
                    imp = ['관리자 메뉴', wiki_set(1), custom(), other2([0, 0])],
                    data = namumark('', '[목차(없음)]\r\n' + \
                                        '== 목록 ==\r\n' + \
                                        ' * [[wiki:manager/2|문서 ACL]]\r\n' + \
                                        ' * [[wiki:manager/3|사용자 검사]]\r\n' + \
                                        ' * [[wiki:manager/10|사용자 비교]]\r\n' + \
                                        ' * [[wiki:manager/4|사용자 차단]]\r\n' + \
                                        ' * [[wiki:manager/5|권한 주기]]\r\n' + \
                                        ' * [[wiki:m_del|여러 문서 삭제]]\r\n' + \
                                        '== 소유자 ==\r\n' + \
                                        ' * [[wiki:indexing|인덱싱]]\r\n' + \
                                        ' * [[wiki:manager/8|관리 그룹 생성]]\r\n' + \
                                        ' * [[wiki:edit_set|설정 편집]]\r\n' + \
                                        ' * [[wiki:manager/9|JSON 출력]]\r\n' + \
                                        ' * [[wiki:json_in|JSON 입력]]\r\n' + \
                                        '== 기타 ==\r\n' + \
                                        ' * 이 메뉴에 없는 기능은 해당 문서의 역사나 토론에서 바로 사용 가능함', 0, 0, 0),
                    menu = [['other', '기타']]
                )
            )
        )
    elif(num == 2):
        if(request.method == 'POST'):
            return(redirect('/acl/' + url_pas(request.forms.name)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['ACL 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="문서명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['manager', '관리자']]
                    )
                )
            )
    elif(num == 3):
        if(request.method == 'POST'):
            return(redirect('/check/' + url_pas(request.forms.name)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['검사 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="사용자명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['manager', '관리자']]
                    )
                )
            )
    elif(num == 4):
        if(request.method == 'POST'):
            return(redirect('/ban/' + url_pas(request.forms.name)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['차단 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="사용자명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['manager', '관리자']]
                    )
                )
            )
    elif(num == 5):
        if(request.method == 'POST'):
            return(redirect('/admin/' + url_pas(request.forms.name)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['권한 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="사용자명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['manager', '관리자']]
                    )
                )
            )
    elif(num == 6):
        if(request.method == 'POST'):
            return(redirect('/record/' + url_pas(request.forms.name)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['기록 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="사용자명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['other', '기타']]
                    )
                )
            )
    elif(num == 8):
        if(request.method == 'POST'):
            return(redirect('/admin_plus/' + url_pas(request.forms.name)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['그룹 생성 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="그룹명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['manager', '관리자']]
                    )
                )
            )
    elif(num == 9):
        if(request.method == 'POST'):
            return(redirect('/json_out/' + url_pas(request.forms.name)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['문서 출력 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="문서명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['manager', '관리자']]
                    )
                )
            )
    elif(num == 10):
        if(request.method == 'POST'):
            return(redirect('/check/' + url_pas(request.forms.name) + '/' + url_pas(request.forms.name2)))
        else:
            return(
                html_minify(
                    template('index', 
                        imp = ['검사 이동', wiki_set(1), custom(), other2([0, 0])],
                        data = '<form method="post"> \
                                    <input placeholder="사용자명" name="name" type="text"> \
                                    <br> \
                                    <br> \
                                    <input placeholder="비교 대상" name="name2" type="text"> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">이동</button> \
                                </form>',
                        menu = [['manager', '관리자']]
                    )
                )
            )
    else:
        return(redirect('/'))

@route('/json_out/<name:path>')
def json_out(name = None):
    if(admin_check(None, 'json_out') != 1):
        return(re_error('/error/3'))

    curs.execute('select data from data where title = ?', [name])
    get_d = curs.fetchall()
    if(get_d):
        da = get_d[0][0]
    else:
        da = ''

    curs.execute('select ip from history where title = ? order by ip asc', [name])
    get_h = curs.fetchall()

    var_n = ''
    hi_d = ''
    for hi in get_h:
        if(hi[0] != var_n):
            var_n = hi[0]
            hi_d += json.dumps(hi[0]) + ', '
    else:
        hi_d = re.sub(', $', '', hi_d)  

    if(hi_d == ''):
        return(redirect('/w/' + url_pas(name)))
    
    json_f = '{ "title" : ' + json.dumps(name) + ', "data" : ' + json.dumps(da) + ', "history" : [' + hi_d + '] }'

    return(json_f)        

@route('/json_in', method=['POST', 'GET'])
def json_in():
    if(admin_check(None, 'json_in') != 1):
        return(re_error('/error/3'))

    if(request.method == 'POST'):
        data = json.loads(request.forms.data)
        title = data["title"]

        curs.execute('select title from history where title = ?', [title])
        get_d = curs.fetchall()
        if(get_d):
            return(redirect('/w/' + url_pas(title)))

        curs.execute('insert into data (title, data, acl) values (?, ?, "")', [title, data["data"]])

        i = 0
        date = get_time()
        for hi in data["history"]:
            i += 1
            if(i == 1):
                curs.execute('insert into history (id, title, data, date, ip, send, leng) values (?, ?, ?, ?, ?, "", ?)', [i, title, data["data"], date, hi, '+' + len(data["data"])])
            else:
                curs.execute('insert into history (id, title, data, date, ip, send, leng) values (?, ?, "", ?, ?, "", "0")', [i, title, date, hi])

        conn.commit()
        return(redirect('/w/' + url_pas(title)))
    else:
        return(
            html_minify(
                template('index', 
                    imp = ['문서 JSON 입력', wiki_set(1), custom(), other2([0, 0])],
                    data = '<form method="post"> \
                                <textarea style="height: 80%;" name="data"></textarea> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">입력</button> \
                            </form>',
                    menu = [['manager', '관리자']]
                )    
            )
        )        
        
@route('/title_index')
@route('/title_index/<num:int>/<page:int>')
def title_index(num = 1000, page = 1):
    if(page > 0):
        v_page = page * num
    else:
        v_page = 1 * num

    if(num != 0):
        i = [v_page - num + 1]
    else:
        i = [1, 0, 0, 0, 0, 0]

    data = '<ul><a href="/title_index/0/1">(전체)</a> <a href="/title_index/500/1">(500)</a> <a href="/title_index/5000/1">(5000개)</a> <a href="/title_index/10000/1">(10000개)</a> <a href="/title_index/50000/1">(50000개)</a><br><br>'

    if(num == 0):
        curs.execute("select title from data order by title asc")
    else:
        curs.execute("select title from data order by title asc limit ?, ?", [str(v_page - num), str(num)])
    title_list = curs.fetchall()

    for list_data in title_list:
        data += '<li>' + str(i[0]) + '. <a href="/w/' + url_pas(list_data[0]) + '">' + list_data[0] + '</a></li>'

        if(num == 0):
            if(re.search('^분류:', list_data[0])):
                i[1] += 1
            elif(re.search('^사용자:', list_data[0])):
                i[2] += 1
            elif(re.search('^틀:', list_data[0])):
                i[3] += 1
            elif(re.search('^파일:', list_data[0])):
                i[4] += 1
            else:
                i[5] += 1
        
        i[0] += 1

    if(num == 0):
        if(title_list):        
            data += '<br><br><li>이 위키에는 총 ' + str(i[0]) + '개의 문서가 있습니다.</li><br><br> \
                    <li>틀 문서는 총 ' + str(i[3]) + '개의 문서가 있습니다.</li> \
                    <li>분류 문서는 총 ' + str(i[1]) + '개의 문서가 있습니다.</li> \
                    <li>사용자 문서는 총 ' + str(i[2]) + '개의 문서가 있습니다.</li> \
                    <li>파일 문서는 총 ' + str(i[4]) + '개의 문서가 있습니다.</li> \
                    <li>나머지 문서는 총 ' + str(i[5]) + '개의 문서가 있습니다.</li>'
    else:
        data += '</ul><br><a href="/title_index/' + str(num) + '/' + str(page - 1) + '">(이전)</a> <a href="/title_index/' + str(num) + '/' + str(page + 1) + '">(이후)</a>'
    
    return(
        html_minify(
            template('index', 
                imp = ['모든 문서', wiki_set(1), custom(), other2([' (' + str(num) + ')', 0])],
                data = data,
                menu = [['other', '기타']]
            )    
        )
    )
        
@route('/topic/<name:path>/sub/<sub:path>/b/<num:int>')
def topic_block(name = None, sub = None, num = None):
    if(admin_check(3, 'blind (' + name + ' - ' + sub + '#' + str(num) + ')') != 1):
        return(re_error('/error/3'))

    curs.execute("select block from topic where title = ? and sub = ? and id = ?", [name, sub, str(num)])
    block = curs.fetchall()
    if(block):
        if(block[0][0] == 'O'):
            curs.execute("update topic set block = '' where title = ? and sub = ? and id = ?", [name, sub, str(num)])
        else:
            curs.execute("update topic set block = 'O' where title = ? and sub = ? and id = ?", [name, sub, str(num)])
        
        rd_plus(
            name, 
            sub, 
            get_time()
        )
        conn.commit()
        
    return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '#' + str(num)))
        
@route('/topic/<name:path>/sub/<sub:path>/notice/<num:int>')
def topic_top(name = None, sub = None, num = None):
    if(admin_check(3, 'notice (' + name + ' - ' + sub + '#' + str(num) + ')') != 1):
        return(re_error('/error/3'))

    curs.execute("select * from topic where title = ? and sub = ? and id = ?", [name, sub, str(num)])
    topic_data = curs.fetchall()
    if(topic_data):
        curs.execute("select top from topic where id = ? and title = ? and sub = ?", [str(num), name, sub])
        top_data = curs.fetchall()
        if(top_data):
            if(top_data[0][0] == 'O'):
                curs.execute("update topic set top = '' where title = ? and sub = ? and id = ?", [name, sub, str(num)])
            else:
                curs.execute("update topic set top = 'O' where title = ? and sub = ? and id = ?", [name, sub, str(num)])
        
        rd_plus(
            name, 
            sub, 
            get_time()
        )
        conn.commit()

    return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '#' + str(num)))        

@route('/topic/<name:path>/sub/<sub:path>/tool/agree')
def topic_agree(name = None, sub = None):
    if(admin_check(3, 'agree (' + name + ' - ' + sub + ')') != 1):
        return(re_error('/error/3'))

    ip = ip_check()
    
    curs.execute("select id from topic where title = ? and sub = ? order by id + 0 desc limit 1", [name, sub])
    topic_check = curs.fetchall()
    if(topic_check):
        time = get_time()
        
        curs.execute("select title from agreedis where title = ? and sub = ?", [name, sub])
        agree = curs.fetchall()
        if(agree):
            curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) values (?, ?, ?, '합의 결렬', ?, ?, '', '1')", [str(int(topic_check[0][0]) + 1), name, sub, time, ip])
            curs.execute("delete from agreedis where title = ? and sub = ?", [name, sub])
        else:
            curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) values (?, ?, ?, '합의 완료', ?, ?, '', '1')", [str(int(topic_check[0][0]) + 1), name, sub, time, ip])
            curs.execute("insert into agreedis (title, sub) values (?, ?)", [name, sub])

        rd_plus(
            name, 
            sub, 
            time
        )
        conn.commit()
            
    return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
        
@route('/topic/<name:path>/sub/<sub:path>/tool/<tool:path>')
def topic_stop(name = None, sub = None, tool = None):
    if(tool == 'close'):
        close = 'O'
        n_close = ''
        data = '토론 닫음'
        n_data = '토론 다시 열기'
    elif(tool == 'stop'):
        close = ''
        n_close = 'O'
        data = '토론 정지'
        n_data = '토론 재 시작'
    else:
        return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))

    if(admin_check(3, 'topic stop and end (' + name + ' - ' + sub + ')') != 1):
        return(re_error('/error/3'))

    ip = ip_check()
    
    curs.execute("select id from topic where title = ? and sub = ? order by id + 0 desc limit 1", [name, sub])
    topic_check = curs.fetchall()
    if(topic_check):
        time = get_time()
        
        curs.execute("select title from stop where title = ? and sub = ? and close = ?", [name, sub, close])
        stop = curs.fetchall()
        if(stop):
            curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) values (?, ?, ?, ?, ?, ?, '', '1')", [str(int(topic_check[0][0]) + 1), name, sub, n_data, time, ip])
            curs.execute("delete from stop where title = ? and sub = ? and close = ?", [name, sub, close])
        else:
            curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) values (?, ?, ?, ?, ?, ?, '', '1')", [str(int(topic_check[0][0]) + 1), name, sub, data, time, ip])
            curs.execute("insert into stop (title, sub, close) values (?, ?, ?)", [name, sub, close])
            curs.execute("delete from stop where title = ? and sub = ? and close = ?", [name, sub, n_close])
        
        rd_plus(
            name, 
            sub, 
            time
        )
        conn.commit()
        
    return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))    

@route('/topic/<name:path>/sub/<sub:path>/admin/<num:int>')
def topic_admin(name = None, sub = None, num = None):
    curs.execute("select block, ip from topic where title = ? and sub = ? and id = ?", [name, sub, str(num)])
    data = curs.fetchall()
    if(not data):
        return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))

    is_ban = '<li><a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/b/' + str(num) + '">'
    if(data[0][0] == 'O'):
        is_ban += '가림 해제'
    else:
        is_ban += '가림'
    is_ban += '</a></li>'

    curs.execute("select id from topic where title = ? and sub = ? and id = ? and top = 'O'", [name, sub, str(num)])
    is_ban += '<li><a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/notice/' + str(num) + '">'
    if(curs.fetchall()):
        is_ban += '공지 해제'
    else:
        is_ban += '공지'
    is_ban += '</a></li>'

    curs.execute("select end from ban where block = ?", [data[0][1]])
    ban = '<li><a href="/ban/' + url_pas(data[0][1]) + '">'
    if(curs.fetchall()):
        ban += '차단 해제'
    else:
        ban += '차단'
    ban += '</a></li>' + is_ban

    return(
        html_minify(
            template('index', 
                imp = ['토론 관리', wiki_set(1), custom(), other2([' (' + str(num) + '번)', 0])],
                data = '<ul>' + ban + '</ul>',
                menu = [['topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '#' + str(num), '토론']]
            )  
        )
    )

@route('/topic/<name:path>/sub/<sub:path>', method=['POST', 'GET'])
def topic(name = None, sub = None):
    ban = topic_check(name, sub)
    admin = admin_check(3, None)
    
    if(request.method == 'POST'):
        ip = ip_check()
        today = get_time()

        if(ban == 1 and admin != 1):
            return(re_error('/ban'))
        
        curs.execute("select id from topic where title = ? and sub = ? order by id + 0 desc limit 1", [name, sub])
        old_n = curs.fetchall()
        if(old_n):
            num = int(old_n[0][0]) + 1
        else:
            num = 1

            m = re.search('^사용자:([^/]+)', name)
            if(m):
                d = m.groups()
                curs.execute('insert into alarm (name, data, date) values (?, ?, ?)', [d[0], ip + '님이 <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '">사용자 토론</a>을 시작했습니다.', today])
        
        rd_plus(name, sub, today)
        
        data = re.sub("\[\[(분류:(?:(?:(?!\]\]).)*))\]\]", "[br]", request.forms.content)
        m = re.findall("(?:#([0-9]+))", data)
        for da in m:
            curs.execute("select ip from topic where title = ? and sub = ? and id = ?", [name, sub, da])
            ip_d = curs.fetchall()
            if(ip_d):
                if(not re.search('(\.|:)', ip_d[0][0])):
                    curs.execute('insert into alarm (name, data, date) values (?, ?, ?)', [ip_d[0][0], ip + '님이 <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '#' + str(num) + '">토론</a>에서 언급 했습니다.', today])
            data = re.sub("(?P<in>#(?:[0-9]+))", '[[\g<in>]]', data)

        data = savemark(data)
        
        curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) values (?, ?, ?, ?, ?, ?, '', '')", [str(num), name, sub, data, today, ip])
        conn.commit()
        
        return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
    else:
        s = ''
        div = ''

        curs.execute("select title from stop where title = ? and sub = ? and close = 'O'", [name, sub])
        cd = curs.fetchall()

        curs.execute("select title from stop where title = ? and sub = ? and close = ''", [name, sub])
        sd = curs.fetchall()
        
        if(admin == 1):
            if(cd):
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/tool/close">(열기)</a> '
            else:
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/tool/close">(닫기)</a> '
            
            if(sd):
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/tool/stop">(재개)</a> '
            else:
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/tool/stop">(정지)</a> '

            curs.execute("select title from agreedis where title = ? and sub = ?", [name, sub])
            if(curs.fetchall()):
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/tool/agree">(합의)</a>'
            else:
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/tool/agree">(취소)</a>'
            
            div += '<br><br>'
        
        if((sd or cd) and admin != 1):
            s = 'display: none;'
        
        curs.execute("select data, id, date, ip, block, top from topic where title = ? and sub = ? order by id + 0 asc", [name, sub])
        t1 = curs.fetchall()

        curs.execute("select data, id, date, ip from topic where title = ? and sub = ? and top = 'O' order by id + 0 asc", [name, sub])
        t2 = curs.fetchall()

        for d in t2:                   
            a = ''
            curs.execute("select who from re_admin where what = ? order by time desc limit 1", ['notice (' + name + ' - ' + sub + '#' + d[1] + ')'])
            m = curs.fetchall()
            if(m):
                a += ' @' + m[0][0]
                                
            div += '<table id="toron"> \
                        <tbody> \
                            <tr> \
                                <td id="toron_color_red"> \
                                    <a href="#' + d[1] + '">#' + d[1] + '</a> ' + ip_pas(d[3]) + a + ' <span style="float:right;">' + d[2] + '</span> \
                                </td> \
                            </tr> \
                            <tr> \
                                <td>' + namumark('', d[0], 0, 0, 0) + '</td> \
                            </tr> \
                        </tbody> \
                    </table> \
                    <br>'
                    
        i = 1          
        for d in t1:
            if(i == 1):
                start = d[3]
            
            p = d[0]
            if(d[4] == 'O'):
                bd = 'style="background: gainsboro;"'
                if(admin != 1):
                    curs.execute("select who from re_admin where what = ? order by time desc limit 1", ['blind (' + name + ' - ' + sub + '#' + str(i) + ')'])
                    b = curs.fetchall()
                    if(b):
                        p = '[[사용자:' + b[0][0] + ']]님이 가림'
                    else:
                        p = '관리자가 가림'
            else:
                bd = ''

            p = namumark('', p, 0, 0, 0)

            ip = ip_pas(d[3])

            curs.execute('select acl from user where id = ?', [d[3]])
            user_acl = curs.fetchall()
            if(user_acl and user_acl[0][0] != 'user'):
                ip += ' <a href="javascript:void(0);" title="관리자">★</a>'

            if(admin == 1 or bd == ''):
                ip += ' <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/raw/' + str(i) + '">(원본)</a>'

                if(admin == 1):
                    ip += ' <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/admin/' + str(i) + '">(관리)</a>'

            curs.execute("select end from ban where block = ?", [d[3]])
            if(curs.fetchall()):
                ip += ' <a href="javascript:void(0);" title="차단자">†</a>'
                    
            if(d[5] == '1'):
                c = '_blue'
            elif(d[3] == start):
                c = '_green'
            else:
                c = ''
                
            if(p == ''):
                p = '<br>'
                         
            div += '<table id="toron"> \
                        <tbody> \
                            <tr> \
                                <td id="toron_color' + c + '"> \
                                    <a href="javascript:void(0);" id="' + str(i) + '">#' + str(i) + '</a> ' + ip + ' <span style="float:right;">' + d[2] + '</span> \
                                </td> \
                            </tr> \
                            <tr ' + bd + '> \
                                <td>' + p + '</td> \
                            </tr> \
                        </tbody> \
                    </table> \
                    <br>'
                
            i += 1

        l = custom()
        if(ban != 1):
            data = '<a id="reload" href="javascript:void(0);" onclick="location.href.endsWith(\'#reload\') ?  location.reload(true) : location.href = \'#reload\'"> \
                        <i aria-hidden="true" class="fa fa-refresh"></i> \
                    </a> \
                    <form style="' + s + '" method="post"> \
                        <br> \
                        <textarea style="width: 100%; height: 100px;" name="content"></textarea> \
                        <br> \
                        <br> \
                        <button class="btn btn-primary" type="submit">전송</button> \
                    </form>'

            if(l[2] == 0 and s == ''):
                data += '<span>비 로그인 상태입니다. 비 로그인으로 작업 시 아이피가 토론에 기록됩니다.</span>'
        else:
            data = ''

        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), l, other2([' (토론)', 0])],
                    data =  '<h2 style="margin-top: 0px;">' + sub + '</h2> \
                            <br> \
                            ' + div + ' \
                            ' + data,
                    menu = [['topic/' + url_pas(name), '목록']]
                )  
            )
        )
        
@route('/topic/<name:path>', method=['POST', 'GET'])
@route('/topic/<name:path>/<tool:path>', method=['GET'])
def close_topic_list(name = None, tool = None):
    div = ''
    i = 0
    list_d = 0

    if(request.method == 'POST'):
        t_num = ''
        while(1):
            curs.execute("select title from topic where title = ? and sub = ? limit 1", [name, request.forms.topic + t_num])
            if(curs.fetchall()):
                if(t_num == ''):
                    t_num = ' 2'
                else:
                    t_num = ' ' + str(int(t_num.replace(' ', '')) + 1)
            else:
                break

        return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(request.forms.topic + t_num)))
    else:
        plus = ''
        menu = [['topic/' + url_pas(name), '목록']]
        if(tool == 'close'):
            curs.execute("select sub from stop where title = ? and close = 'O' order by sub asc", [name])
            sub = '닫힘'
        elif(tool == 'agree'):
            curs.execute("select sub from agreedis where title = ? order by sub asc", [name])
            sub = '합의'
        else:
            curs.execute("select sub from rd where title = ? order by date desc", [name])
            sub = '토론 목록'
            menu = [['w/' + url_pas(name), '문서']]
            plus =  '<br> \
                    <a href="/topic/' + url_pas(name) + '/close">(닫힘)</a> <a href="/topic/' + url_pas(name) + '/agree">(합의)</a> \
                    <br> \
                    <br> \
                    <input placeholder="토론명" class="form-control" name="topic" style="width: 100%;"> \
                    <br> \
                    <br> \
                    <button class="btn btn-primary" type="submit">만들기</button>'

        for data in curs.fetchall():
            curs.execute("select data, date, ip, block from topic where title = ? and sub = ? and id = '1'", [name, data[0]])
            if(curs.fetchall()):                
                it_p = 0
                if(sub == '토론 목록'):
                    curs.execute("select title from stop where title = ? and sub = ? and close = 'O' order by sub asc", [name, data[0]])
                    close = curs.fetchall()
                    if(close):
                        it_p = 1
                
                if(it_p != 1):
                    div += '<h2><a href="/topic/' + url_pas(name) + '/sub/' + url_pas(data[0]) + '">' + str((i + 1)) + '. ' + data[0] + '</a></h2>'
                
                i += 1
        
        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), custom(), other2([' (' + sub + ')', 0])],
                    data =  '<form style="margin-top: 0px;" method="post"> \
                                ' + div + plus + ' \
                            </form>',
                    menu = menu
                )    
            )
        )
        
@route('/login', method=['POST', 'GET'])
def login():
    session = request.environ.get('beaker.session')
    agent = request.environ.get('HTTP_USER_AGENT')
    ip = ip_check()
    ban = ban_check()
        
    if(request.method == 'POST'):        
        if(ban == 1):
            return(re_error('/ban'))

        curs.execute("select pw from user where id = ?", [request.forms.id])
        user = curs.fetchall()
        if(not user):
            return(re_error('/error/5'))

        if(session.get('Now') == 1):
            return(re_error('/error/11'))

        if(not bcrypt.checkpw(bytes(request.forms.pw, 'utf-8'), bytes(user[0][0], 'utf-8'))):
            return(re_error('/error/10'))

        session['Now'] = 1
        session['DREAMER'] = request.forms.id

        curs.execute("select css from custom where user = ?", [request.forms.id])
        css_data = curs.fetchall()
        if(css_data):
            session['Daydream'] = css_data[0][0]
        else:
            session['Daydream'] = ''
        
        curs.execute("insert into ua_d (name, ip, ua, today, sub) values (?, ?, ?, ?, '')", [request.forms.id, ip, agent, get_time()])
        conn.commit()
        
        return(redirect('/user'))                            
    else:        
        if(ban == 1):
            return(re_error('/ban'))

        if(session.get('Now') == 1):
            return(re_error('/error/11'))

        return(
            html_minify(
                template('index',    
                    imp = ['로그인', wiki_set(1), custom(), other2([0, 0])],
                    data = '<form method="post"> \
                                <input placeholder="아이디" name="id" type="text"> \
                                <br> \
                                <br> \
                                <input placeholder="비밀번호" name="pw" type="password"> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">로그인</button> \
                                <br> \
                                <br> \
                                <span>주의 : 만약 HTTPS 연결이 아닌 경우 데이터가 유출될 가능성이 있습니다. 이에 대해 책임지지 않습니다.</span> \
                            </form>',
                    menu = [['user', '사용자']]
                )
            )
        )
                
@route('/change', method=['POST', 'GET'])
def change_password():
    ip = ip_check()
    ban = ban_check()
    
    if(request.method == 'POST'):      
        if(request.forms.pw2 != request.forms.pw3):
            return(re_error('/error/20'))

        if(ban == 1):
            return(re_error('/ban'))

        curs.execute("select pw from user where id = ?", [request.forms.id])
        user = curs.fetchall()
        if(not user):
            return(re_error('/error/10'))

        if(re.search('(\.|:)', ip)):
            return(redirect('/login'))

        if(not bcrypt.checkpw(bytes(request.forms.pw, 'utf-8'), bytes(user[0][0], 'utf-8'))):
            return(re_error('/error/5'))

        hashed = bcrypt.hashpw(bytes(request.forms.pw2, 'utf-8'), bcrypt.gensalt())
        
        curs.execute("update user set pw = ? where id = ?", [hashed.decode(), request.forms.id])
        conn.commit()
        
        return(redirect('/user'))
    else:        
        if(ban == 1):
            return(re_error('/ban'))

        if(re.search('(\.|:)', ip)):
            return(redirect('/login'))

        return(
            html_minify(
                template('index',    
                    imp = ['비밀번호 변경', wiki_set(1), custom(), other2([0, 0])],
                    data = '<form method="post"> \
                                <input placeholder="아이디" name="id" type="text"> \
                                <br> \
                                <br> \
                                <input placeholder="현재 비밀번호" name="pw" type="password"> \
                                <br> \
                                <br> \
                                <input placeholder="변경할 비밀번호" name="pw2" type="password"> \
                                <br> \
                                <br> \
                                <input placeholder="재 확인" name="pw3" type="password"> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">변경</button> \
                                <br> \
                                <br> \
                                <span>주의 : 만약 HTTPS 연결이 아닌 경우 데이터가 유출될 가능성이 있습니다. 이에 대해 책임지지 않습니다.</span> \
                            </form>',
                    menu = [['user', '사용자']]
                )
            )
        )
                
@route('/check/<name:path>')
@route('/check/<name:path>/<name2:path>')
def user_check(name = None, name2 = None):
    curs.execute("select acl from user where id = ? or id = ?", [name, name2])
    user = curs.fetchall()
    if(user and user[0][0] != 'user'):
        if(admin_check(None, None) != 1):
            return(re_error('/error/4'))

    if(admin_check(4, 'check (' + name + ')') != 1):
        return(re_error('/error/3'))
    
    if(name2):
        if(re.search('(?:\.|:)', name)):
            if(re.search('(?:\.|:)', name2)):
                curs.execute("select name, ip, ua, today from ua_d where ip = ? or ip = ? order by today desc", [name, name2])
            else:
                curs.execute("select name, ip, ua, today from ua_d where ip = ? or name = ? order by today desc", [name, name2])
        else:
            if(re.search('(?:\.|:)', name2)):
                curs.execute("select name, ip, ua, today from ua_d where name = ? or ip = ? order by today desc", [name, name2])
            else:
                curs.execute("select name, ip, ua, today from ua_d where name = ? or name = ? order by today desc", [name, name2])
    elif(re.search('(?:\.|:)', name)):
        curs.execute("select name, ip, ua, today from ua_d where ip = ? order by today desc", [name])
    else:
        curs.execute("select name, ip, ua, today from ua_d where name = ? order by today desc", [name])
    record = curs.fetchall()
    if(record):
        c = '<table style="width: 100%; text-align: center;"> \
                <tbody> \
                    <tr> \
                        <td style="width: 33.3%;">이름</td> \
                        <td style="width: 33.3%;">아이피</td> \
                        <td style="width: 33.3%;">언제</td> \
                    </tr>'

        for data in record:
            if(data[2]):
                ua = data[2]
            else:
                ua = '<br>'

            c +=    '<tr> \
                        <td>' + ip_pas(data[0]) + '</td> \
                        <td>' + ip_pas(data[1]) + '</td> \
                        <td>' + data[3] + '</td> \
                    </tr> \
                    <tr><td colspan="3">' + ua + '</td></tr>'
        else:
            c += '</tbody></table>'
    else:
        c = ''
            
    return(
        html_minify(
            template('index',    
                imp = ['다중 검사', wiki_set(1), custom(), other2([0, 0])],
                data = c,
                menu = [['manager', '관리자']]
            )
        )
    )
                
@route('/register', method=['POST', 'GET'])
def register():
    ip = ip_check()
    ban = ban_check()

    if(ban == 1):
        return(re_error('/ban'))

    if(not admin_check(None, None) == 1):
        curs.execute('select data from other where name = "reg"')
        set_d = curs.fetchall()
        if(set_d and set_d[0][0] == 'on'):
            return(re_error('/ban'))
    
    if(request.method == 'POST'):        
        if(request.forms.pw != request.forms.pw2):
            return(re_error('/error/20'))

        if(re.search('(?:[^A-Za-zㄱ-힣0-9 ])', request.forms.id)):
            return(re_error('/error/8'))

        if(len(request.forms.id) > 32):
            return(re_error('/error/7'))

        curs.execute("select id from user where id = ?", [request.forms.id])
        if(curs.fetchall()):
            return(re_error('/error/6'))

        hashed = bcrypt.hashpw(bytes(request.forms.pw, 'utf-8'), bcrypt.gensalt())
        
        curs.execute("select id from user limit 1")
        user_ex = curs.fetchall()
        if(not user_ex):
            curs.execute("insert into user (id, pw, acl) values (?, ?, '소유자')", [request.forms.id, hashed.decode()])
        else:
            curs.execute("insert into user (id, pw, acl) values (?, ?, 'user')", [request.forms.id, hashed.decode()])
        conn.commit()
        
        return(redirect('/login'))
    else:        
        p = ''
        curs.execute('select data from other where name = "contract"')
        d = curs.fetchall()
        if(d and d[0][0] != ''):
            p = d[0][0] + '<br><br>'

        return(
            html_minify(
                template('index',    
                    imp = ['회원가입', wiki_set(1), custom(), other2([0, 0])],
                    data = '<form method="post"> \
                                ' + p + ' \
                                <input placeholder="아이디" name="id" type="text"> \
                                <br> \
                                <br> \
                                <input placeholder="비밀번호" name="pw" type="password"> \
                                <br> \
                                <br> \
                                <input placeholder="재 확인" name="pw2" type="password"> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">가입</button> \
                                <br> \
                                <br> \
                                <span>주의 : 만약 HTTPS 연결이 아닌 경우 데이터가 유출될 가능성이 있습니다. 이에 대해 책임지지 않습니다.</span> \
                            </form>',
                    menu = [['user', '사용자']]
                )
            )
        )
            
@route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session['Now'] = 0
    session.pop('DREAMER', None)

    return(redirect('/user'))
    
@route('/ban/<name:path>', method=['POST', 'GET'])
def user_ban(name = None):
    curs.execute("select acl from user where id = ?", [name])
    user = curs.fetchall()
    if(user and user[0][0] != 'user'):
        if(admin_check(None, None) != 1):
            return(re_error('/error/4'))

    if(request.method == 'POST'):
        if(admin_check(1, 'ban (' + name + ')') != 1):
            return(re_error('/error/3'))

        ip = ip_check()
        
        if(request.forms.year == '09'):
            end = ''
        else:
            end = request.forms.year + '-' + request.forms.month + '-' + request.forms.day

        curs.execute("select block from ban where block = ?", [name])
        if(curs.fetchall()):
            rb_plus(name, '해제', get_time(), ip, '')
            
            curs.execute("delete from ban where block = ?", [name])
        else:
            b = re.search("^([0-9]{1,3}\.[0-9]{1,3})$", name)
            if(b):
                band_d = 'O'
            else:
                band_d = ''

            rb_plus(name, end, get_time(), ip, request.forms.why)

            curs.execute("insert into ban (block, end, why, band) values (?, ?, ?, ?)", [name, end, request.forms.why, band_d])
        conn.commit()

        return(redirect('/ban/' + url_pas(name)))            
    else:
        if(admin_check(1, None) != 1):
            return(re_error('/error/3'))

        curs.execute("select block from ban where block = ?", [name])
        if(curs.fetchall()):
            now = '차단 해제'
            data = ''
        else:
            b = re.search("^([0-9]{1,3}\.[0-9]{1,3})$", name)
            if(b):
                now = '대역 차단'
            else:
                now = '차단'

            year_n = int("%04d" % (time.localtime().tm_year))
            year = '<option value="09">영구</option>'
            for i in range(year_n, year_n + 51):
                if(i == year_n):
                    year += '<option value="' + str(i) + '" selected>' + str(i) + '</option>'
                else:
                    year += '<option value="' + str(i) + '">' + str(i) + '</option>'

            month = '<option value="1" selected>1</option>'
            for i in range(2, 13):
                month += '<option value="' + str(i) + '">' + str(i) + '</option>'

            day = '<option value="1" selected>1</option>'
            for i in range(2, 32):
                day += '<option value="' + str(i) + '">' + str(i) + '</option>'
            
            data = '<select name="year"> \
                        ' + year + ' \
                    </select> \
                    <select name="month"> \
                        ' + month + ' \
                    </select> \
                    <select name="day"> \
                        ' + day + ' \
                    </select> \
                    <br> \
                    <br> \
                    <input placeholder="사유" class="form-control" name="why" style="width: 100%;"> \
                    <br> \
                    <br>'

        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), custom(), other2([' (' + now + ')', 0])],
                    data = '<form method="post"> \
                                ' + data + ' \
                                <button class="btn btn-primary" type="submit">' + now + '</button> \
                            </form>',
                    menu = [['manager', '관리자']]
                )
            )
        )            

@route('/user_acl/<name:path>', method=['POST', 'GET'])
def acl(name = None):
    ip = ip_check()
    if(ip != name or re.search("(\.|:)", name)):
        return(redirect('/login'))
    
    if(request.method == 'POST'):
        curs.execute("select acl from data where title = ?", ['사용자:' + name])
        acl_d = curs.fetchall()
        if(acl_d):
            if(request.forms.select == 'all'):
                curs.execute("update data set acl = 'all' where title = ?", ['사용자:' + name])
            elif(request.forms.select == 'user'):
                curs.execute("update data set acl = 'user' where title = ?", ['사용자:' + name])
            else:
                curs.execute("update data set acl = '' where title = ?", ['사용자:' + name])
                
            conn.commit()
            
        return(redirect('/w/' + url_pas('사용자:' + name)))

    curs.execute("select acl from data where title = ?", ['사용자:' + name])
    acl_d = curs.fetchall()
    if(acl_d):
        if(acl_d[0][0] == 'all'):
            now = '모두'
        elif(acl_d[0][0] == 'user'):
            now = '가입자'
        else:
            now = '일반'
        
        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), custom(), other2([' (SET)', 0])],
                    data = '<span>현재 ACL : ' + now + '</span> \
                            <br> \
                            <br> \
                            <form method="post"> \
                                <select name="select"> \
                                    <option value="all">모두</option> \
                                    <option value="user">가입자</option> \
                                    <option value="normal" selected="selected">일반</option> \
                                </select> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">ACL 변경</button> \
                            </form>',
                    menu = [['user', '사용자']]
                )
            )
        )
    else:
        return(redirect('/w/' + url_pas(name)))
                
@route('/acl/<name:path>', method=['POST', 'GET'])
def acl(name = None):
    if(request.method == 'POST'):
        if(admin_check(5, 'acl (' + name + ')') != 1):
            return(re_error('/error/3'))

        curs.execute("select acl from data where title = ?", [name])
        if(curs.fetchall()):
            if(request.forms.select == 'admin'):
                curs.execute("update data set acl = 'admin' where title = ?", [name])
            elif(request.forms.select == 'user'):
                curs.execute("update data set acl = 'user' where title = ?", [name])
            else:
                curs.execute("update data set acl = '' where title = ?", [name])
                
            conn.commit()
            
        return(redirect('/w/' + url_pas(name)))            
    else:
        if(admin_check(5, None) != 1):
            return(re_error('/error/3'))

        curs.execute("select acl from data where title = ?", [name])
        acl = curs.fetchall()
        if(acl):
            if(acl[0][0] == 'admin'):
                now = '관리자'
            elif(acl[0][0] == 'user'):
                now = '가입자'
            else:
                now = '일반'
            
            return(
                html_minify(
                    template('index', 
                        imp = [name, wiki_set(1), custom(), other2([' (ACL)', 0])],
                        data = '<span>현재 ACL : ' + now + '</span> \
                                <br> \
                                <br> \
                                <form method="post"> \
                                    <select name="select"> \
                                        <option value="admin" selected="selected">관리자</option> \
                                        <option value="user">가입자</option> \
                                        <option value="normal">일반</option> \
                                    </select> \
                                    <br> \
                                    <br> \
                                    <button class="btn btn-primary" type="submit">ACL 변경</button> \
                                </form>',
                        menu = [['w/' + url_pas(name), '문서'], ['manager', '관리자']]
                    )
                )
            )
        else:
            return(redirect('/w/' + url_pas(name)))
            
@route('/admin/<name:path>', method=['POST', 'GET'])
def user_admin(name = None):
    if(request.method == 'POST'):
        if(admin_check(None, 'admin (' + name + ')') != 1):
            return(re_error('/error/3'))

        if(request.forms.select == 'X'):
            curs.execute("update user set acl = 'user' where id = ?", [name])
        else:
            curs.execute("update user set acl = ? where id = ?", [request.forms.select, name])
        conn.commit()
        
        return(redirect('/admin/' + url_pas(name)))            
    else:
        if(admin_check(None, None) != 1):
            return(re_error('/error/3'))

        curs.execute("select acl from user where id = ?", [name])
        user = curs.fetchall()
        if(not user):
            return(re_error('/error/5'))

        div = '<option value="X">X</option>'
            
        curs.execute('select name from alist order by name asc')
        get_alist = curs.fetchall()
        if(get_alist):
            i = 0
            name_rem = ''
            for data in get_alist:
                if(name_rem != data[0]):
                    name_rem = data[0]
                    if(user[0][0] == data[0]):
                        div += '<option value="' + data[0] + '" selected="selected">' + data[0] + '</option>'
                    else:
                        div += '<option value="' + data[0] + '">' + data[0] + '</option>'
        
        return(
            html_minify(
                template('index', 
                    imp = [name, wiki_set(1), custom(), other2([' (권한 부여)', 0])],
                    data =  '<form method="post"> \
                                <select name="select"> \
                                    ' + div + ' \
                                </select> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">변경</button> \
                            </form>',
                    menu = [['manager', '관리자']]
                )
            )
        )
    
@route('/w/<name:path>/r/<a:int>/diff/<b:int>')
def diff_data(name = None, a = None, b = None):
    curs.execute("select data from history where id = ? and title = ?", [str(a), name])
    a_raw_data = curs.fetchall()
    if(a_raw_data):
        curs.execute("select data from history where id = ? and title = ?", [str(b), name])
        b_raw_data = curs.fetchall()
        if(b_raw_data):
            a_data = html.escape(a_raw_data[0][0])            
            b_data = html.escape(b_raw_data[0][0])

            if(a_data == b_data):
                result = '내용이 같습니다.'
            else:            
                diff_data = difflib.SequenceMatcher(None, a_data, b_data)
                result_1 = diff(diff_data, 1)
                result_2 = diff(diff_data, 0)

                if(a_data == result_1):
                    result = '<pre>' + result_2 + '</pre>'
                elif(b_data == result_2):
                    result = '<pre>' + result_1 + '</pre>'
                else:
                    result = '<pre>' + result_1 + '<hr>' + result_2 + '</pre>'
            
            return(
                html_minify(
                    template('index', 
                        imp = [name, wiki_set(1), custom(), other2([' (비교)', 0])],
                        data = result,
                        menu = [['history/' + url_pas(name), '역사']]
                    )
                )
            )

    return(redirect('/history/' + url_pas(name)))
        
@route('/down/<name:path>')
def down(name = None):
    curs.execute("select title from data where title like ?", ['%' + name + '/%'])
    under = curs.fetchall()
    
    div = '<ul>'
    i = 0

    for data in under:
        div += '<li>' + str(i + 1) + '. <a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a></li>'
        i += 1
        
    div += '</ul>'
    
    return(
        html_minify(
            template('index', 
                imp = [name, wiki_set(1), custom(), other2([' (하위)', 0])],
                data = div,
                menu = [['w/' + url_pas(name), '문서']]
            )
        )
    )

@route('/w/<name:path>')
@route('/w/<name:path>/r/<num:int>')
@route('/w/<name:path>/from/<redirect:path>')
def read_view(name = None, num = None, redirect = None):
    data_none = 0
    sub = ''
    acl = ''
    div = ''
    topic = 0
    
    if(not num):
        session = request.environ.get('beaker.session')
        if(session.get('View_List')):
            m = re.findall('([^\n]+)\n', session.get('View_List'))
            if(m[-1] != name):
                d = re.sub(name + '\n', '', session.get('View_List'))
                d += name + '\n'
                if(len(m) > 50):
                    d = re.sub('([^\n]+)\n', '', d, 1)
                session['View_List'] = d
        else:
            session['View_List'] = name + '\n'


    curs.execute("select sub from rd where title = ? order by date desc", [name])
    rd = curs.fetchall()
    for data in rd:
        curs.execute("select title from stop where title = ? and sub = ? and close = 'O'", [name, data[0]])
        if(not curs.fetchall()):
            topic = 1
            break
                
    curs.execute("select title from data where title like ?", ['%' + name + '/%'])
    if(curs.fetchall()):
        down = 1
    else:
        down = 0
        
    m = re.search("^(.*)\/(.*)$", name)
    if(m):
        uppage = m.groups()[0]
    else:
        uppage = 0
        
    if(admin_check(5, None) == 1):
        admin_memu = 1
    else:
        admin_memu = 0
        
    if(re.search("^분류:", name)):        
        curs.execute("select link from back where title = ? and type='cat' order by link asc", [name])
        back = curs.fetchall()
        if(back):
            div = '[목차(없음)]\r\n== 분류 ==\r\n'
            u_div = ''
            i = 0
            
            for data in back:       
                if(re.search('^분류:', data[0])):
                    if(u_div == ''):
                        u_div = '=== 하위 분류 ===\r\n'

                    u_div += ' * [[:' + data[0] + ']]\r\n'
                elif(re.search('^틀:', data[0])):
                    curs.execute("select data from data where title = ?", [data[0]])
                    d = mid_pas(curs.fetchall()[0][0], 0, 1, 0)[0]
                    if(re.search('\[\[' + name + ']]', d)):
                        div += ' * [[' + data[0] + ']]\r\n * [[wiki:xref/' + url_pas(data[0]) + '|' + data[0] + ' (역링크)]]\r\n'
                    else:
                        div += ' * [[' + data[0] + ']]\r\n'
                else:
                    div += ' * [[' + data[0] + ']]\r\n'

            div += u_div

    if(num):
        curs.execute("select title from hidhi where title = ? and re = ?", [name, str(num)])
        hid = curs.fetchall()
        if(hid and admin_check(6, None) != 1):
            return(redirect('/history/' + url_pas(name)))

        curs.execute("select title, data from history where title = ? and id = ?", [name, str(num)])
    else:
        curs.execute("select acl, data from data where title = ?", [name])

    data = curs.fetchall()
    if(data):
        if(not num):
            if(data[0][0] == 'admin'):
                acl = ' (관리자)'
            elif(data[0][0] == 'user'):
                acl = ' (가입자)'
                
        elsedata = data[0][1]
    else:
        data_none = 1
        response.status = 404
        elsedata = ''

    m = re.search("^사용자:([^/]*)", name)
    if(m):
        g = m.groups()
        
        curs.execute("select acl from user where id = ?", [g[0]])
        test = curs.fetchall()
        if(test and test[0][0] != 'user'):
            acl = ' (관리자)'
        else:
            acl = ''

        if(data):
            if(data[0][0] == 'all'):
                acl += ' (모두)'
            elif(data[0][0] == 'user'):
                acl += ' (가입자)'

        curs.execute("select block from ban where block = ?", [g[0]])
        user = curs.fetchall()
        if(user):
            sub = ' (차단)'
            
    if(redirect):
        elsedata = re.sub("^#(?:redirect|넘겨주기) (?P<in>[^\n]*)", " * [[\g<in>]] 문서로 넘겨주기", elsedata)
            
    enddata = namumark(name, elsedata, 0, 0, 1)

    if(data_none == 1):
        menu = [['edit/' + url_pas(name), '생성'], ['topic/' + url_pas(name), topic], ['history/' + url_pas(name), '역사'], ['move/' + url_pas(name), '이동'], ['xref/' + url_pas(name), '역링크']]
    else:
        menu = [['edit/' + url_pas(name), '수정'], ['topic/' + url_pas(name), topic], ['history/' + url_pas(name), '역사'], ['delete/' + url_pas(name), '삭제'], ['move/' + url_pas(name), '이동'], ['raw/' + url_pas(name), '원본'], ['xref/' + url_pas(name), '역링크']]
        if(admin_memu == 1):
            menu += [['acl/' + url_pas(name), 'ACL']]

    if(redirect):
        menu += [['w/' + url_pas(name), '넘기기']]
        enddata = '<ul id="redirect"><li><a href="/w/' + url_pas(redirect) + '/from/' + url_pas(name) + '">' + redirect + '</a>에서 넘어 왔습니다.</li></ul><br>' + enddata

    if(uppage != 0):
        menu += [['w/' + url_pas(uppage), '상위']]

    if(down):
        menu += [['down/' + url_pas(name), '하위']]

    if(num):
        menu = [['history/' + url_pas(name), '역사']]
        sub = ' (' + str(num) + '판)'
        acl = ''
        r_date = 0
    else:
        curs.execute("select date from history where title = ? order by date desc limit 1", [name])
        date = curs.fetchall()
        if(date):
            r_date = date[0][0]
        else:
            r_date = 0

    return(
        html_minify(
            template('index', 
                imp = [name, wiki_set(1), custom(), other2([sub + acl, r_date])],
                data = enddata + namumark(name, div, 0, 0, 0),
                menu = menu
            )
        )
    )

@route('/user/<name:path>/topic')
@route('/user/<name:path>/topic/<num:int>')
def user_topic_list(name = None, num = 1):
    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
    
    i = v - 50
    ydmin = admin_check(1, None)
    div =   '<table style="width: 100%; text-align: center;"> \
                <tbody> \
                    <tr> \
                        <td style="width: 33.3%;">토론명</td> \
                        <td style="width: 33.3%;">작성자</td> \
                        <td style="width: 33.3%;">시간</td> \
                    </tr>'

    div = '<a href="/record/' + url_pas(name) + '">(기여 기록)</a><br><br>' + div
    
    curs.execute("select title, id, sub, ip, date from topic where ip = ? order by date desc limit ?, ?", [name, str(i), str(v)])
    for data in curs.fetchall():
        title = html.escape(data[0])
        sub = html.escape(data[2])
            
        if(ydmin == 1):
            curs.execute("select * from ban where block = ?", [data[3]])
            if(curs.fetchall()):
                ban = ' <a href="/ban/' + url_pas(data[3]) + '">(해제)</a>'
            else:
                ban = ' <a href="/ban/' + url_pas(data[3]) + '">(차단)</a>'
        else:
            ban = ''
            
        ip = ip_pas(data[3])
            
        div += '<tr> \
                    <td> \
                        <a href="/topic/' + url_pas(data[0]) + '/sub/' + url_pas(data[2]) + '#' + data[1] + '">' + title + '#' + data[1] + '</a> (' + sub + ') \
                    </td> \
                    <td>' + ip + ban +  '</td> \
                    <td>' + data[4] + '</td> \
                </tr>'

    div += '</tbody></table>'
    div += '<br><a href="/user/' + url_pas(name) + '/topic/' + str(num - 1) + '">(이전)</a> <a href="/user/' + url_pas(name) + '/topic/' + str(num + 1) + '">(이후)</a>'
                
    curs.execute("select end, why from ban where block = ?", [name])
    ban_it = curs.fetchall()
    if(ban_it):
        sub = ' (차단)'
    else:
        sub = 0 
    
    return(
        html_minify(
            template('index', 
                imp = ['토론 기록', wiki_set(1), custom(), other2([sub, 0])],
                data = div,
                menu = [['other', '기타'], ['user', '사용자']]
            )
        )
    )
    
@route('/upload', method=['GET', 'POST'])
def upload():
    if(ban_check() == 1):
        return(re_error('/ban'))
    
    if(request.method == 'POST'):
        data = request.files.f_data
        if(not data):
            return(re_error('/error/9'))

        if(int(wiki_set(3)) * 1024 * 1024 < request.content_length):
            return re_error('/error/17')
        
        value = os.path.splitext(data.filename)[1]
        if(not value in ['.jpeg', '.jpg', '.gif', '.png', '.webp', '.JPEG', '.JPG', '.GIF', '.PNG', '.WEBP']):
            return re_error('/error/14')
    
        if(request.forms.get('f_name')):
            name = request.forms.get('f_name') + value
        else:
            name = data.filename
        
        piece = os.path.splitext(name)
        e_data = sha224(piece[0]) + piece[1]
            
        ip = ip_check()
        if(request.forms.get('f_lice')):
            lice = request.forms.get('f_lice')
        else:
            if(re.search('(?:\.|:)', ip)):
                lice = ip + ' 올림'
            else:
                lice = '[[사용자:' + ip + ']] 올림'
                
        if(os.path.exists(os.path.join('image', e_data))):
            return(re_error('/error/16'))
            
        data.save(os.path.join('image', e_data))
            
        curs.execute("select title from data where title = ?", ['파일:' + name])
        exist = curs.fetchall()
        if(exist): 
            curs.execute("delete from data where title = ?", ['파일:' + name])
        
        curs.execute("insert into data (title, data, acl) values (?, ?, 'admin')", ['파일:' + name, '[[파일:' + name + ']][br][br]{{{[[파일:' + name + ']]}}}[br][br]' + lice])
        history_plus('파일:' + name, '[[파일:' + name + ']][br][br]{{{[[파일:' + name + ']]}}}[br][br]' + lice, get_time(), ip, '(파일 올림)', '0')
        conn.commit()
        
        return(redirect('/w/파일:' + name))            
    else:
        return(
            html_minify(
                template('index', 
                    imp = ['파일 올리기', wiki_set(1), custom(), other2([0, 0])],
                    data =  '<form method="post" enctype="multipart/form-data" accept-charset="utf8"> \
                                <input type="file" name="f_data"> \
                                <br> \
                                <br> \
                                <input placeholder="파일 이름" name="f_name" type="text"> \
                                <br> \
                                <br> \
                                <input placeholder="라이선스" name="f_lice" type="text"> \
                                <br> \
                                <br> \
                                <span>한글이 되지 않을 때도 있습니다.</span> \
                                <br> \
                                <br> \
                                <button class="btn btn-primary" type="submit">저장</button> \
                            </form>',
                    menu = [['other', '기타']]
                )
            )
        )  
        
@route('/user')
def user_info():
    ip = ip_check()
    raw_ip = ip
    
    curs.execute("select acl from user where id = ?", [ip])
    data = curs.fetchall()
    if(ban_check() == 0):
        if(data):
            if(data[0][0] != 'user'):
                acl = data[0][0]
            else:
                acl = '가입자'
        else:
            acl = '일반'
    else:
        acl = '차단'
        
    ip = ip_pas(ip)

    l = custom()
    if(l[2] != 0):
        plus = ' * [[wiki:logout|로그아웃]]\r\n * [[wiki:change|비밀번호 변경]]'
    else:
        plus = ' * [[wiki:login|로그인]]'

    return(
        html_minify(
            template('index', 
                imp = ['사용자 메뉴', wiki_set(1), l, other2([0, 0])],
                data =  ip + '<br><br>' + namumark('',  '권한 상태 : ' + acl + '\r\n' + \
                                                        '[목차(없음)]\r\n' + \
                                                        '== 로그인 ==\r\n' + \
                                                        plus + '\r\n' + \
                                                        ' * [[wiki:register|회원가입]]\r\n' + \
                                                        '== 사용자 기능 ==\r\n' + \
                                                        ' * [[wiki:user_acl/' + url_pas(raw_ip) + '|사용자 문서 ACL]]\r\n' + \
                                                        ' * [[wiki:custom_css|사용자 CSS]]\r\n' + \
                                                        ' * [[wiki:custom_js|사용자 JS]]\r\n' + \
                                                        '== 기타 ==\r\n' + \
                                                        ' * [[wiki:alarm|알림]]\r\n' + \
                                                        ' * [[wiki:view_log|지나온 문서]]\r\n' + \
                                                        ' * [[wiki:count|기여 횟수]]\r\n', 0, 0, 0),
                menu = 0
            )
        )
    )

@route('/view_log')
def view_log():
    session = request.environ.get('beaker.session')
    data = '<ul>'
    if(session.get('View_List')):
        data += '<li>최근 50개</li><br><br>'
        m = re.findall('([^\n]+)\n', session.get('View_List'))
        for d in m:
            data += '<li><a href="/w/' + url_pas(d) + '">' + d + '</a></li>'
    else:
        data += '<li>기록 없음</li>'
    data += '</ul>'

    return(
        html_minify(
            template('index', 
                imp = ['지나온 문서', wiki_set(1), custom(), other2([0, 0])],
                data = data,
                menu = [['user', '사용자']]
            )
        )
    )

@route('/custom_css', method=['GET', 'POST'])
def custom_css_view():
    session = request.environ.get('beaker.session')
    ip = ip_check()
    if(request.method == 'POST'):
        if(not re.search('(\.|:)', ip)):
            curs.execute("select * from custom where user = ?", [ip])
            css_data = curs.fetchall()
            if(css_data):
                curs.execute("update custom set css = ? where user = ?", [request.forms.content, ip])
            else:
                curs.execute("insert into custom (user, css) values (?, ?)", [ip, request.forms.content])
            conn.commit()

        session['Daydream'] = request.forms.content

        return(redirect('/user'))
    else:
        if(not re.search('(\.|:)', ip)):
            start = ''
            curs.execute("select css from custom where user = ?", [ip])
            css_data = curs.fetchall()
            if(css_data):
                data = css_data[0][0]
            else:
                data = ''
        else:
            start = '<span>비 로그인의 경우에는 로그인하면 날아갑니다.</span><br><br>'
            try:
                data = session['Daydream']
            except:
                data = ''

        return(
            html_minify(
                template('index', 
                    imp = ['사용자 CSS', wiki_set(1), custom(), other2([0, 0])],
                    data =  start + ' \
                            <form method="post"> \
                                <textarea rows="30" cols="100" name="content">'\
                                     + data + \
                                '</textarea> \
                                <br> \
                                <br> \
                                <div class="form-actions"> \
                                    <button class="btn btn-primary" type="submit">저장</button> \
                                </div> \
                            </form>',
                    menu = [['user', '사용자']]
                )
            )
        )

@route('/custom_js', method=['GET', 'POST'])
def custom_js_view():
    session = request.environ.get('beaker.session')
    ip = ip_check()
    if(request.method == 'POST'):
        if(not re.search('(\.|:)', ip)):
            curs.execute("select * from custom where user = ?", [ip + ' (js)'])
            js_data = curs.fetchall()
            if(js_data):
                curs.execute("update custom set css = ? where user = ?", [request.forms.content, ip + ' (js)'])
            else:
                curs.execute("insert into custom (user, css) values (?, ?)", [ip + ' (js)', request.forms.content])
            conn.commit()
        session['AQUARIUM'] = request.forms.content

        return(redirect('/user'))
    else:
        if(not re.search('(\.|:)', ip)):
            start = ''
            curs.execute("select css from custom where user = ?", [ip + ' (js)'])
            js_data = curs.fetchall()
            if(js_data):
                data = js_data[0][0]
            else:
                data = ''
        else:
            start = '<span>비 로그인의 경우에는 로그인하면 날아갑니다.</span><br><br>'
            try:
                data = session['AQUARIUM']
            except:
                data = ''

        return(
            html_minify(
                template('index', 
                    imp = ['사용자 JS', wiki_set(1), custom(), other2([0, 0])],
                    data =  start + ' \
                            <form method="post"> \
                                <textarea rows="30" cols="100" name="content">'\
                                     + data + \
                                '</textarea> \
                                <br> \
                                <br> \
                                <div class="form-actions"> \
                                    <button class="btn btn-primary" type="submit">저장</button> \
                                </div> \
                            </form>',
                    menu = [['user', '사용자']]
                )
            )
        )

@route('/count')
@route('/count/<name:path>')
def count_edit(name = None):
    if(name == None):
        that = ip_check()
    else:
        that = name

    curs.execute("select count(title) from history where ip = ?", [that])
    count = curs.fetchall()
    if(count):
        data = count[0][0]
    else:
        data = 0

    curs.execute("select count(title) from topic where ip = ?", [that])
    count = curs.fetchall()
    if(count):
        t_data = count[0][0]
    else:
        t_data = 0

    return(
        html_minify(
            template('index', 
                imp = ['기여 횟수', wiki_set(1), custom(), other2([0, 0])],
                data = namumark("", "||<-2><:> " + that + " ||\r\n||<:> 기여 횟수 ||<:> " + str(data) + "||\r\n||<:> 토론 횟수 ||<:> " + str(t_data) + "||", 0, 0, 0),
                menu = [['user', '사용자']]
            )
        )
    )
        
@route('/random')
def random():
    curs.execute("select title from data order by random() limit 1")
    d = curs.fetchall()
    if(d):
        return(redirect('/w/' + url_pas(d[0][0])))
    else:
        return(redirect('/'))
    
@route('/views/<name:path>')
def views(name = None):
    if(re.search('\/', name)):
        m = re.search('^(.*)\/(.*)$', name)
        if(m):
            n = m.groups()
            plus = '/' + n[0]
            rename = n[1]
        else:
            plus = ''
            rename = name
    else:
        plus = ''
        rename = name
        
    return(
        static_file(rename, 
            root = './views' + plus
        )
    )

@error(404)
def error_404(error):
    try:
        curs.execute("select title from data limit 1")
        return('<!-- 나니카가 하지마룻테 코토와 오와리니 츠나가루다난테 캉가에테모 미나캇타. 이야, 캉카에타쿠나캇탄다... 아마오토 마도오 타타쿠 소라카라 와타시노 요-나 카나시미 훗테루 토메도나쿠 이마오 누라시테 오모이데 난테 이라나이노 코코로가 쿠루시쿠나루 다케다토 No more! September Rain No more! September Rain 이츠닷테 아나타와 미짓카닷타 와자와자 키모치오 타시카메룻테 코토모 히츠요-쟈나쿠테 시젠니 나카라요쿠 나레타카라 안신시테타노 카모시레나이네 도-시테? 나미니 토이카케루케도 나츠노 하지마리가 츠레테키타 오모이 나츠가 오와루토키 키에챠우모노닷타 난테 시라나쿠테 토키메이테타 아츠이 키세츠 우미베노 소라가 히캇테 토츠젠 쿠모가 나가레 오츠부노 아메 와타시노 나카노 나미다미타이 콘나니 타노시이 나츠가 즛토 츠즈이테쿳테 신지테타요 But now... September Rain But now... September Rain -->' + redirect('/w/' + url_pas(wiki_set(2))))
    except:
        return('<!-- 토오쿠 츠즈이테루 우미노사키니와 돈나 나츠가 아루노다로? 이츠카 타시카메타이 키모치모 아루케레도 팟토하데쟈나이 데모 코노우미와 즛또 와타시타치노코토오 이츠모 미테테쿠레따 요로코비모 나미다모 싯떼루노 무카시카라노 하마베 아사와 마다 츠메타쿠떼 아시가 빗쿠리시떼루요 미즈노나카 오사카나니 츠츠카레챳따? 난다카 타노시이네 잇쇼노 나츠와 코코데 스고소우요 오야스미 키분데 요세떼 카에스 나미노 코에 잇쇼니 키키타이나 농비리스루노모 이이데쇼? 타마니와 이키누키시나쿠챠 스나오 사쿠사쿠 후미나가라 오샤베리시요우요 호랏 지모토지만노 사마 라이후 -->' + redirect('/setup'))

@error(500)
def error_500(error):
    try:
        curs.execute("select title from data limit 1")
        return('<!-- Splash, Spark, and Shining the Summer! 코코데맛떼나이데 잇쇼니코나캬, 다! Summer time (Oh ya! Summer time!!) 톤데모나이 나츠니나리소오 키미모카쿠고와 데키타카나? 히토리맛떼타라 앗토이우마니 바이바이 Summer time (Oh ya! Summer time!!) 오이데카레루노가 키라이나라 스구니오이데요 코코로우키우키 우키요노도리-무 비-치 세카이데 보우켄시요오 "보-옷"토 스키챠못타이나이 "규-웃"토 코이지칸가호시이? 닷타라(Let\'s go!) 닷타라(Let\'s go!) 코토시와 이치도키리사 아소보오 Splash! (Splash!!) 토비콘다 우미노아오사가(Good feeling) 오와라나이 나츠에노 토비라오 유메밋테루토 싯테루카이? 아소보오 Splash! (Splash!!) 토비콘데 미세타아토 키미가 타메랏테루(나라바) 요우샤나쿠 Summer Summer Summer에 츠레텟챠우카라! -->' + redirect('/w/' + url_pas(wiki_set(2))))
    except:
        return('<!-- 아카이 타이요노 도레스데 오도루 와타시노 코토 미츠메테이루노 메오 소라시타이 데모 소라세나이 아아 죠네츠데 야카레타이 도키메키 이죠노 리즈무 코요이 시리타쿠테 이츠모요리 타이탄나 코토바오 츠부야이타 지분노 키모치나노니 젠젠 와카라나쿠 (낫챠이타이나) 리세이카라 시레이가 (토도카나이) 콘토로-루 후카노 손나 코이오 시타놋테 코에가 토도이테시맛타 하즈카시잇테 오모우케도 못토 시리타이노 못토 시리타이노 이케나이 유메다토 키즈키나가라 아카이 타이요노 도레스데 오도루 와타시노 코토 미츠메루 히토미 메오 소라시타이 데모 소라세나이 마나츠와 다레노 모노 아나타토 와타시노 모노니시타이 (닷테네) 코코로가 토마레나이 키세츠니 하지메테 무네노 토비라가 아이테 시마이소오요 You knock knock my heart!! -->' + redirect('/setup'))
    
run(app = app, server = 'tornado', host = '0.0.0.0', port = int(set_data['port']))
