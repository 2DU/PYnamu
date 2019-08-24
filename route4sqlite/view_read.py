from .tool.func import *

def view_read_2(conn, name):
    curs = conn.cursor()

    sub = ''
    acl = ''
    div = ''
    plus_d = ''
    plus_t = []

    num = flask.request.args.get('num', None)
    if num:
        num = int(number_check(num))
    else:
        if not flask.request.args.get('from', None):
            curs.execute("select title from back where link = ? and type = 'redirect'", [name])
            r_db = curs.fetchall()
            if r_db:
                r_data = link_fix(r_db[0][0])
            
                return redirect('/w/' + r_data[0] + '?from=' + name + r_data[1])

    curs.execute("select sub from rd where title = ? and not stop = 'O' order by date desc", [name])
    if curs.fetchall():
        sub += ' (' + load_lang('discussion') + ')'

    curs.execute("select link from back where title = ? and type = 'cat' order by link asc", [name])
                
    curs.execute("select title from data where title like ?", ['%' + name + '/%'])
    if curs.fetchall():
        down = 1
    else:
        down = 0
        
    m = re.search("^(.*)\/(.*)$", name)
    if m:
        uppage = m.groups()[0]
    else:
        uppage = 0
        
    if re.search('^category:', name):        
        curs.execute("select link from back where title = ? and type = 'cat' order by link asc", [name])
        back = curs.fetchall()
        if back:
            div = '<br><h2 id="cate_normal">' + load_lang('category') + '</h2><ul>'
            u_div = ''

            for data in back:    
                if re.search('^category:', data[0]):
                    u_div += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a></li>'
                else:
                    curs.execute("select title from back where title = ? and type = 'include'", [data[0]])
                    db_data = curs.fetchall()
                    if db_data:
                        div += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a> <a id="inside" href="/xref/' + url_pas(data[0]) + '">(' + load_lang('backlink') + ')</a></li>'
                    else: 
                        div += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a></li>'

            div += '</ul>'
            
            if div == '<br><h2 id="cate_normal">' + load_lang('category') + '</h2><ul></ul>':
                div = ''
            
            if u_div != '':
                div += '<br><h2 id="cate_under">' + load_lang('under_category') + '</h2><ul>' + u_div + '</ul>'


    if num:
        curs.execute("select title from history where title = ? and id = ? and hide = 'O'", [name, str(num)])
        if curs.fetchall() and admin_check(6) != 1:
            return redirect('/history/' + url_pas(name))

        curs.execute("select title, data from history where title = ? and id = ?", [name, str(num)])
    else:
        curs.execute("select title, data from data where title = ?", [name])
    
    data = curs.fetchall()
    if data:
        else_data = data[0][1]
    else:
        else_data = None

    curs.execute("select decu from acl where title = ?", [name])
    data = curs.fetchall()
    if data:
        acl += ' (' + load_lang('acl') + ')'
            
    if flask.request.args.get('from', None) and else_data:
        else_data = re.sub('^\r\n', '', else_data)
        else_data = re.sub('\r\n$', '', else_data)
            
    end_data = render_set(
        title = name,
        data = else_data
    )

    if end_data == 'HTTP Request 401.3':
        response_data = 401
        
        curs.execute('select data from other where name = "error_401"')
        sql_d = curs.fetchall()
        if sql_d and sql_d[0][0] != '':
            end_data = '<h2>' + load_lang('error') + '</h2><ul><li>' + sql_d[0][0] + '</li></ul>'
        else:
            end_data = '<h2>' + load_lang('error') + '</h2><ul><li>' + load_lang('authority_error') + '</li></ul>'
    elif end_data == 'HTTP Request 404':
        response_data = 404
        
        curs.execute('select data from other where name = "error_404"')
        sql_d = curs.fetchall()
        if sql_d and sql_d[0][0] != '':
            end_data = '<h2>' + load_lang('error') + '</h2><ul><li>' + sql_d[0][0] + '</li></ul>'
        else:
            end_data = '<h2>' + load_lang('error') + '</h2><ul><li>' + load_lang('decument_404_error') + '</li></ul>'
            
        curs.execute('select ip, date, leng, send from history where title = ? order by id desc limit 3', [name])
        sql_d = curs.fetchall()
        if sql_d:
            end_data += '<h2>' + load_lang('history') + '</h2><ul>'
            for i in sql_d:
                if re.search("\+", i[2]):
                    leng = '<span style="color:green;">(' + i[2] + ')</span>'
                elif re.search("\-", i[2]):
                    leng = '<span style="color:red;">(' + i[2] + ')</span>'
                else:
                    leng = '<span style="color:gray;">(' + i[2] + ')</span>'
            
                end_data += '<li>' + i[1] + ' | ' + ip_pas(i[0]) + ' | ' + leng + (' | ' + i[3] if i[3] != '' else '') + '</li>'
                
            end_data += '<li><a href="/history/' + url_pas(name) + '">(...)</a></li></ul>'
    else:
        response_data = 200
    
    if num:
        menu = [['history/' + url_pas(name), load_lang('history')]]
        sub = ' (r' + str(num) + ')'
        acl = ''
        r_date = 0
    else:
        if response_data == 404:
            menu = [['edit/' + url_pas(name), load_lang('create')]]
        else:
            menu = [['edit/' + url_pas(name), load_lang('edit')]]

        menu += [['topic/' + url_pas(name), load_lang('discussion')], ['history/' + url_pas(name), load_lang('history')], ['xref/' + url_pas(name), load_lang('backlink')], ['acl/' + url_pas(name), load_lang('acl')]]

        if flask.request.args.get('from', None):
            menu += [['w/' + url_pas(name), load_lang('pass')]]
            end_data = '''
                <div id="redirect">
                    <a href="/w/''' + url_pas(flask.request.args.get('from', None)) + '?from=' + url_pas(name) + '">' + flask.request.args.get('from', None) + '</a> → ' + name + '''
                </div>
                <br>
            ''' + end_data

        if uppage != 0:
            menu += [['w/' + url_pas(uppage), load_lang('upper')]]

        if down:
            menu += [['down/' + url_pas(name), load_lang('sub')]]
    
        curs.execute("select date from history where title = ? order by date desc limit 1", [name])
        date = curs.fetchall()
        if date:
            r_date = date[0][0]
        else:
            r_date = 0

    div = end_data + div
            
    adsense_code = '<div align="center" style="display: block; margin-bottom: 10px;">{}</div>'

    curs.execute("select data from other where name = 'adsense'")
    adsense_enabled = curs.fetchall()[0][0]
    if adsense_enabled == 'True':
        curs.execute("select data from other where name = 'adsense_code'")
        adsense_code = adsense_code.format(curs.fetchall()[0][0])
    else:
        adsense_code = adsense_code.format('')

    curs.execute("select data from other where name = 'body'")
    body = curs.fetchall()
    if body:
        div = body[0][0] + '<hr class=\"main_hr\">' + div
    
    div = adsense_code + '<div>' + div + '</div>'

    # 이 부분 개선 필요
    m = re.search("^user:([^/]*)", name)
    if m:
        g = m.groups()

        plus_d = '''
            <table>
                <tbody>
                    <tr>
                        <td>''' + load_lang('authority') + '''</td>
                        <td>{}</td>
                    </tr>
                    <tr>
                        <td>''' + load_lang('state') + '''</td>
                        <td>{}</td>
                    </tr>
                </tbody>
            </table>
        '''
        
        curs.execute("select acl from user where id = ?", [g[0]])
        data = curs.fetchall()
        if data:
            if data[0][0] != 'user':
                plus_t += [data[0][0]]
            else:
                plus_t += [load_lang('member')]
        else:
            plus_t += [load_lang('normal')]

        if ban_check(g[0]) == 0:
            plus_t += [load_lang('normal')]
        else:
            match = re.search("^([0-9]{1,3}\.[0-9]{1,3})", g[0])
            if match:
                match = match.groups()[0]
            else:
                match = '-'

            curs.execute("select end, login, band from ban where block = ? or block = ?", [g[0], match])
            block_data = curs.fetchall()
            if block_data:
                if block_data[0][0] != '':
                    plus_t += [load_lang('period') + ' : ' + block_data[0][0]]
                else:
                    plus_t += [load_lang('limitless')]

                if block_data[0][1] != '':
                    plus_t += [load_lang('login_able')]

                if block_data[0][2] == 'O':
                    plus_t += [load_lang('band_blocked')]

        plus_d = plus_d.format(plus_t[0], plus_t[1])

    return easy_minify(flask.render_template(skin_check(), 
        imp = [flask.request.args.get('show', name), wiki_set(), custom(), other2([sub + acl, r_date])],
        data = plus_d + div,
        menu = menu
    )), response_data