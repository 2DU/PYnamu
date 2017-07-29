﻿from bottle import route, run, template, error, request, static_file, app, BaseRequest
from bottle.ext import beaker
import bcrypt
import os
import difflib
import hashlib
import json
import pymysql

json_data = open('set.json').read()
set_data = json.loads(json_data)

session_opts = {
    'session.type': 'file',
    'session.data_dir': './app_session/',
    'session.auto': True
}

app = beaker.middleware.SessionMiddleware(app(), session_opts)

BaseRequest.MEMFILE_MAX = 1024 * 1024

def redirect(data):
    return('<meta http-equiv="refresh" content="0;url=' + data + '" />')
    
from func import *
from mark import *
    
db_pas = pymysql.escape_string

r_ver = '2.1.3'

@route('/setup', method=['GET', 'POST'])
def setup():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4')
    curs = conn.cursor(pymysql.cursors.DictCursor)
    
    if(request.method == 'POST'):            
        if(not request.forms.owner == set_data['pw']):            
            conn.close()
            return(redirect('/error/3'))
        else:
            try:
                curs.execute("use " + set_data['db'])
            except:
                curs.execute("create database " + set_data['db'])
                curs.execute("use " + set_data['db'])
                curs.execute("alter database " + set_data['db'] + " character set = utf8mb4 collate = utf8mb4_unicode_ci")    
        
            curs.execute("create table data(title text, data longtext, acl text)")
            curs.execute("create table history(id text, title text, data longtext, date text, ip text, send text, leng text)")
            curs.execute("create table rd(title text, sub text, date text)")
            curs.execute("create table user(id text, pw text, acl text)")
            curs.execute("create table ban(block text, end text, why text, band text)")
            curs.execute("create table topic(id text, title text, sub text, data longtext, date text, ip text, block text, top text)")
            curs.execute("create table stop(title text, sub text, close text)")
            curs.execute("create table rb(block text, end text, today text, blocker text, why text)")
            curs.execute("create table login(user text, ip text, today text)")
            curs.execute("create table back(title text, link text, type text)")
            curs.execute("create table cat(title text, cat text)")
            curs.execute("create table hidhi(title text, re text)")
            curs.execute("create table agreedis(title text, sub text)")
            curs.execute("create table custom(user text, css longtext)")
            curs.execute("create table other(name text, data text)")
            curs.execute("create table alist(name text, acl text)")

            conn.close()
            return(redirect('/'))
    else:
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = '<form method="POST"><input name="owner" type="password"> <button class="btn btn-primary" type="submit">저장</button></form>', title = '오픈나무 설치'))

@route('/upload', method=['GET', 'POST'])
def upload():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)
    
    MEMFILE_MAX = int(set_data['upload']) * 1024 * 1024
    
    ip = ip_check()
    ban = ban_check(ip)
    
    if(request.method == 'POST'):        
        if(ban == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            file = request.files.file
            if(file):
                comp = re.compile("^(.+)(\.(?:jpg|gif|png|jpeg))$", re.I)
                exist = comp.search(file.filename)
                if(exist):
                    if((int(set_data['upload']) * 1024 * 1024) < request.content_length):
                        conn.close()
                        return(redirect('/error/17'))
                    else:
                        file_info = exist.groups()

                        file_data = file_info[0] + file_info[1]
                        file_name = sha224(file_info[0]) + file_info[1]
                                           
                        if(os.path.exists(os.path.join('image', file_name))):
                            conn.close()
                            return(redirect('/error/16'))
                        else:
                            file.save(os.path.join('image', file_name))
                            
                            curs.execute("select title from data where title = '" + db_pas('파일:' + file_data) + "'")
                            exist_db = curs.fetchall()
                            if(not exist_db):
                                curs.execute("insert into data (title, data, acl) value ('" + db_pas('파일:' + file_data) + "', '" + db_pas('[[파일:' + file_data + ']][br][br]{{{[[파일:' + file_data + ']]}}}') + "', '')")
                                conn.commit()
                            
                            history_plus('파일:' + file_data, '[[파일:' + file_data + ']][br][br]{{{[[파일:' + file_data + ']]}}}', get_time(), ip, '파일:' + file_data + ' 업로드', '0')
                            
                            conn.close()
                            return(redirect('/w/' + url_pas('파일:' + file_data)))
                else:
                    conn.close()
                    return(redirect('/error/14'))
            else:
                conn.close()
                return(redirect('/error/14'))
    else:        
        if(ban == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            conn.close()
            return(template('upload', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], title = '업로드', number = set_data['upload']))

@route('/image/<name:path>')
def static(name = None):
    if(os.path.exists(os.path.join('image', name))):
        return(static_file(name, root = 'image'))
    else:
        return(redirect('/'))

@route('/acllist')
def acl_list():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    div = '<div>'
    i = 0

    curs.execute("select title, acl from data where acl = 'admin' or acl = 'user' order by acl desc")
    list_data = curs.fetchall()
    if(list_data):
        for data in list_data:
            if(data['acl'] == 'admin'):
                acl = '관리자'
            else:
                acl = '로그인'

            div += '<li>' + str(i + 1) + '. <a href="/w/' + url_pas(data['title']) + '">' + data['title'] + '</a> (' + acl + ')</li>'
            
            i += 1
        else:
            div += '</div>'
    else:
        div = ''

    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = 'ACL 문서 목록'))
    
@route('/listacl')
def list_acl():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    div = '<div>'
    i = 0

    curs.execute("select * from alist order by name desc")
    list_data = curs.fetchall()
    if(list_data):
        for data in list_data:
            if(data['acl'] == 'ban'):
                acl = '차단'
            elif(data['acl'] == 'mdel'):
                acl = '많은 문서 삭제'
            elif(data['acl'] == 'toron'):
                acl = '토론 관리'
            elif(data['acl'] == 'check'):
                acl = '사용자 검사'
            elif(data['acl'] == 'acl'):
                acl = '문서 ACL'
            elif(data['acl'] == 'hidel'):
                acl = '역사 숨김'
            elif(data['acl'] == 'owner'):
                acl = '소유자'
                
            div += '<li>' + str(i + 1) + '. <a href="/adminplus/' + url_pas(data['name']) + '">' + data['name'] + '</a> (' + acl + ')</li>'
            
            i += 1
        else:        
            div += '<br><a href="/manager/8">(생성)</a></div>'
    else:
        div = '<a href="/manager/8">(생성)</a></div>'

    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = 'ACL 목록'))

@route('/adminplus/<name:path>', method=['POST', 'GET'])
def admin_plus(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(None) == 1):
        if(request.method == 'POST'):
            curs.execute("delete from alist where name = '" + db_pas(name) + "'")
            
            if(request.forms.ban):
                curs.execute("insert into alist (name, acl) value ('" + db_pas(name) + "', 'ban')")
            if(request.forms.mdel):
                curs.execute("insert into alist (name, acl) value ('" + db_pas(name) + "', 'mdel')")    
            if(request.forms.toron):
                curs.execute("insert into alist (name, acl) value ('" + db_pas(name) + "', 'toron')")
            if(request.forms.check):
                curs.execute("insert into alist (name, acl) value ('" + db_pas(name) + "', 'check')")
            if(request.forms.acl):
                curs.execute("insert into alist (name, acl) value ('" + db_pas(name) + "', 'acl')")
            if(request.forms.hidel):
                curs.execute("insert into alist (name, acl) value ('" + db_pas(name) + "', 'hidel')")
            if(request.forms.owner):
                curs.execute("insert into alist (name, acl) value ('" + db_pas(name) + "', 'owner')")
                
            conn.commit()
            conn.close()
            return(redirect('/adminplus/admin'))
        else:
            curs.execute('select acl from alist where name = "' + db_pas(name) + '"')
            test = curs.fetchall()
            
            list = ''
            exist_list = ['', '', '', '', '', '', '', '', '']

            for go in test:
                if(go['acl'] == 'ban'):
                    exist_list[0] = 'checked="checked"'
                elif(go['acl'] == 'mdel'):
                    exist_list[1] = 'checked="checked"'
                elif(go['acl'] == 'toron'):
                    exist_list[2] = 'checked="checked"'
                elif(go['acl'] == 'check'):
                    exist_list[3] = 'checked="checked"'
                elif(go['acl'] == 'acl'):
                    exist_list[4] = 'checked="checked"'
                elif(go['acl'] == 'hidel'):
                    exist_list[5] = 'checked="checked"'
                elif(go['acl'] == 'owner'):
                    exist_list[7] = 'checked="checked"'

            list += '<li><input type="checkbox" name="ban" ' + exist_list[0] + '> 차단</li>'
            list += '<li><input type="checkbox" name="mdel" ' + exist_list[1] + '> 많은 문서 삭제</li>'
            list += '<li><input type="checkbox" name="toron" ' + exist_list[2] + '> 토론 관리</li>'
            list += '<li><input type="checkbox" name="check" ' + exist_list[3] + '> 사용자 검사</li>'
            list += '<li><input type="checkbox" name="acl" ' + exist_list[4] + '> 문서 ACL</li>'
            list += '<li><input type="checkbox" name="hidel" ' + exist_list[5] + '> 역사 숨김</li>'
            list += '<li><input type="checkbox" name="owner" ' + exist_list[7] + '> 소유자</li>'
            
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '관리 그룹 추가', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/adminplus/' + url_pas(name) + '">' + list + '<div class="form-actions"><button class="btn btn-primary" type="submit">저장</button></div></form>'))
    else:
        conn.close()
        return(redirect('/error/3'))
        
@route('/adminlist')
def admin_list():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    i = 1
    div = '<div>'
    
    curs.execute("select * from user where acl = 'admin' or acl = 'owner'")
    user_data = curs.fetchall()
    if(user_data):
        for data in user_data:
            name = ip_pas(data['id'], 2)
            name += ' (' + data['acl'] + ')'

            div += '<li>' + str(i) + '. ' + name + '</li>'
            
            i += 1
        else:
            div += '</div>'
                
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = '관리자 목록'))
    else:
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], title = '관리자 목록'))
        
@route('/recentchanges')
def recentchanges():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ydmin = admin_check(1)
    zdmin = admin_check(6)
    div = '<div><table style="width: 100%;"><tbody><tr><td style="text-align: center;width:33.33%;">문서명</td><td style="text-align: center;width:33.33%;">기여자</td><td style="text-align: center;width:33.33%;">시간</td></tr>'
    
    curs.execute("select id, title, date, ip, send, leng from history order by date desc limit 50")
    rows = curs.fetchall()
    if(rows):
        for data in rows:                
            if(data['send']):
                if(re.search("^(?: *)$", data['send'])):
                    send = '<br>'
                else:
                    send = data['send']
            else:
                send = '<br>'
                
            title = data['title']
            title = re.sub('<', '&lt;', title)
            title = re.sub('>', '&gt;', title)
            title = re.sub('"', '&quot;', title)
            
            m = re.search("\+", data['leng'])
            n = re.search("\-", data['leng'])
            
            if(m):
                leng = '<span style="color:green;">' + data['leng'] + '</span>'
            elif(n):
                leng = '<span style="color:red;">' + data['leng'] + '</span>'
            else:
                leng = '<span style="color:gray;">' + data['leng'] + '</span>'
                
            if(ydmin == 1):
                curs.execute("select * from ban where block = '" + db_pas(data['ip']) + "'")
                row = curs.fetchall()
                if(row):
                    ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(해제)</a>'
                else:
                    ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(차단)</a>'
            else:
                ban = ''
                
            ip = ip_pas(data['ip'], None)
                    
            if((int(data['id']) - 1) == 0):
                revert = ''
            else:
                revert = '<a href="/w/' + url_pas(data['title']) + '/r/' + str(int(data['id']) - 1) + '/diff/' + data['id'] + '">(비교)</a> <a href="/revert/' + url_pas(data['title']) + '/r/' + str(int(data['id']) - 1) + '">(되돌리기)</a>'
            
            style = ''
            if(zdmin == 1):
                curs.execute("select * from hidhi where title = '" + db_pas(data['title']) + "' and re = '" + db_pas(data['id']) + "'")
                row = curs.fetchall()
                if(row):                            
                    ip += ' (숨김)'                            
                    hidden = ' <a href="/history/' + url_pas(data['title']) + '/r/' + data['id'] + '/hidden">(공개)'
                else:
                    hidden = ' <a href="/history/' + url_pas(data['title']) + '/r/' + data['id'] + '/hidden">(숨김)'
            else:
                curs.execute("select * from hidhi where title = '" + db_pas(data['title']) + "' and re = '" + db_pas(data['id']) + "'")
                row = curs.fetchall()
                if(row):
                    ip = '숨김'
                    hidden = ''
                    send = '숨김'
                    ban = ''
                    style = 'display:none;'
                else:
                    hidden = ''      
                
            div += '<tr style="' + style + '"><td style="text-align: center;width:33.33%;"><a href="/w/' + url_pas(data['title']) + '">' + title + '</a> (<a href="/history/' + url_pas(data['title']) + '">' + data['id'] + '판</a>) ' + revert + ' (' + leng + ')</td><td style="text-align: center;width:33.33%;">' + ip + ban + hidden + '</td><td style="text-align: center;width:33.33%;">' + data['date'] + '</td></tr><tr><td colspan="3" style="text-align: center;width:100%;">' + send + '</td></tr>'
        else:
            div += '</tbody></table></div>'
    else:
        div = 'None'
            
    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = '최근 변경내역'))
        
@route('/history/<name:path>/r/<num:int>/hidden')
def history_hidden(name = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(6) == 1):
        curs.execute("select * from hidhi where title = '" + db_pas(name) + "' and re = '" + db_pas(str(num)) + "'")
        exist = curs.fetchall()
        if(exist):
            curs.execute("delete from hidhi where title = '" + db_pas(name) + "' and re = '" + db_pas(str(num)) + "'")
        else:
            curs.execute("insert into hidhi (title, re) value ('" + db_pas(name) + "', '" + db_pas(str(num)) + "')")
            
        conn.commit()
        
    conn.close()
    return(redirect('/history/' + url_pas(name)))

@route('/record/<name:path>')
@route('/record/<name:path>/n/<num:int>')
def user_record(name = None, num = 1):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
        
    i = v - 50
    ydmin = admin_check(1)
    zdmin = admin_check(6)
    div = '<div><table style="width: 100%;"><tbody><tr><td style="text-align: center;width:33.33%;">문서명</td><td style="text-align: center;width:33.33%;">기여자</td><td style="text-align: center;width:33.33%;">시간</td></tr>'
    
    curs.execute("select * from history where ip = '" + db_pas(name) + "' order by date desc limit " + str(i) + ", " + str(v))
    rows = curs.fetchall()
    if(rows):
        for data in rows:  
            if(data['send']):
                send = data['send']
                send = re.sub('<a href="\/w\/(?P<in>[^"]*)">(?P<out>[^&]*)<\/a>', '<a href="/w/\g<in>">\g<out></a>', send)
            else:
                send = '<br>'
                
            title = data['title']
            title = re.sub('<', '&lt;', title)
            title = re.sub('>', '&gt;', title)
            title = re.sub('"', '&quot;', title)
            
            m = re.search("\+", data['leng'])
            n = re.search("\-", data['leng'])
            
            if(m):
                leng = '<span style="color:green;">' + data['leng'] + '</span>'
            elif(n):
                leng = '<span style="color:red;">' + data['leng'] + '</span>'
            else:
                leng = '<span style="color:gray;">' + data['leng'] + '</span>'
                
            if(ydmin == 1):
                curs.execute("select * from ban where block = '" + db_pas(data['ip']) + "'")
                row = curs.fetchall()
                if(row):
                    ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(해제)</a>'
                else:
                    ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(차단)</a>'
            else:
                ban = ''
                
            ip = ip_pas(data['ip'], None)
                    
            if((int(data['id']) - 1) == 0):
                revert = ''
            else:
                revert = '<a href="/revert/' + url_pas(data['title']) + '/r/' + str(int(data['id']) - 1) + '">(되돌리기)</a>'
                
            style = ''
            if(zdmin == 1):
                curs.execute("select * from hidhi where title = '" + db_pas(data['title']) + "' and re = '" + db_pas(data['id']) + "'")
                row = curs.fetchall()
                if(row):                            
                    ip += ' (숨김)'                            
                    hidden = ' <a href="/history/' + url_pas(data['title']) + '/r/' + data['id'] + '/hidden">(공개)'
                else:
                    hidden = ' <a href="/history/' + url_pas(data['title']) + '/r/' + data['id'] + '/hidden">(숨김)'
            else:
                curs.execute("select * from hidhi where title = '" + db_pas(data['title']) + "' and re = '" + db_pas(data['id']) + "'")
                row = curs.fetchall()
                if(row):
                    ip = '숨김'
                    hidden = ''
                    send = '숨김'
                    ban = ''
                    style = 'display:none;'
                else:
                    hidden = ''
                
            div += '<tr style="' + style + '"><td style="text-align: center;width:33.33%;"><a href="/w/' + url_pas(data['title']) + '">' + title + '</a> (<a href="/history/' + url_pas(data['title']) + '">' + data['id'] + '판</a>) <a href="/w/' + url_pas(data['title']) + '/r/' + str(int(data['id']) - 1) + '/diff/' + data['id'] + '">(비교)</a> ' + revert + ' (' + leng + ')</td><td style="text-align: center;width:33.33%;">' + ip + ban + hidden + '</td><td style="text-align: center;width:33.33%;">' + data['date'] + '</td></tr><tr><td colspan="3" style="text-align: center;width:100%;">' + send + '</td></tr>'
        else:
            div += '</tbody></table></div>'
    else:
        div = 'None<br>'
        
    div += '<br><a href="/record/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/record/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'
        
    curs.execute("select end, why from ban where block = '" + db_pas(name) + "'")
    ban_it = curs.fetchall()
    if(ban_it):
        div = namumark('', '{{{#!wiki style="border:2px solid red;padding:10px;"\r\n{{{+2 {{{#red 이 사용자는 차단 당했습니다.}}}}}}\r\n\r\n차단 해제 일 : ' + ban_it[0]['end'] + '[br]사유 : ' + ban_it[0]['why'] + '}}}') + '<br>' + div
                
    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = '사용자 기록'))
        
@route('/userlog')
@route('/userlog/n/<num:int>')
def user_log(num = 1):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(num * 50 <= 0):
         i = 50
    else:
        i = num * 50
        
    j = i - 50
    list_data = ''
    ydmin = admin_check(1)
    
    curs.execute("select * from user limit " + str(j) + ", " + str(i))
    user_list = curs.fetchall()
    if(user_list):        
        for data in user_list:
            if(ydmin == 1):
                curs.execute("select * from ban where block = '" + db_pas(data['id']) + "'")
                ban_exist = curs.fetchall()
                if(ban_exist):
                    ban_button = ' <a href="/ban/' + url_pas(data['id']) + '">(해제)</a>'
                else:
                    ban_button = ' <a href="/ban/' + url_pas(data['id']) + '">(차단)</a>'
            else:
                ban_button = ''
                
            ip = ip_pas(data['id'], None)
                
            list_data += '<li>' + str(j + 1) + '. ' + ip + ban_button + '</li>'
            
            j += 1

        list_data += '<br><a href="/userlog/n/' + str(num - 1) + '">(이전)</a> <a href="/userlog/n/' + str(num + 1) + '">(이후)</a>'
                
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = list_data, title = '사용자 가입 기록'))
    else:
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = '', title = '사용자 가입 기록'))
        
@route('/backreset')
def xref_reset():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(None) == 1):
        i = 0
        
        curs.execute("delete from back")
        conn.commit()
        
        curs.execute("select title, data from data")
        all = curs.fetchall()
        if(all):
            for data in all:
                namumark(data['title'], data['data'])
        
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = '에러 없음', title = '완료'))
    else:
        conn.close()
        return(redirect('/error/3'))
        
@route('/xref/<name:path>')
@route('/xref/<name:path>/n/<num:int>')
def xref(name = None, num = 1):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
        
    i = v - 50
    div = ''
    
    curs.execute("delete from back where title = '" + db_pas(name) + "' and link = ''")
    conn.commit()
    
    curs.execute("select * from back where title = '" + db_pas(name) + "' order by link asc")
    rows = curs.fetchall()
    if(rows):        
        for data in rows:
            div += '<li><a href="/w/' + url_pas(data['link']) + '">' + data['link'] + '</a>'
            
            if(data['type']):
                div += ' (' + data['type'] + ')</li>'
            else:
                div += '</li>'
                
        div += '<br><a href="/xref/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/xref/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'

        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = name, page = url_pas(name), sub = '역링크'))
    else:
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = 'None', title = name, page = url_pas(name), sub = '역링크'))
        
@route('/recentdiscuss')
def recentdiscuss():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    div = '<div><table style="width: 100%;"><tbody><tr><td style="text-align: center;width:50%;">토론명</td><td style="text-align: center;width:50%;">시간</td></tr>'
    
    curs.execute("select * from rd order by date desc limit 50")
    rows = curs.fetchall()
    if(rows):
        for data in rows:
            title = data['title']
            title = re.sub('<', '&lt;', title)
            title = re.sub('>', '&gt;', title)
            title = re.sub('"', '&quot;', title)
            
            sub = data['sub']
            sub = re.sub('<', '&lt;', sub)
            sub = re.sub('>', '&gt;', sub)
            sub = re.sub('"', '&quot;', sub)
            
            div += '<tr><td style="text-align: center;width:50%;"><a href="/topic/' + url_pas(data['title']) + '/sub/' + url_pas(data['sub']) + '">' + title + '</a> (' + sub + ')</td><td style="text-align: center;width:50%;">' + data['date'] + '</td></tr>'
        else:
            div += '</tbody></table></div>'
    else:
        div = 'None'
            
    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = '최근 토론내역'))

@route('/blocklog')
@route('/blocklog/n/<number:int>')
def blocklog(num = 1):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
    
    i = v - 50
    div = '<div><table style="width: 100%;"><tbody><tr><td style="text-align: center;width:20%;">차단자</td><td style="text-align: center;width:20%;">관리자</td><td style="text-align: center;width:20%;">기간</td><td style="text-align: center;width:20%;">이유</td><td style="text-align: center;width:20%;">시간</td></tr>'
    
    curs.execute("select * from rb order by today desc")
    rows = curs.fetchall()
    if(rows):
        for data in rows:
            why = data['why']
            why = re.sub('<', '&lt;', why)
            why = re.sub('>', '&gt;', why)
            why = re.sub('"', '&quot;', why)
            
            b = re.search("^([0-9]{1,3}\.[0-9]{1,3})$", data['block'])
            if(b):
                ip = data['block'] + ' (대역)'
            else:
                ip = data['block']
                
            div += '<tr><td style="text-align: center;width:20%;">' + ip + '</a></td><td style="text-align: center;width:20%;">' + data['blocker'] + '</td><td style="text-align: center;width:20%;">' + data['end'] + '</td><td style="text-align: center;width:20%;">' + data['why'] + '</td><td style="text-align: center;width:20%;">' + data['today'] + '</td></tr>'
        else:
            div += '</tbody></table></div>'
    else:
        div = 'None'
                
    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = '사용자 차단 기록'))

@route('/history/<name:path>', method=['POST', 'GET'])    
@route('/history/<name:path>/n/<num:int>', method=['POST', 'GET'])
def history_view(name = None, num = 1):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(request.method == 'POST'):
        conn.close()
        return(redirect('/w/' + url_pas(name) + '/r/' + request.forms.b + '/diff/' + request.forms.a))
    else:
        select = ''
        num1 = 0
        num2 = 0
        curs.execute("select id from history where title = '" + db_pas(name) + "' order by id + 0 desc limit 1")
        end_num = curs.fetchall()
        if(end_num):
            num1 = int(end_num[0]['id']) - num * 50
            if(num1 > 0):
                num2 = num1 + 51
            else:
                if(num1 + 51 > 0):
                    num2 = num1 + 51
 
        admin1 = admin_check(1)
        admin2 = admin_check(6)
        
        div = '<div><table style="text-align:center; width:100%;"><tbody><tr><td style="width:33.33%;">판</td><td style="width:33.33%;">기여자</td><td style="width:33.33%;">시간</td></tr>'
        
        curs.execute("select send, leng, ip, date, title, id from history where title = '" + db_pas(name) + "' and id + 0 < '" + str(num2) + "' and id + 0 > '" + str(num1) + "' order by id + 0 desc")
        all_data = curs.fetchall()
        if(all_data):
            for data in all_data:
                select += '<option value="' + data['id'] + '">' + data['id'] + '</option>'
                
                if(data['send']):
                    send = data['send']
                else:
                    send = '<br>'
                    
                if(re.search("^\+", data['leng'])):
                    leng = '<span style="color:green;">' + data['leng'] + '</span>'
                elif(re.search("^\-", data['leng'])):
                    leng = '<span style="color:red;">' + data['leng'] + '</span>'
                else:
                    leng = '<span style="color:gray;">' + data['leng'] + '</span>'
                    
                ip = ip_pas(data['ip'], None)
                
                curs.execute("select block from ban where block = '" + db_pas(data['ip']) + "'")
                ban_it = curs.fetchall()
                if(ban_it):
                    if(admin1 == 1):
                        ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(해제)</a>'
                    else:
                        ban = ' (X)'
                else:
                    if(admin1 == 1):
                        ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(차단)</a>'
                    else:
                        ban = ''
                
                curs.execute("select * from hidhi where title = '" + db_pas(name) + "' and re = '" + db_pas(data['id']) + "'")
                hid_it = curs.fetchall()
                if(hid_it):
                    if(admin2):
                        hidden = ' <a href="/history/' + url_pas(name) + '/r/' + url_pas(data['id']) + '/hidden">(공개)'
                        hid = 0
                    else:
                        hid = 1
                else:
                    if(admin2):
                        hidden = ' <a href="/history/' + url_pas(name) + '/r/' + url_pas(data['id']) + '/hidden">(숨김)'
                        hid = 0
                    else:
                        hidden = ''
                        hid = 0
                
                if(hid == 1):
                    div += '<tr><td colspan="3">숨김</td></tr>'
                else:
                    div += '<tr><td>' + data['id'] + '판</a> <a href="/w/' + url_pas(data['title']) + '/r/' + url_pas(data['id']) + '">(보기)</a> <a href="/w/' + url_pas(data['title']) + '/raw/' + url_pas(data['id']) + '">(원본)</a> <a href="/revert/' + url_pas(data['title']) + '/r/' + url_pas(data['id']) + '">(되돌리기)</a> (' + leng + ')</td><td>' + ip + ban + hidden + '</td><td>' + data['date'] + '</td></tr><tr><td colspan="3">' + send + '</td></tr>'
            else:
                div += '</tbody></table></div>'
        else:
            div = 'None<br>'
            
        div += '<br><a href="/history/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/history/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'
                    
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = name, page = url_pas(name), select = select, sub = '역사'))
            
@route('/search', method=['POST'])
def search():
    return(redirect('/search/' + url_pas(request.forms.search)))

@route('/goto', method=['POST'])
def goto():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select title from data where title = '" + db_pas(request.forms.search) + "'")
    data = curs.fetchall()
    
    conn.close()
    
    if(data):
        return(redirect('/w/' + url_pas(request.forms.search)))
    else:
        return(redirect('/search/' + url_pas(request.forms.search)))

@route('/search/<name:path>')
@route('/search/<name:path>/n/<num:int>')
def deep_search(name = None, num = 1):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(num * 50 <= 0):
        v = num * 50
    else:
        v = 50

    i = v - 50

    div = ''
    div_plus = ''
    end = ''

    curs.execute("select title from data where title like '%" + db_pas(name) + "%'")
    title_list = curs.fetchall()

    curs.execute("select title from data where data like '%" + db_pas(name) + "%'")
    data_list = curs.fetchall()

    curs.execute("select title from data where title = '" + db_pas(name) + "'")
    exist = curs.fetchall()
    if(exist):
        div = '<li>문서로 <a href="/w/' + url_pas(name) + '">바로가기</a></li><br>'
    else:
        div = '<li>문서가 없습니다. <a class="not_thing" href="/w/' + url_pas(name) + '">바로가기</a></li><br>'

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
    
    if(not all_list == ''):
        for data in all_list:
            re_title = re.compile(name, re.I)
            if(re.search(re_title, data['title'])):
                if(no == 0):
                    div += '<li><a href="/w/' + url_pas(data['title']) + '">' + data['title'] + '</a> (문서명)</li>'
                else:
                    div_plus += '<li><a href="/w/' + url_pas(data['title']) + '">' + data['title'] + '</a> (내용)</li>'
            else:
                no = 1

                div_plus += '<li><a href="/w/' + url_pas(data['title']) + '">' + data['title'] + '</a> (내용)</li>'
    else:
        div += '<li>검색 결과 없음</li>'

    div += div_plus + end

    div += '<br><a href="/search/' + url_pas(name) + '/n/' + str(num - 1) + '">(이전)</a> <a href="/search/' + url_pas(name) + '/n/' + str(num + 1) + '">(이후)</a>'

    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = name, sub = '검색'))
        
@route('/w/<name:path>/r/<num:int>')
def old_view(name = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select * from hidhi where title = '" + db_pas(name) + "' and re = '" + db_pas(str(num)) + "'")
    row = curs.fetchall()
    if(row):
        if(admin_check(6) == 1):
            curs.execute("select * from history where title = '" + db_pas(name) + "' and id = '" + str(num) + "'")
            rows = curs.fetchall()
            if(rows):
                conn.close()
                return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = namumark(name, rows[0]['data']), sub = '옛 문서'))
            else:
                conn.close()
                return(redirect('/history/' + url_pas(name)))
        else:
            conn.close()
            return(redirect('/error/3'))
    else:
        curs.execute("select * from history where title = '" + db_pas(name) + "' and id = '" + str(num) + "'")
        rows = curs.fetchall()
        if(rows):
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = namumark(name, rows[0]['data']), sub = '옛 문서'))
        else:
            conn.close()
            return(redirect('/history/' + url_pas(name)))
            
@route('/w/<name:path>/raw/<num:int>')
def old_raw(name = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select * from hidhi where title = '" + db_pas(name) + "' and re = '" + db_pas(str(num)) + "'")
    row = curs.fetchall()
    if(row):
        if(not admin_check(6) == 1):
            conn.close()
            return(redirect('/error/3'))

    curs.execute("select * from history where title = '" + db_pas(name) + "' and id = '" + str(num) + "'")
    rows = curs.fetchall()
    if(rows):
        enddata = re.sub('<', '&lt;', rows[0]['data'])
        enddata = re.sub('>', '&gt;', enddata)
        enddata = re.sub('"', '&quot;', enddata)
        
        enddata = '<textarea id="other_text">' + enddata + '</textarea>'
        
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = enddata, sub = '옛 원본'))
    else:
        conn.close()
        return(redirect('/history/' + url_pas(name)))
            
@route('/raw/<name:path>')
def raw_view(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select * from data where title = '" + db_pas(name) + "'")
    rows = curs.fetchall()
    if(rows):
        enddata = re.sub('<', '&lt;', rows[0]['data'])
        enddata = re.sub('>', '&gt;', enddata)
        enddata = re.sub('"', '&quot;', enddata)
        
        enddata = '<textarea id="other_text">' + enddata + '</textarea>'
        
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = enddata, sub = '원본'))
    else:
        conn.close()
        return(redirect('/w/' + url_pas(name)))
        
@route('/revert/<name:path>/r/<num:int>', method=['POST', 'GET'])
def revert(name = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    can = acl_check(ip, name)
    today = get_time()
    
    if(request.method == 'POST'):
        curs.execute("select * from hidhi where title = '" + db_pas(name) + "' and re = '" + db_pas(str(num)) + "'")
        row = curs.fetchall()
        if(row):
            if(admin_check(6) == 1):        
                curs.execute("select * from history where title = '" + db_pas(name) + "' and id = '" + str(num) + "'")
                rows = curs.fetchall()
                if(rows):
                    if(can == 1):
                        conn.close()
                        return(redirect('/ban'))
                    else:
                        curs.execute("select * from data where title = '" + db_pas(name) + "'")
                        row = curs.fetchall()
                        if(row):
                            leng = leng_check(len(row[0]['data']), len(rows[0]['data']))
                            
                            curs.execute("update data set data = '" + db_pas(rows[0]['data']) + "' where title = '" + db_pas(name) + "'")
                            conn.commit()
                        else:
                            leng = '+' + str(len(rows[0]['data']))
                            
                            curs.execute("insert into data (title, data, acl) value ('" + db_pas(name) + "', '" + db_pas(rows[0]['data']) + "', '')")
                            conn.commit()
                            
                        history_plus(name, rows[0]['data'], today, ip, '문서를 ' + str(num) + '판으로 되돌렸습니다.', leng)
                        
                        conn.close()
                        return(redirect('/w/' + url_pas(name)))
                else:
                    conn.close()
                    return(redirect('/w/' + url_pas(name)))
            else:
                conn.close()
                return(redirect('/error/3'))
        else:
            curs.execute("select * from history where title = '" + db_pas(name) + "' and id = '" + str(num) + "'")
            rows = curs.fetchall()
            if(rows):                
                if(can == 1):
                    conn.close()
                    return(redirect('/ban'))
                else:                    
                    curs.execute("select * from data where title = '" + db_pas(name) + "'")
                    row = curs.fetchall()
                    if(row):
                        leng = leng_check(len(row[0]['data']), len(rows[0]['data']))
                        
                        curs.execute("update data set data = '" + db_pas(rows[0]['data']) + "' where title = '" + db_pas(name) + "'")
                        conn.commit()
                    else:
                        leng = '+' + str(len(rows[0]['data']))
                        
                        curs.execute("insert into data (title, data, acl) value ('" + db_pas(name) + "', '" + db_pas(rows[0]['data']) + "', '')")
                        conn.commit()
                        
                    history_plus(name, rows[0]['data'], today, ip, '문서를 ' + str(num) + '판으로 되돌렸습니다.', leng)
                    
                    conn.close()
                    return(redirect('/w/' + url_pas(name)))
            else:
                conn.close()
                return(redirect('/w/' + url_pas(name))            )
    else:
        curs.execute("select * from hidhi where title = '" + db_pas(name) + "' and re = '" + db_pas(str(num)) + "'")
        row = curs.fetchall()
        if(row):
            if(admin_check(6) == 1):                
                if(can == 1):
                    conn.close()
                    return(redirect('/ban'))
                else:
                    curs.execute("select * from history where title = '" + db_pas(name) + "' and id = '" + str(num) + "'")
                    rows = curs.fetchall()
                    if(rows):
                        conn.close()
                        return(template('revert', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), r = url_pas(str(num)), plus = '정말 되돌리시겠습니까?', sub = '되돌리기'))
                    else:
                        conn.close()
                        return(redirect('/w/' + url_pas(name)))
            else:
                conn.close()
                return(redirect('/error/3'))
        else:            
            if(can == 1):
                conn.close()
                return(redirect('/ban'))
            else:
                curs.execute("select * from history where title = '" + db_pas(name) + "' and id = '" + str(num) + "'")
                rows = curs.fetchall()
                if(rows):
                    conn.close()
                    return(template('revert', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), r = url_pas(str(num)), plus = '정말 되돌리시겠습니까?', sub = '되돌리기'))
                else:
                    conn.close()
                    return(redirect('/w/' + url_pas(name)))
                    
@route('/mdel', method=['POST', 'GET'])
def many_del():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    today = get_time()
    ip = ip_check()
    if(admin_check(2) == 1):
        if(request.method == 'POST'):
            data = request.forms.content + '\r\n'
            while(True):
                m = re.search('(.*)\r\n', data)
                if(m):
                    g = m.groups()
                    curs.execute("select data from data where title = '" + db_pas(g[0]) + "'")
                    rows = curs.fetchall()
                    if(rows):
                        leng = '-' + str(len(rows[0]['data']))
                        curs.execute("delete from data where title = '" + db_pas(g[0]) + "'")
                        history_plus(g[0], '', today, ip, request.forms.send + ' (대량 삭제)', leng)
                    data = re.sub('(.*)\r\n', '', data, 1)
                else:
                    break
            conn.commit()
            conn.close()
            return(redirect('/'))
        else:
            conn.close()
            return(template('mdel', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '많은 문서 삭제', logo = set_data['name']))
    else:
        conn.close()
        return(redirect('/error/3'))
    
                
@route('/edit/<name:path>/section/<num:int>', method=['POST', 'GET'])
def section_edit(name = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    can = acl_check(ip, name)
    
    if(request.method == 'POST'):
        if(len(request.forms.send) > 500):
            conn.close()
            return(redirect('/error/15'))
        else:
            today = get_time()
            
            content = savemark(request.forms.content)

            curs.execute("delete from back where title = '" + db_pas(name) + "'")
            conn.commit()
            
            curs.execute("select * from data where title = '" + db_pas(name) + "'")
            rows = curs.fetchall()
            if(rows):
                if(request.forms.otent == content):
                    conn.close()
                    return(redirect('/error/18'))
                else:                    
                    if(can == 1):
                        conn.close()
                        return(redirect('/ban'))
                    else:
                        leng = leng_check(len(request.forms.otent), len(content))
                        
                        content = rows[0]['data'].replace(request.forms.otent, content)
                        
                        history_plus(name, content, today, ip, html_pas(request.forms.send, 2), leng)
                        
                        curs.execute("update data set data = '" + db_pas(content) + "' where title = '" + db_pas(name) + "'")
                        conn.commit()
                        
                    include_check(name, content)
                    
                    conn.close()
                    return(redirect('/w/' + url_pas(name)))
            else:
                conn.close()
                return(redirect('/w/' + url_pas(name)))
    else:        
        if(can == 1):
            conn.close()
            return(redirect('/ban'))
        else:                
            curs.execute("select * from data where title = '" + db_pas(name) + "'")
            rows = curs.fetchall()
            if(rows):
                i = 0
                j = 0
                
                gdata = rows[0]['data'] + '\r\n'
                while(True):
                    m = re.search("((?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n(?:(?:(?:(?!(?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n).)*)(?:\n)?)+)", gdata)
                    if(m):
                        if(i == num - 1):
                            g = m.groups()
                            gdata = re.sub("\r\n$", "", g[0])
                            break
                        else:
                            gdata = re.sub("((?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n(?:(?:(?:(?!(?:={1,6})\s?(?:[^=]*)\s?(?:={1,6})(?:\s+)?\n).)*)(?:\n)?)+)", "", gdata, 1)
                            
                            i += 1
                    else:
                        j = 1
                        
                        break
                        
                if(j == 0):
                    gdata = re.sub("\r\n$", "", gdata)

                    conn.close()
                    return(template('edit', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = gdata, section = 1, number = num, sub = '편집'))
                else:
                    conn.close()
                    return(redirect('/w/' + url_pas(name)))
            else:
                conn.close()
                return(redirect('/w/' + url_pas(name)))

@route('/edit/<name:path>', method=['POST', 'GET'])
def edit(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    can = acl_check(ip, name)
    
    if(request.method == 'POST'):
        if(len(request.forms.send) > 500):
            conn.close()
            return(redirect('/error/15'))
        else:
            today = get_time()
            
            content = savemark(request.forms.content)

            curs.execute("delete from back where title = '" + db_pas(name) + "'")
            conn.commit()
            
            curs.execute("select * from data where title = '" + db_pas(name) + "'")
            rows = curs.fetchall()
            if(rows):
                if(rows[0]['data'] == content):
                    conn.close()
                    return(redirect('/error/18'))
                else:                    
                    if(can == 1):
                        conn.close()
                        return(redirect('/ban'))
                    else:                        
                        leng = leng_check(len(rows[0]['data']), len(content))
                        history_plus(name, content, today, ip, html_pas(request.forms.send, 2), leng)
                        
                        curs.execute("update data set data = '" + db_pas(content) + "' where title = '" + db_pas(name) + "'")
                        conn.commit()
            else:                
                if(can == 1):
                    conn.close()
                    return(redirect('/ban'))
                else:
                    leng = '+' + str(len(content))
                    history_plus(name, content, today, ip, html_pas(request.forms.send, 2), leng)
                    
                    curs.execute("insert into data (title, data, acl) value ('" + db_pas(name) + "', '" + db_pas(content) + "', '')")
                    conn.commit()
                    
            include_check(name, content)
            
            conn.close()
            return(redirect('/w/' + url_pas(name)))
    else:        
        if(can == 1):
            conn.close()
            return(redirect('/ban'))
        else:                
            curs.execute("select * from data where title = '" + db_pas(name) + "'")
            rows = curs.fetchall()
            if(rows):
                conn.close()
                return(template('edit', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = rows[0]['data'], sub = '편집'))
            else:
                conn.close()
                return(template('edit', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = '', sub = '편집'))

@route('/preview/<name:path>/section/<num:int>', method=['POST'])
def section_preview(name = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    can = acl_check(ip, name)
    
    if(can == 1):
        conn.close()
        return(redirect('/ban'))
    else:            
        newdata = request.forms.content
        newdata = re.sub('^#(?:redirect|넘겨주기)\s(?P<in>[^\n]*)', ' * [[\g<in>]] 문서로 넘겨주기', newdata)
        enddata = namumark(name, newdata)
            
        conn.close()
        return(template('edit', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = request.forms.content, preview = 1, enddata = enddata, section = 1, number = num, odata = request.forms.otent, sub = '미리보기'))
                
@route('/preview/<name:path>', method=['POST'])
def preview(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    can = acl_check(ip, name)
    
    if(can == 1):
        conn.close()
        return(redirect('/ban'))
    else:            
        newdata = request.forms.content
        newdata = re.sub('^#(?:redirect|넘겨주기)\s(?P<in>[^\n]*)', ' * [[\g<in>]] 문서로 넘겨주기', newdata)
        enddata = namumark(name, newdata)
            
        conn.close()
        return(template('edit', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = request.forms.content, preview = 1, enddata = enddata, sub = '미리보기'))
        
@route('/delete/<name:path>', method=['POST', 'GET'])
def delete(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    can = acl_check(ip, name)
    
    if(request.method == 'POST'):
        curs.execute("select * from data where title = '" + db_pas(name) + "'")
        rows = curs.fetchall()
        if(rows):
            if(can == 1):
                conn.close()
                return(redirect('/ban'))
            else:
                today = get_time()
                
                leng = '-' + str(len(rows[0]['data']))
                history_plus(name, '', today, ip, request.forms.send + ' (삭제)', leng)
                
                curs.execute("delete from data where title = '" + db_pas(name) + "'")
                conn.commit()
                
                conn.close()
                return(redirect('/w/' + url_pas(name)))
        else:
            conn.close()
            return(redirect('/w/' + url_pas(name)))
    else:
        curs.execute("select * from data where title = '" + db_pas(name) + "'")
        rows = curs.fetchall()
        if(rows):
            if(can == 1):
                conn.close()
                return(redirect('/ban'))
            else:
                conn.close()
                return(template('del', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), plus = '정말 삭제 하시겠습니까?', sub = '삭제'))
        else:
            conn.close()
            return(redirect('/w/' + url_pas(name)))
            
@route('/move/<name:path>', method=['POST', 'GET'])
def move(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    can = acl_check(ip, name)
    today = get_time()
    
    if(request.method == 'POST'):
        curs.execute("select * from data where title = '" + db_pas(name) + "'")
        rows = curs.fetchall()

        if(can == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            leng = '0'
            curs.execute("select * from history where title = '" + db_pas(request.forms.title) + "'")
            row = curs.fetchall()
            if(row):
                conn.close()
                return(redirect('/error/19'))
            else:
                history_plus(name, rows[0]['data'], today, ip, request.forms.send + ' (<a href="/w/' + url_pas(name) + '">' + name + '</a> - <a href="/w/' + url_pas(request.forms.title) + '">' + request.forms.title + '</a> 이동)', leng)
                
                if(rows):
                    curs.execute("update data set title = '" + db_pas(request.forms.title) + "' where title = '" + db_pas(name) + "'")

                curs.execute("update history set title = '" + db_pas(request.forms.title) + "' where title = '" + db_pas(name) + "'")
                conn.commit()
                conn.close()
                return(redirect('/w/' + url_pas(request.forms.title)))
    else:
        if(can == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            conn.close()
            return(template('move', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), plus = '정말 이동 하시겠습니까?', sub = '이동'))
            
@route('/other')
def other():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '기타 메뉴', logo = set_data['name'], data = '<h2 style="margin-top: 0px;">기록</h2><li><a href="/blocklog">사용자 차단 기록</a></li><li><a href="/userlog">사용자 가입 기록</a></li><li><a href="/manager/6">사용자 기록</a></li><li><a href="/manager/7">사용자 토론 기록</a></li><h2>기타</h2><li><a href="/titleindex">모든 문서</a></li><li><a href="/acllist">ACL 문서 목록</a></li><li><a href="/upload">업로드</a></li><li><a href="/adminlist">관리자 목록</a></li><li><a href="/manager/1">관리자 메뉴</a></li><br>이 오픈나무의 버전은 <a href="https://github.com/2DU/openNAMU/blob/normal/version.md">v' + r_ver + '</a> 입니다.'))
    
@route('/manager/<num:int>', method=['POST', 'GET'])
def manager(num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(num == 1):
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '관리자 메뉴', logo = set_data['name'], data = '<h2 style="margin-top: 0px;">목록</h2><li><a href="/manager/2">문서 ACL</a></li><li><a href="/manager/3">사용자 체크</a></li><li><a href="/manager/4">사용자 차단</a></li><li><a href="/manager/5">관리자 권한 주기</a></li><li><a href="/mdel">많은 문서 삭제</a></li><h2>소유자</h2><li><a href="/backreset">모든 역링크 재 생성</a></li><li><a href="/manager/8">관리 그룹 생성</a></li><h2>기타</h2><li>이 메뉴에 없는 기능은 해당 문서의 역사나 토론에서 바로 사용 가능함</li>'))
    elif(num == 2):
        if(request.method == 'POST'):
            conn.close()
            return(redirect('/acl/' + url_pas(request.forms.name)))
        else:
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = 'ACL 이동', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/manager/2"><input name="name" type="text"><br><br><button class="btn btn-primary" type="submit">이동</button></form>'))
    elif(num == 3):
        if(request.method == 'POST'):
            conn.close()
            return(redirect('/check/' + url_pas(request.forms.name)))
        else:
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '체크 이동', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/manager/3"><input name="name" type="text"><br><br><button class="btn btn-primary" type="submit">이동</button></form>'))
    elif(num == 4):
        if(request.method == 'POST'):
            conn.close()
            return(redirect('/ban/' + url_pas(request.forms.name)))
        else:
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '차단 이동', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/manager/4"><input name="name" type="text"><br><br><button class="btn btn-primary" type="submit">이동</button><br><br><span>아이피 앞 두자리 (XXX.XXX) 입력하면 대역 차단</span></form>'))
    elif(num == 5):
        if(request.method == 'POST'):
            conn.close()
            return(redirect('/admin/' + url_pas(request.forms.name)))
        else:
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '권한 이동', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/manager/5"><input name="name" type="text"><br><br><button class="btn btn-primary" type="submit">이동</button></form>')   )
    elif(num == 6):
        if(request.method == 'POST'):
            conn.close()
            return(redirect('/record/' + url_pas(request.forms.name)))
        else:
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '기록 이동', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/manager/6"><input name="name" type="text"><br><br><button class="btn btn-primary" type="submit">이동</button></form>')    )
    elif(num == 7):
        if(request.method == 'POST'):
            conn.close()
            return(redirect('/user/' + url_pas(request.forms.name) + '/topic'))
        else:
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '토론 기록 이동', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/manager/7"><input name="name" type="text"><br><br><button class="btn btn-primary" type="submit">이동</button></form>')    )
    elif(num == 8):
        if(request.method == 'POST'):
            conn.close()
            return(redirect('/adminplus/' + url_pas(request.forms.name)))
        else:
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '그룹 생성 이동', logo = set_data['name'], data = '<form id="usrform" method="POST" action="/manager/8"><input name="name" type="text"><br><br><button class="btn btn-primary" type="submit">이동</button></form>')    )
    else:
        conn.close()
        return(redirect('/'))
        
@route('/titleindex')
def title_index():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    i = [0, 0, 0, 0, 0, 0]
    data = '<div>'
    curs.execute("select title from data order by title asc")
    title_list = curs.fetchall()
    if(title_list):
        for list_data in title_list:
            data += '<li>' + str(i[0] + 1) + '. <a href="/w/' + url_pas(list_data['title']) + '">' + list_data['title'] + '</a></li>'

            if(re.search('^분류:', list_data['title'])):
                i[1] += 1
            elif(re.search('^사용자:', list_data['title'])):
                i[2] += 1
            elif(re.search('^틀:', list_data['title'])):
                i[3] += 1
            elif(re.search('^파일:', list_data['title'])):
                i[4] += 1
            else:
                i[5] += 1
        
            i[0] += 1
                
        else:
            data += '</div>'
                
        data += '<br><li>이 위키에는 총 ' + str(i[0]) + '개의 문서가 있습니다.</li><br><li>틀 문서는 총 ' + str(i[3]) + '개의 문서가 있습니다.</li><li>분류 문서는 총 ' + str(i[1]) + '개의 문서가 있습니다.</li><li>사용자 문서는 총 ' + str(i[2]) + '개의 문서가 있습니다.</li><li>파일 문서는 총 ' + str(i[4]) + '개의 문서가 있습니다.</li><li>나머지 문서는 총 ' + str(i[5]) + '개의 문서가 있습니다.</li>'
    else:
        data = 'None'

    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = data, title = '모든 문서'))
        
@route('/topic/<name:path>/sub/<sub:path>/b/<num:int>')
def topic_block(name = None, sub = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(3) == 1):
        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and id = '" + str(num) + "'")
        block = curs.fetchall()
        if(block):
            if(block[0]['block'] == 'O'):
                curs.execute("update topic set block = '' where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and id = '" + str(num) + "'")
            else:
                curs.execute("update topic set block = 'O' where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and id = '" + str(num) + "'")
            conn.commit()
            
            rd_plus(name, sub, get_time())
            
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
        else:
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
    else:
        conn.close()
        return(redirect('/error/3'))
        
@route('/topic/<name:path>/sub/<sub:path>/notice/<num:int>')
def topic_top(name = None, sub = None, num = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(3) == 1):
        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and id = '" + str(num) + "'")
        topic_data = curs.fetchall()
        if(topic_data):
            curs.execute("select * from topic where id = '" + str(num) + "' and title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "'")
            top_data = curs.fetchall()
            if(top_data):
                if(top_data[0]['top'] == 'O'):
                    curs.execute("update topic set top = '' where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and id = '" + str(num) + "'")
                else:
                    curs.execute("update topic set top = 'O' where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and id = '" + str(num) + "'")

            conn.commit()
            
            rd_plus(name, sub, get_time())

            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
        else:
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
    else:
        conn.close()
        return(redirect('/error/3'))
        
@route('/topic/<name:path>/sub/<sub:path>/stop')
def topic_stop(name = None, sub = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(3) == 1):
        ip = ip_check()
        
        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' order by id + 0 desc limit 1")
        topic_check = curs.fetchall()
        if(topic_check):
            time = get_time()
            
            curs.execute("select * from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and close = ''")
            stop = curs.fetchall()
            if(stop):
                curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) value ('" + db_pas(str(int(topic_check[0]['id']) + 1)) + "', '" + db_pas(name) + "', '" + db_pas(sub) + "', '토론 재 시작', '" + db_pas(time) + "', '" + db_pas(ip) + "', '', '1')")
                curs.execute("delete from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and close = ''")
            else:
                curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) value ('" + db_pas(str(int(topic_check[0]['id']) + 1)) + "', '" + db_pas(name) + "', '" + db_pas(sub) + "', '토론 정지', '" + db_pas(time) + "', '" + db_pas(ip) + "', '', '1')")
                curs.execute("insert into stop (title, sub, close) value ('" + db_pas(name) + "', '" + db_pas(sub) + "', '')")
            conn.commit()
            
            rd_plus(name, sub, time)
            
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
        else:
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
    else:
        conn.close()
        return(redirect('/error/3'))
        
@route('/topic/<name:path>/sub/<sub:path>/close')
def topic_close(name = None, sub = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(3) == 1):
        ip = ip_check()
        
        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' order by id + 0 desc limit 1")
        topic_check = curs.fetchall()
        if(topic_check):
            time = get_time()
            
            curs.execute("select * from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and close = 'O'")
            close = curs.fetchall()
            if(close):
                curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) value ('" + db_pas(str(int(topic_check[0]['id']) + 1)) + "', '" + db_pas(name) + "', '" + db_pas(sub) + "', '토론 다시 열기', '" + db_pas(time) + "', '" + db_pas(ip) + "', '', '1')")
                curs.execute("delete from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and close = 'O'")
            else:
                curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) value ('" + db_pas(str(int(topic_check[0]['id']) + 1)) + "', '" + db_pas(name) + "', '" + db_pas(sub) + "', '토론 닫음', '" + db_pas(time) + "', '" + db_pas(ip) + "', '', '1')")
                curs.execute("insert into stop (title, sub, close) value ('" + db_pas(name) + "', '" + db_pas(sub) + "', 'O')")
            conn.commit()
            
            rd_plus(name, sub, time)
            
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
        else:
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
    else:
        conn.close()
        return(redirect('/error/3'))
        
@route('/topic/<name:path>/sub/<sub:path>/agree')
def topic_agree(name = None, sub = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(admin_check(3) == 1):
        ip = ip_check()
        
        curs.execute("select id from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' order by id + 0 desc limit 1")
        topic_check = curs.fetchall()
        if(topic_check):
            time = get_time()
            
            curs.execute("select * from agreedis where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "'")
            agree = curs.fetchall()
            if(agree):
                curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) value ('" + db_pas(str(int(topic_check[0]['id']) + 1)) + "', '" + db_pas(name) + "', '" + db_pas(sub) + "', '합의 결렬', '" + db_pas(time) + "', '" + db_pas(ip) + "', '', '1')")
                curs.execute("delete from agreedis where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "'")
            else:
                curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) value ('" + db_pas(str(int(topic_check[0]['id']) + 1)) + "', '" + db_pas(name) + "', '" + db_pas(sub) + "', '합의 완료', '" + db_pas(time) + "', '" + db_pas(ip) + "', '', '1')")
                curs.execute("insert into agreedis (title, sub) value ('" + db_pas(name) + "', '" + db_pas(sub) + "')")
            conn.commit()
            
            rd_plus(name, sub, time)
            
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
        else:
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
    else:
        conn.close()
        return(redirect('/error/3'))

@route('/topic/<name:path>/sub/<sub:path>', method=['POST', 'GET'])
def topic(name = None, sub = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    ban = topic_check(ip, name, sub)
    admin = admin_check(3)
    
    if(request.method == 'POST'):
        curs.execute("select id from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' order by id + 0 desc limit 1")
        rows = curs.fetchall()
        if(rows):
            num = int(rows[0]['id']) + 1
        else:
            num = 1
        
        if(ban == 1 and not admin == 1):
            conn.close()
            return(redirect('/ban'))
        else:                    
            today = get_time()
            rd_plus(name, sub, today)
            
            aa = re.sub("\[\[(분류:(?:(?:(?!\]\]).)*))\]\]", "[br]", request.forms.content)
            aa = savemark(aa)
            
            curs.execute("insert into topic (id, title, sub, data, date, ip, block, top) value ('" + str(num) + "', '" + db_pas(name) + "', '" + db_pas(sub) + "', '" + db_pas(aa) + "', '" + today + "', '" + ip + "', '', '')")
            conn.commit()
            
            conn.close()
            return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub)))
    else:
        style = ''

        curs.execute("select * from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and close = 'O'")
        close = curs.fetchall()

        curs.execute("select * from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and close = ''")
        stop = curs.fetchall()
        
        if(admin == 1):
            div = '<div>'
            
            if(close):
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/close">(토론 열기)</a> '
            else:
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/close">(토론 닫기)</a> '
            
            if(stop):
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/stop">(토론 재개)</a> '
            else:
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/stop">(토론 정지)</a> '

            curs.execute("select * from agreedis where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "'")
            agree = curs.fetchall()
            if(agree):
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/agree">(합의 취소)</a>'
            else:
                div += '<a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/agree">(합의 완료)</a>'
            
            div += '<br><br>'
        else:
            div = '<div>'
        
        if(stop or close):
            if(not admin == 1):
                style = 'display:none;'
        
        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' order by id + 0 asc")
        toda = curs.fetchall()

        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and top = 'O' order by id + 0 asc")
        top = curs.fetchall()

        if(top):
            for dain in top:                     
                top_data = namumark('', dain['data'])
                top_data = re.sub("(?P<in>#(?:[0-9]*))", '<a href="\g<in>">\g<in></a>', top_data)
                        
                ip = ip_pas(dain['ip'], 1)
                                   
                div += '<table id="toron"><tbody><tr><td id="toroncolorred"><a href="#' + dain['id'] + '">#' + dain['id'] + '</a> ' + ip + ' <span style="float:right;">' + dain['date'] + '</span></td></tr><tr><td>' + top_data + '</td></tr></tbody></table><br>'
                    
        i = 0          
        for dain in toda:
            if(i == 0):
                start = dain['ip']
                
            indata = namumark('', dain['data'])
            indata = re.sub("(?P<in>#(?:[0-9]*))", '<a href="\g<in>">\g<in></a>', indata)
            
            if(dain['block'] == 'O'):
                indata = '<br>'
                block = 'id="block"'
            else:
                block = ''

            if(admin == 1):
                if(dain['block'] == 'O'):
                    isblock = ' <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/b/' + str(i + 1) + '">(해제)</a>'
                else:
                    isblock = ' <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/b/' + str(i + 1) + '">(가림)</a>'

                curs.execute("select id from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(sub) + "' and id = '" + db_pas(str(i + 1)) + "' and top = 'O'")
                row = curs.fetchall()
                if(row):
                    isblock = isblock + ' <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/notice/' + str(i + 1) + '">(해제)</a>'
                else:
                    isblock = isblock + ' <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/notice/' + str(i + 1) + '">(공지)</a>'
                    
                curs.execute("select end from ban where block = '" + db_pas(dain['ip']) + "'")
                ban_it = curs.fetchall()
                if(ban_it):
                    ban = ' <a href="/ban/' + url_pas(dain['ip']) + '">(해제)</a>' + isblock
                else:
                    ban = ' <a href="/ban/' + url_pas(dain['ip']) + '">(차단)</a>' + isblock
            else:
                curs.execute("select end from ban where block = '" + db_pas(dain['ip']) + "'")
                ban_it = curs.fetchall()
                if(ban_it):
                    ban = ' (X)'
                else:
                    ban = ''
            
            chad = ''
            curs.execute('select acl from user where id = "' + db_pas(dain['ip']) + '"')
            adch = curs.fetchall()
            if(adch):
                if(not adch[0]['acl'] == 'user'):
                    chad = ' ★'

            ip = ip_pas(dain['ip'], 1)
                    
            if(dain['top'] == '1'):
                color = 'blue'
            elif(dain['ip'] == start):
                color = 'green'
            else:
                color = ''
                         
            div += '<table id="toron"><tbody><tr><td id="toroncolor' + color + '"><a href="javascript:void(0);" id="' + str(i + 1) + '">#' + str(i + 1) + '</a> ' + ip + chad + ban + ' <span style="float:right;">' + dain['date'] + '</span></td></tr><tr><td ' + block + '>' + indata + '</td></tr></tbody></table><br>'
                
            i += 1
            
        conn.close()
        return(template('vstopic', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, page = url_pas(name), suburl = url_pas(sub), toron = sub, logo = set_data['name'], rows = div, ban = ban, style = style, sub = '토론'))
        
@route('/topic/<name:path>/close')
def close_topic_list(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    div = '<div>'
    i = 0
    
    curs.execute("select * from stop where title = '" + db_pas(name) + "' and close = 'O' order by sub asc")
    rows = curs.fetchall()
    for data in rows:
        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(data['sub']) + "' and id = '1'")
        row = curs.fetchall()
        if(row):
            indata = namumark(name, row[0]['data'])
            
            if(row[0]['block'] == 'O'):
                indata = '<br>'
                block = 'id="block"'
            else:
                block = ''

            ip = ip_pas(row[0]['ip'], 1)
                
            div += '<h2><a href="/topic/' + url_pas(name) + '/sub/' + url_pas(data['sub']) + '">' + str((i + 1)) + '. ' + data['sub'] + '</a></h2><table id="toron"><tbody><tr><td id="toroncolorgreen"><a href="javascript:void(0);" id="1">#1</a> ' + ip + ' <span style="float:right;">' + row[0]['date'] + '</span></td></tr><tr><td ' + block + '>' + indata + '</td></tr></tbody></table><br>'
            
            i += 1
    else:
        div += '</div>'
        
    conn.close()
    return(template('topic', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, page = url_pas(name), logo = set_data['name'], plus = div, sub = '닫힘'))
    
@route('/topic/<name:path>/agree')
def agree_topic_list(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    div = '<div>'
    i = 0
    
    curs.execute("select * from agreedis where title = '" + db_pas(name) + "' order by sub asc")
    agree_list = curs.fetchall()
    for data in agree_list:
        curs.execute("select * from topic where title = '" + db_pas(name) + "' and sub = '" + db_pas(data['sub']) + "' and id = '1'")
        topic_data = curs.fetchall()
        if(topic_data):
            indata = namumark(name, topic_data[0]['data'])
            
            if(topic_data[0]['block'] == 'O'):
                indata = '<br>'
                block = 'id="block"'
            else:
                block = ''

            ip = ip_pas(topic_data[0]['ip'], 1)
                
            div += '<h2><a href="/topic/' + url_pas(name) + '/sub/' + url_pas(data['sub']) + '">' + str(i + 1) + '. ' + data['sub'] + '</a></h2><table id="toron"><tbody><tr><td id="toroncolorgreen"><a href="javascript:void(0);" id="1">#1</a> ' + ip + ' <span style="float:right;">' + topic_data[0]['date'] + '</span></td></tr><tr><td ' + block + '>' + indata + '</td></tr></tbody></table><br>'
            
            i += 1
    else:
        div += '</div>'
        
    conn.close()
    return(template('topic', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, page = url_pas(name), logo = set_data['name'], plus = div, sub = '합의'))

@route('/topic/<name:path>', method=['POST', 'GET'])
def topic_list(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(request.method == 'POST'):
        conn.close()
        return(redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(request.forms.topic)))
    else:
        div = '<div>'
        j = 1
        curs.execute("select * from rd where title = '" + db_pas(name) + "' order by date asc")
        rows = curs.fetchall()
        for data in rows:
            curs.execute("select * from topic where title = '" + db_pas(data['title']) + "' and sub = '" + db_pas(data['sub']) + "' and id = '1' order by sub asc")
            aa = curs.fetchall()
            
            indata = namumark(name, aa[0]['data'])
            
            if(aa[0]['block'] == 'O'):
                indata = '<br>'
                block = 'id="block"'
            else:
                block = ''

            ip = ip_pas(aa[0]['ip'], 1)
                
            curs.execute("select * from stop where title = '" + db_pas(data['title']) + "' and sub = '" + db_pas(data['sub']) + "' and close = 'O'")
            row = curs.fetchall()
            if(not row):
                div += '<h2><a href="/topic/' + url_pas(data['title']) + '/sub/' + url_pas(data['sub']) + '">' + str(j) + '. ' + data['sub'] + '</a></h2><table id="toron"><tbody><tr><td id="toroncolorgreen"><a href="javascript:void(0);" id="1">#1</a> ' + ip + ' <span style="float:right;">' + aa[0]['date'] + '</span></td></tr><tr><td ' + block + '>' + indata + '</td></tr></tbody></table><br>'
                
                j += 1
        else:
            div += '</div>'
                
        conn.close()
        return(template('topic', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, page = url_pas(name), logo = set_data['name'], plus = div, list = 1, sub = '토론 목록'))
        
@route('/login', method=['POST', 'GET'])
def login():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    session = request.environ.get('beaker.session')
    ip = ip_check()
    ban = ban_check(ip)
        
    if(request.method == 'POST'):        
        if(ban == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            curs.execute("select * from user where id = '" + db_pas(request.forms.id) + "'")
            user = curs.fetchall()
            if(user):
                if(session.get('Now') == True):
                    conn.close()
                    return(redirect('/error/11'))
                elif(bcrypt.checkpw(bytes(request.forms.pw, 'utf-8'), bytes(user[0]['pw'], 'utf-8'))):
                    session['Now'] = True
                    session['DREAMER'] = request.forms.id

                    curs.execute("select * from custom where user = '" + db_pas(request.forms.id) + "'")
                    css_data = curs.fetchall()
                    if(css_data):
                        session['Daydream'] = css_data[0]['css']
                    else:
                        session['Daydream'] = ''
                    
                    curs.execute("insert into login (user, ip, today) value ('" + db_pas(request.forms.id) + "', '" + db_pas(ip) + "', '" + db_pas(get_time()) + "')")
                    conn.commit()
                    
                    conn.close()
                    return(redirect('/user'))
                else:
                    conn.close()
                    return(redirect('/error/13'))
            else:
                conn.close()
                return(redirect('/error/12'))
    else:        
        if(ban == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            if(session.get('Now') == True):
                conn.close()
                return(redirect('/error/11'))
            else:
                conn.close()
                return(template('login', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '로그인', enter = '로그인', logo = set_data['name']))
                
@route('/change', method=['POST', 'GET'])
def change_password():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    ban = ban_check(ip)
    
    if(request.method == 'POST'):      
        if(request.forms.pw2 == request.forms.pw3):
            if(ban == 1):
                conn.close()
                return(redirect('/ban'))
            else:
                curs.execute("select * from user where id = '" + db_pas(request.forms.id) + "'")
                user = curs.fetchall()
                if(user):
                    if(not re.search('(\.|:)', ip)):
                        conn.close()
                        return(redirect('/logout'))
                    elif(bcrypt.checkpw(bytes(request.forms.pw, 'utf-8'), bytes(user[0]['pw'], 'utf-8'))):
                        hashed = bcrypt.hashpw(bytes(request.forms.pw2, 'utf-8'), bcrypt.gensalt())
                        
                        curs.execute("update user set pw = '" + db_pas(hashed.decode()) + "' where id = '" + db_pas(request.forms.id) + "'")
                        conn.commit()
                        
                        conn.close()
                        return(redirect('/login'))
                    else:
                        conn.close()
                        return(redirect('/error/10'))
                else:
                    conn.close()
                    return(redirect('/error/9'))
        else:
            conn.close()
            return(redirect('/error/20'))
    else:        
        if(ban == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            if(not re.search('(\.|:)', ip)):
                conn.close()
                return(redirect('/logout'))
            else:
                conn.close()
                return(template('login', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '비밀번호 변경', enter = '변경', logo = set_data['name']))
                
@route('/check/<name:path>')
def user_check(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select * from user where id = '" + db_pas(name) + "'")
    user = curs.fetchall()
    if(user and not user[0]['acl'] == 'user'):
        conn.close()
        return(redirect('/error/4'))
    else:
        if(admin_check(4) == 1):
            m = re.search('^(?:[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}?)$', name)
            if(m):
                curs.execute("select * from login where ip = '" + db_pas(name) + "' order by today desc")
                row = curs.fetchall()
                if(row):
                    c = '<div><table style="width: 100%;"><tbody><tr><td style="text-align: center;width:33.33%;">이름</td><td style="text-align: center;width:33.33%;">아이피</td><td style="text-align: center;width:33.33%;">언제</td></tr>'
                    for data in row:
                        c += '<tr><td style="text-align: center;width:33.33%;">' + data['user'] + '</td><td style="text-align: center;width:33.33%;">' + data['ip'] + '</td><td style="text-align: center;width:33.33%;">' + data['today'] + '</td></tr>'
                    else:
                        c += '</tbody></table></div>'
                else:
                    c = 'None'
                        
                conn.close()
                return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '다중 검사', logo = set_data['name'], data = c))
            else:
                curs.execute("select * from login where user = '" + db_pas(name) + "' order by today desc")
                row = curs.fetchall()
                if(row):
                    c = '<div><table style="width: 100%;"><tbody><tr><td style="text-align: center;width:33.33%;">이름</td><td style="text-align: center;width:33.33%;">아이피</td><td style="text-align: center;width:33.33%;">언제</td></tr>'
                    for data in row:
                        c += '<tr><td style="text-align: center;width:33.33%;">' + data['user'] + '</td><td style="text-align: center;width:33.33%;">' + data['ip'] + '</td><td style="text-align: center;width:33.33%;">' + data['today'] + '</td></tr>'
                    else:
                        c += '</tbody></table></div>'
                else:
                    c = 'None'
                        
                conn.close()
                return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '다중 검사', logo = set_data['name'], data = c))
        else:
            conn.close()
            return(redirect('/error/3'))
                
@route('/register', method=['POST', 'GET'])
def register():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    ban = ban_check(ip)
    
    if(request.method == 'POST'):        
        if(request.forms.pw == request.forms.pw2):
            if(ban == 1):
                conn.close()
                return(redirect('/ban'))
            else:
                m = re.search('(?:[^A-Za-zㄱ-힣0-9 ])', request.forms.id)
                if(m):
                    conn.close()
                    return(redirect('/error/8'))
                else:
                    if(len(request.forms.id) > 20):
                        conn.close()
                        return(redirect('/error/7'))
                    else:
                        curs.execute("select * from user where id = '" + db_pas(request.forms.id) + "'")
                        rows = curs.fetchall()
                        if(rows):
                            conn.close()
                            return(redirect('/error/6'))
                        else:
                            hashed = bcrypt.hashpw(bytes(request.forms.pw, 'utf-8'), bcrypt.gensalt())
                            
                            curs.execute("select id from user limit 1")
                            user_ex = curs.fetchall()
                            if(not user_ex):
                                curs.execute("insert into user (id, pw, acl) value ('" + db_pas(request.forms.id) + "', '" + db_pas(hashed.decode()) + "', 'owner')")
                            else:
                                curs.execute("insert into user (id, pw, acl) value ('" + db_pas(request.forms.id) + "', '" + db_pas(hashed.decode()) + "', 'user')")
                            conn.commit()
                            
                            conn.close()
                            return(redirect('/login'))
        else:
            conn.close()
            return(redirect('/error/20'))
    else:        
        if(ban == 1):
            conn.close()
            return(redirect('/ban'))
        else:
            conn.close()
            return(template('login', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '회원가입', enter = '회원가입', logo = set_data['name']))
            
@route('/logout')
def logout():
    session = request.environ.get('beaker.session')
    session['Now'] = False
    session.pop('DREAMER', None)

    return(redirect('/user'))
    
@route('/ban/<name:path>', method=['POST', 'GET'])
def user_ban(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select * from user where id = '" + db_pas(name) + "'")
    user = curs.fetchall()
    if(user and not user[0]['acl'] == 'user'):
        conn.close()
        return(redirect('/error/4'))
    else:
        if(request.method == 'POST'):
            if(admin_check(1) == 1):
                ip = ip_check()
                
                if(not re.search("[0-9]{4}-[0-9]{2}-[0-9]{2}", request.forms.end)):
                    end = ''
                else:
                    end = request.forms.end

                curs.execute("select * from ban where block = '" + db_pas(name) + "'")
                row = curs.fetchall()
                if(row):
                    rb_plus(name, '해제', get_time(), ip, '')
                    
                    curs.execute("delete from ban where block = '" + db_pas(name) + "'")
                else:
                    b = re.search("^([0-9]{1,3}\.[0-9]{1,3})$", name)
                    if(b):
                        rb_plus(name, end, get_time(), ip, request.forms.why)
                        
                        curs.execute("insert into ban (block, end, why, band) value ('" + db_pas(name) + "', '" + db_pas(end) + "', '" + db_pas(request.forms.why) + "', 'O')")
                    else:
                        rb_plus(name, end, get_time(), ip, request.forms.why)
                        
                        curs.execute("insert into ban (block, end, why, band) value ('" + db_pas(name) + "', '" + db_pas(end) + "', '" + db_pas(request.forms.why) + "', '')")
                conn.commit()
                
                conn.close()
                return(redirect('/ban/' + url_pas(name)))
            else:
                conn.close()
                return(redirect('/error/3'))
        else:
            if(admin_check(1) == 1):
                curs.execute("select * from ban where block = '" + db_pas(name) + "'")
                row = curs.fetchall()
                if(row):
                    now = '차단 해제'
                else:
                    b = re.search("^([0-9]{1,3}\.[0-9]{1,3})$", name)
                    if(b):
                        now = '대역 차단'
                    else:
                        now = '차단'
                        
                conn.close()
                return(template('ban', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, page = url_pas(name), logo = set_data['name'], now = now, today = get_time(), sub = '차단'))
            else:
                conn.close()
                return(redirect('/error/3'))
                
@route('/acl/<name:path>', method=['POST', 'GET'])
def acl(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(request.method == 'POST'):
        if(admin_check(5) == 1):
            curs.execute("select acl from data where title = '" + db_pas(name) + "'")
            row = curs.fetchall()
            if(row):
                if(request.forms.select == 'admin'):
                   curs.execute("update data set acl = 'admin' where title = '" + db_pas(name) + "'")
                elif(request.forms.select == 'user'):
                    curs.execute("update data set acl = 'user' where title = '" + db_pas(name) + "'")
                else:
                    curs.execute("update data set acl = '' where title = '" + db_pas(name) + "'")
                    
                conn.commit()
                
            conn.close()
            return(redirect('/w/' + url_pas(name)) )
        else:
            conn.close()
            return(redirect('/error/3'))
    else:
        if(admin_check(5) == 1):
            curs.execute("select acl from data where title = '" + db_pas(name) + "'")
            row = curs.fetchall()
            if(row):
                if(row[0]['acl'] == 'admin'):
                    now = '관리자만'
                elif(row[0]['acl'] == 'user'):
                    now = '로그인 이상'
                else:
                    now = '일반'
                    
                conn.close()
                return(template('acl', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, page = url_pas(name), logo = set_data['name'], now = '현재 ACL 상태는 ' + now, sub = 'ACL'))
            else:
                conn.close()
                return(redirect('/w/' + url_pas(name)) )
        else:
            conn.close()
            return(redirect('/error/3'))
            
@route('/admin/<name:path>', method=['POST', 'GET'])
def user_admin(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(request.method == 'POST'):
        if(admin_check(None) == 1):
            curs.execute("select * from user where id = '" + db_pas(name) + "'")
            user = curs.fetchall()
            if(user):
                if(not user[0]['acl'] == 'user'):
                    curs.execute("update user set acl = 'user' where id = '" + db_pas(name) + "'")
                else:
                    curs.execute("update user set acl = '" + db_pas(request.forms.select) + "' where id = '" + db_pas(name) + "'")
                conn.commit()
                
                conn.close()
                return(redirect('/'))
            else:
                conn.close()
                return(redirect('/error/5'))
        else:
            conn.close()
            return(redirect('/error/3'))
    else:
        if(admin_check(None) == 1):
            curs.execute("select * from user where id = '" + db_pas(name) + "'")
            user = curs.fetchall()
            if(user):
                if(not user[0]['acl'] == 'user'):
                    now = '권한 해제'
                else:
                    now = '권한 부여'
                    
                div = ''
                    
                curs.execute('select name from alist order by name asc')
                get_alist = curs.fetchall()
                if(get_alist):
                    i = 0
                    name_rem = ''
                    for data in get_alist:
                        if(not name_rem == data['name']):
                            name_rem = data['name']
                            div += '<option value="' + data['name'] + '" selected="selected">' + data['name'] + '</option>'                       
                    
                conn.close()
                return(template('admin', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, page = url_pas(name), datalist = div, logo = set_data['name'], now = now, sub = '권한 부여'))
            else:
                conn.close()
                return(redirect('/error/5'))
        else:
            conn.close()
            return(redirect('/error/3'))
            
@route('/ban')
def are_you_ban():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    
    if(ban_check(ip) == 1):
        curs.execute("select * from ban where block = '" + db_pas(ip) + "'")
        rows = curs.fetchall()
        if(rows):
            if(rows[0]['end']):
                end = rows[0]['end'] + ' 까지 차단 상태 입니다. / 사유 : ' + rows[0]['why']                

                now = re.sub(':', '', get_time())
                now = re.sub('\-', '', now)
                now = int(re.sub(' ', '', now))
                
                day = re.sub('\-', '', rows[0]['end'])    
                
                if(now >= int(day + '000000')):
                    curs.execute("delete from ban where block = '" + db_pas(ip) + "'")
                    conn.commit()
                    
                    end = '차단이 풀렸습니다. 다시 시도 해 보세요.'
            else:
                end = '영구 차단 상태 입니다. / 사유 : ' + rows[0]['why']
        else:
            b = re.search("^([0-9](?:[0-9]?[0-9]?)\.[0-9](?:[0-9]?[0-9]?))", ip)
            if(b):
                results = b.groups()
                
                curs.execute("select * from ban where block = '" + db_pas(results[0]) + "' and band = 'O'")
                row = curs.fetchall()
                if(row):
                    if(row[0]['end']):
                        end = row[0]['end'] + ' 까지 차단 상태 입니다. / 사유 : ' + rows[0]['why']             
                        
                        now = re.sub(':', '', get_time())
                        now = re.sub('\-', '', now)
                        now = int(re.sub(' ', '', now))
                        
                        day = re.sub('\-', '', row[0]['end'])
                        
                        if(now >= int(day + '000000')):
                            curs.execute("delete from ban where block = '" + db_pas(results[0]) + "' and band = 'O'")
                            conn.commit()
                            
                            end = '차단이 풀렸습니다. 다시 시도 해 보세요.'
                    else:
                        end = '영구 차단 상태 입니다. / 사유 : ' + row[0]['why']                
    else:
        end = '권한이 맞지 않는 상태 입니다.'
        
    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '권한 오류', logo = set_data['name'], data = end))
    
@route('/w/<name:path>/r/<a:int>/diff/<b:int>')
def diff_data(name = None, a = None, b = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select * from history where id = '" + db_pas(str(a)) + "' and title = '" + db_pas(name) + "'")
    a_raw_data = curs.fetchall()
    if(a_raw_data):
        curs.execute("select * from history where id = '" + db_pas(str(b)) + "' and title = '" + db_pas(name) + "'")
        b_raw_data = curs.fetchall()
        if(b_raw_data):
            a_data = re.sub('<', '&lt;', a_raw_data[0]['data'])
            a_data = re.sub('>', '&gt;', a_data)
            a_data = re.sub('"', '&quot;', a_data)
            
            b_data = re.sub('<', '&lt;', b_raw_data[0]['data'])
            b_data = re.sub('>', '&gt;', b_data)
            b_data = re.sub('"', '&quot;', b_data)
            
            diff_data = difflib.SequenceMatcher(None, a_data, b_data)
            result = diff(diff_data)
            
            result = '<pre>' + result + '</pre>'
            
            conn.close()
            return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], data = result, sub = '비교', page = url_pas(name)))
        else:
            conn.close()
            return(redirect('/history/' + url_pas(name)))
    else:
        conn.close()
        return(redirect('/history/' + url_pas(name)))
        
@route('/down/<name:path>')
def down(name = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)
    
    curs.execute("select title from data where title like '%" + db_pas(name) + "/%'")
    under = curs.fetchall()
    
    div = ''
    
    i = 0
    for data in under:
        div += '<li>' + str(i + 1) + '. <a href="/w/' + url_pas(data['title']) + '">' + data['title'] + '</a></li>'
        i += 1
        
    conn.close()
    
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], data = div, sub = '하위 문서', page = url_pas(name)))

@route('/w/<name:path>')
@route('/w/<name:path>/from/<redirect:path>')
def read_view(name = None, redirect = None):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    data_none = False
    sub = None
    acl = ''
    div = ''
    
    i = 0
    curs.execute("select sub from rd where title = '" + db_pas(name) + "' order by date asc")
    rows = curs.fetchall()
    while(True):
        try:            
            curs.execute("select title from stop where title = '" + db_pas(name) + "' and sub = '" + db_pas(rows[i]['sub']) + "' and close = 'O'")
            row = curs.fetchall()
            if(not row):
                topic = "open"
                
                break

            i += 1
        except:
            topic = ""
            
            break
            
    curs.execute("select title from data where title like '%" + db_pas(name) + "/%'")
    under = curs.fetchall()
    if(under):
        down = True
    else:
        down = False
    
    m = re.search("^(.*)\/(.*)$", name)
    if(m):
        uppage = m.groups()[0]
    else:
        uppage = False
        
    if(admin_check(5) == 1):
        admin_memu = 'ACL'
    else:
        admin_memu = ''
    
    if(re.search("^분류:", name)):
        curs.execute("select * from cat where title = '" + db_pas(name) + "' order by cat asc")
        rows = curs.fetchall()
        if(rows):
            div = '<h2>분류</h2>'
            i = 0
            
            for data in rows:       
                curs.execute("select * from data where title = '" + db_pas(data['cat']) + "'")
                row = curs.fetchall()
                if(row):
                    aa = row[0]['data']                  
                    aa = namumark('', aa)
                    bb = re.search('<div style="width:100%;border: 1px solid #777;padding: 5px;margin-top: 1em;">분류:((?:(?!<\/div>).)*)<\/div>', aa)
                    if(bb):
                        cc = bb.groups()
                        
                        mm = re.search("^분류:(.*)", name)
                        if(mm):
                            ee = mm.groups()
                            
                            if(re.search("<a (class=\"not_thing\")? href=\"\/w\/" + url_pas(name) + "\">" + ee[0] + "<\/a>", cc[0])):
                                div += '<li><a href="/w/' + url_pas(data['cat']) + '">' + data['cat'] + '</a></li>'
                                
                                i += 1
                            else:
                                curs.execute("delete from cat where title = '" + db_pas(name) + "' and cat = '" + db_pas(data['cat']) + "'")
                                conn.commit()
                                
                                i += 1
                        else:
                            curs.execute("delete from cat where title = '" + db_pas(name) + "' and cat = '" + db_pas(data['cat']) + "'")
                            conn.commit()
                            
                            i += 1
                    else:
                        curs.execute("delete from cat where title = '" + db_pas(name) + "' and cat = '" + db_pas(data['cat']) + "'")
                        conn.commit()
                        
                        i += 1
                else:
                    curs.execute("delete from cat where title = '" + db_pas(name) + "' and cat = '" + db_pas(data['cat']) + "'")
                    conn.commit()
                    
                    i += 1
    
    curs.execute("select * from data where title = '" + db_pas(name) + "'")
    rows = curs.fetchall()
    if(rows):
        if(rows[0]['acl'] == 'admin'):
            acl = '(관리자)'
        elif(rows[0]['acl'] == 'user'):
            acl = '(로그인)'
                
        elsedata = rows[0]['data']
    else:
        data_none = True
        elsedata = 'None'

    m = re.search("^사용자:([^/]*)", name)
    if(m):
        g = m.groups()
        
        curs.execute("select acl from user where id = '" + db_pas(g[0]) + "'")
        test = curs.fetchall()
        if(test):
            if(not test[0]['acl'] == 'user'):
                acl = '(관리자)'

        curs.execute("select block from ban where block = '" + db_pas(g[0]) + "'")
        user = curs.fetchall()
        if(user):
            sub = '차단'
            
    if(redirect):
        elsedata = re.sub("^#(?:redirect|넘겨주기)\s(?P<in>[^\n]*)", " * [[\g<in>]] 문서로 넘겨주기", elsedata)
            
    enddata = namumark(name, elsedata)
        
    conn.close()
    return(template('read', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = name, logo = set_data['name'], page = url_pas(name), data = enddata + div, uppage = uppage, acl = acl, topic = topic, redirect = redirect, admin = admin_memu, data_none = data_none, sub = sub, down = down))

@route('/user/<name:path>/topic')
@route('/user/<name:path>/topic/<num:int>')
def user_topic_list(name = None, num = 1):
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    if(num * 50 <= 0):
        v = 50
    else:
        v = num * 50
    
    i = v - 50
    ydmin = admin_check(1)
    div = '<div><table style="width: 100%;"><tbody><tr><td style="text-align: center;width:33.33%;">토론명</td><td style="text-align: center;width:33.33%;">작성자</td><td style="text-align: center;width:33.33%;">시간</td></tr>'
    
    curs.execute("select title, id, sub, ip, date from topic where ip = '" + db_pas(name) + "' order by date desc limit " + str(i) + ", " + str(v))
    rows = curs.fetchall()
    if(rows):
        for data in rows:
            title = re.sub('<', '&lt;', data['title'])
            title = re.sub('>', '&gt;', title)
            title = re.sub('"', '&quot;', title)

            sub = re.sub('<', '&lt;', data['sub'])
            sub = re.sub('>', '&gt;', sub)
            sub = re.sub('"', '&quot;', sub)
                
            if(ydmin == 1):
                curs.execute("select * from ban where block = '" + db_pas(data['ip']) + "'")
                row = curs.fetchall()
                if(row):
                    ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(해제)</a>'
                else:
                    ban = ' <a href="/ban/' + url_pas(data['ip']) + '">(차단)</a>'
            else:
                ban = ''
                
            ip = ip_pas(data['ip'], 1)
                
            div += '<tr><td style="text-align: center;width:33.33%;"><a href="/topic/' + url_pas(data['title']) + '/sub/' + url_pas(data['sub']) + '#' + data['id'] + '">' + title + '</a> (' + sub + ') (#' + data['id'] + ') </td><td style="text-align: center;width:33.33%;">' + ip + ban +  '</td><td style="text-align: center;width:33.33%;">' + data['date'] + '</td></tr>'
        else:
            div += '</tbody></table></div>'
    else:
        div = 'None<br>'
        
    div += '<br><a href="/user/' + url_pas(name) + '/topic/' + str(num - 1) + '">(이전)</a> <a href="/user/' + url_pas(name) + '/topic/' + str(num + 1) + '">(이후)</a>'
                
    curs.execute("select end, why from ban where block = '" + db_pas(name) + "'")
    ban_it = curs.fetchall()
    if(ban_it):
        sub = '차단'
    else:
        sub = None
                
    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), logo = set_data['name'], data = div, title = '사용자 토론 기록', sub = sub))
        
@route('/user')
def user_info():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    ip = ip_check()
    raw_ip = ip
    
    curs.execute("select * from user where id = '" + db_pas(ip) + "'")
    rows = curs.fetchall()
    if(ban_check(ip) == 0):
        if(rows):
            if(not rows[0]['acl'] == 'user'):
                acl = rows[0]['acl']
            else:
                acl = '로그인'
        else:
            acl = '일반'
    else:
        acl = '차단'
        
    ip = ip_pas(ip, 2)
        
    conn.close()
    return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '사용자 메뉴', logo = set_data['name'], data = ip + '<br><br><span>권한 상태 : ' + acl + '<h2>로그인 관련</h2><li><a href="/login">로그인</a></li><li><a href="/logout">로그아웃</a></li><li><a href="/register">회원가입</a></li><h2>기타</h2><li><a href="/change">비밀번호 변경</a></li><li><a href="/count">기여 횟수</a></li><li><a href="/record/' + raw_ip + '">기여 목록</a></li><li><a href="/custom">커스텀 CSS</a></li>'))

@route('/custom', method=['GET', 'POST'])
def custom_css():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    session = request.environ.get('beaker.session')
    ip = ip_check()
    if(request.method == 'POST'):
        if(not re.search('(\.|:)', ip)):
            curs.execute("select * from custom where user = '" + db_pas(ip) + "'")
            css_data = curs.fetchall()
            if(css_data):
                curs.execute("update custom set css = '" + db_pas(request.forms.content) + "' where user = '" + db_pas(ip) + "'")
            else:
                curs.execute("insert into custom (user, css) value ('" + db_pas(ip) + "', '" + db_pas(request.forms.content) + "')")
            conn.commit()

        session['Daydream'] = request.forms.content

        conn.close()
        return(redirect('/user'))
    else:
        if(not re.search('(\.|:)', ip)):
            start = ''
            curs.execute("select * from custom where user = '" + db_pas(ip) + "'")
            css_data = curs.fetchall()
            if(css_data):
                data = css_data[0]['css']
            else:
                data = ''
        else:
            start = '<span>비 로그인의 경우에는 로그인하면 날아갑니다.</span><br><br>'
            try:
                data = session['Daydream']
            except:
                data = ''

        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '커스텀 CSS', logo = set_data['name'], data = start + '<form id="usrform" name="f1" method="POST" action="/custom"><textarea rows="30" cols="100" name="content" form="usrform">' + data + '</textarea><div class="form-actions"><button class="btn btn-primary" type="submit">저장</button></div></form>'))
    
@route('/count')
def count_edit():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select count(title) from history where ip = '" + ip_check() + "'")
    count = curs.fetchall()
    if(count):
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '기여 횟수', logo = set_data['name'], data = "기여 횟수 : " + str(count[0]["count(title)"])))
    else:
        conn.close()
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '기여 횟수', logo = set_data['name'], data = "기여 횟수 : 0"))
        
@route('/random')
def random():
    conn = pymysql.connect(user = set_data['user'], password = set_data['pw'], charset = 'utf8mb4', db = set_data['db'])
    curs = conn.cursor(pymysql.cursors.DictCursor)

    curs.execute("select title from data order by rand() limit 1")
    rows = curs.fetchall()
    if(rows):
        conn.close()
        return(redirect('/w/' + url_pas(rows[0]['title'])))
    else:
        conn.close()
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
        
    return(static_file(rename, root = './views' + plus))
        
@route('/error/<num:int>')
def error_test(num = None):
    if(num == 1):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '권한 오류', logo = set_data['name'], data = '비 로그인 상태 입니다.'))
    elif(num == 2):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '권한 오류', logo = set_data['name'], data = '이 계정이 없습니다.'))
    elif(num == 3):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '권한 오류', logo = set_data['name'], data = '권한이 모자랍니다.'))
    elif(num == 4):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '권한 오류', logo = set_data['name'], data = '관리자는 차단, 검사 할 수 없습니다.'))
    elif(num == 5):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '사용자 오류', logo = set_data['name'], data = '그런 계정이 없습니다.'))
    elif(num == 6):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '가입 오류', logo = set_data['name'], data = '동일한 아이디의 사용자가 있습니다.'))
    elif(num == 7):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '가입 오류', logo = set_data['name'], data = '아이디는 20글자보다 짧아야 합니다.'))
    elif(num == 8):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '가입 오류', logo = set_data['name'], data = '아이디에는 한글과 알파벳과 공백만 허용 됩니다.'))
    elif(num == 9):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '변경 오류', logo = set_data['name'], data = '그런 계정이 없습니다.'))
    elif(num == 10):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '변경 오류', logo = set_data['name'], data = '비밀번호가 다릅니다.'))
    elif(num == 11):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '로그인 오류', logo = set_data['name'], data = '이미 로그인 되어 있습니다.'))
    elif(num == 12):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '로그인 오류', logo = set_data['name'], data = '그런 계정이 없습니다.'))
    elif(num == 13):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '로그인 오류', logo = set_data['name'], data = '비밀번호가 다릅니다.'))
    elif(num == 14):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '업로드 오류', logo = set_data['name'], data = 'jpg, gif, jpeg, png(대 소문자 상관 없음)만 가능 합니다.'))
    elif(num == 15):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '편집 오류', logo = set_data['name'], data = '편집 기록은 500자를 넘을 수 없습니다.'))
    elif(num == 16):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '업로드 오류', logo = set_data['name'], data = '동일한 이름의 파일이 있습니다.'))
    elif(num == 17):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '업로드 오류', logo = set_data['name'], data = '파일 용량은 ' + set_data['upload'] + 'MB를 넘길 수 없습니다.'))
    elif(num == 18):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '편집 오류', logo = set_data['name'], data = '내용이 원래 문서와 동일 합니다.'))
    elif(num == 19):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '이동 오류', logo = set_data['name'], data = '이동 하려는 곳에 문서가 이미 있습니다.'))
    elif(num == 20):
        return(template('other', custom = custom_css_user(), license = set_data['license'], login = login_check(), title = '비밀번호 오류', logo = set_data['name'], data = '재 확인이랑 비밀번호가 다릅니다.'))
    else:
        return(redirect('/'))

@error(404)
def error_404(error):
    return(redirect('/w/' + url_pas(set_data['frontpage'])))
    
run(app = app, server='tornado', host = '0.0.0.0', port = int(set_data['port']))
