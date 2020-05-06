from .tool.func import *

def recent_changes_2(conn, name, tool):
    curs = conn.cursor()

    if tool_acl_check('recent_changes') == 1:
        return re_error('/ban')
    
    if flask.request.method == 'POST':
        return redirect(
            '/diff/' + url_pas(name) +
            '?first=' + flask.request.form.get('b', '1') +
            '&second=' + flask.request.form.get('a', '1')
        )
    else:
        ban = ''
        select = ''
        sub = ''

        div = '''
            <table id="main_table_set">
                <tbody>
                    <tr>
        '''

        num = int(number_check(flask.request.args.get('num', '1')))
        if num * 50 > 0:
            sql_num = num * 50 - 50
        else:
            sql_num = 0

        if name:
            if tool == 'history':
                sub += ' (' + load_lang('history') + ')'

                div += '''
                    <td id="main_table_width">''' + load_lang('version') + '''</td>
                    <td id="main_table_width">''' + load_lang('editor') + '''</td>
                    <td id="main_table_width">''' + load_lang('time') + '''</td>
                '''

                tool_select = flask.request.args.get('tool', 'normal')
                if tool_select == 'move':
                    plus_sql = 'where send >= "" and (send like ? or send like ?) and type = "" '
                    plus_list = ['%(<a>' + name +'</a>%', '%<a>' + name + '</a> move)', sql_num]
                    sub += ' (' + load_lang('move') + ')'
                elif tool_select == 'delete':
                    plus_sql = 'where send like "%(delete)" and title = ? and type = "" '
                    plus_list = [name, sql_num]
                    sub += ' (' + load_lang('delete') + ')'
                elif tool_select == 'revert':
                    plus_sql = 'where send >= "" and send like ? and title = ? and type = "" '
                    plus_list = ['%(r%)', name, sql_num]
                    sub += ' (' + load_lang('revert') + ')'
                else:
                    plus_sql = 'where title = ? and type = "" '
                    plus_list = [name, sql_num]

                curs.execute(db_change('' + \
                    'select id, title, date, ip, send, leng, hide from history ' + \
                    plus_sql + \
                    'order by id + 0 desc ' + \
                    "limit ?, 50" + \
                ''), plus_list)
            else:
                div +=  '''
                    <td id="main_table_width">''' + load_lang('document_name') + '''</td>
                    <td id="main_table_width">''' + load_lang('editor') + '''</td>
                    <td id="main_table_width">''' + load_lang('time') + '''</td>
                '''

                div = '<a href="/topic_record/' + url_pas(name) + '">(' + load_lang('discussion') + ')</a><hr class=\"main_hr\">' + div

                curs.execute(db_change('' + \
                    'select id, title, date, ip, send, leng, hide from history ' + \
                    "where ip = ? and type = '' order by date desc limit ?, 50" + \
                ''), [name, sql_num])
        else:
            div +=  '''
                <td id="main_table_width">''' + load_lang('document_name') + '''</td>
                <td id="main_table_width">''' + load_lang('editor') + '''</td>
                <td id="main_table_width">''' + load_lang('time') + '''</td>
            '''
            sub = ''
            set_type = flask.request.args.get('set', 'normal')

            if set_type == 'move':
                plus_sql = 'where send >= "" and send like "%</a> move)" and '
                sub += ' (' + load_lang('move') + ')'
            elif set_type == 'delete':
                plus_sql = 'where send like "%(delete)" and '
                sub += ' (' + load_lang('delete') + ')'
            elif set_type == 'revert':
                plus_sql = 'where send >= "" and send like "%(r%)" and '
                sub += ' (' + load_lang('revert') + ')'
            else:
                plus_sql = 'where '

            if set_type == 'req':
                plus_sql = 'where type = "req" '
                sub += ' (' + load_lang('edit_req') + ')'
            else:
                plus_sql += 'type = "" '
            
            if set_type == 'user':
                plus_sql = 'where title like "user:%" '
                sub += ' (' + load_lang('user') + ')'
            else:
                plus_sql += 'and not title like "user:%" '

            curs.execute(db_change('' + \
                'select id, title, date, ip, send, leng, hide from history ' + \
                plus_sql + \
                'order by date desc ' + \
                'limit ?, 50' + \
            ''), [sql_num])

        div += '</tr>'

        data_list = curs.fetchall()
        for data in data_list:
            select += '<option value="' + data[0] + '">' + data[0] + '</option>'
            send = '<br>'

            if data[4]:
                if not re.search(r"^(?: *)$", data[4]):
                    send = data[4]

            if re.search(r"\+", data[5]):
                leng = '<span style="color:green;">(' + data[5] + ')</span>'
            elif re.search(r"\-", data[5]):
                leng = '<span style="color:red;">(' + data[5] + ')</span>'
            else:
                leng = '<span style="color:gray;">(' + data[5] + ')</span>'

            ip = ip_pas(data[3])
            if tool == 'history':
                m_tool = '<a href="/history_tool/' + url_pas(data[1]) + '?num=' + data[0] + '&type=history">(' + load_lang('tool') + ')</a>'
            else:
                m_tool = '<a href="/history_tool/' + url_pas(data[1]) + '?num=' + data[0] + '">(' + load_lang('tool') + ')</a>'

            style = ['', '']
            date = data[2]

            if data[6] == 'O':
                if admin_check(6) == 1:
                    style[0] = 'id="toron_color_grey"'
                    style[1] = 'id="toron_color_grey"'

                    send += ' (' + load_lang('hide') + ')'
                else:
                    ip = ''
                    ban = ''
                    date = ''

                    send = '(' + load_lang('hide') + ')'

                    style[0] = 'style="display: none;"'
                    style[1] = 'id="toron_color_grey"'

            if tool == 'history':
                title = '<a href="/w/' + url_pas(name) + '?num=' + data[0] + '">r' + data[0] + '</a> '
            else:
                if not name and set_type == 'req':
                    title = '<a href="/edit_req/' + url_pas(data[1]) + '?r=' + data[0] + '">' + html.escape(data[1]) + ' (r' + data[0] + ')</a> '
                else:
                    title = '<a href="/w/' + url_pas(data[1]) + '">' + html.escape(data[1]) + '</a> '
                    title += '<a href="/history/' + url_pas(data[1]) + '">(r' + data[0] + ')</a> '

            div += '''
                <tr ''' + style[0] + '''>
                    <td>''' + title + m_tool + ' ' + leng + '''</td>
                    <td>''' + ip + ban + '''</td>
                    <td>''' + date + '''</td>
                </tr>
                <tr ''' + style[1] + '''>
                    <td colspan="3">''' + send_parser(send) + '''</td>
                </tr>
            '''

        div += '''
                </tbody>
            </table>
        '''

        if name:
            if tool == 'history':
                if tool_select == 'normal':
                    div = '' + \
                        '<a href="?tool=move">(' + load_lang('move') + ')</a> ' + \
                        '<a href="?tool=delete">(' + load_lang('delete') + ')</a> ' + \
                        '<a href="?tool=revert">(' + load_lang('revert') + ')</a>' + \
                        '<hr class="main_hr">' + div + \
                    ''

                    div = '''
                        <form method="post">
                            <select name="a">''' + select + '''</select> <select name="b">''' + select + '''</select>
                            <button type="submit">''' + load_lang('compare') + '''</button>
                        </form>
                        <hr class=\"main_hr\">
                    ''' + div

                    menu = [['w/' + url_pas(name), load_lang('return')]]

                    if admin_check() == 1:
                        menu += [['add_history/' + url_pas(name), load_lang('history_add')]]
                else:
                    menu = [['history/' + url_pas(name), load_lang('return')]]

                title = name
                div += next_fix('/history/' + url_pas(name) + '?tool=' + tool_select + '&num=', num, data_list)
            else:
                title = load_lang('edit_record')
                menu = [['other', load_lang('other')], ['user', load_lang('user')], ['count/' + url_pas(name), load_lang('count')]]
                div += next_fix('/record/' + url_pas(name) + '?num=', num, data_list)
        else:
            div = '' + \
                '<a href="?set=normal">(' + load_lang('normal') + ')</a> ' + \
                '<a href="?set=user">(' + load_lang('user_document') + ')</a> ' + \
                '<a href="?set=req">(' + load_lang('edit_req') + ')</a> ' + \
                '<a href="?set=move">(' + load_lang('move') + ')</a> ' + \
                '<a href="?set=delete">(' + load_lang('delete') + ')</a> ' + \
                '<a href="?set=revert">(' + load_lang('revert') + ')</a>' + \
                '<hr class="main_hr">' + div + \
            ''

            menu = 0
            title = load_lang('recent_change')
            div += next_fix('/recent_changes?set=' + set_type + '&num=', num, data_list)

        if sub == '':
            sub = 0

        return easy_minify(flask.render_template(skin_check(),
            imp = [title, wiki_set(), custom(), other2([sub, 0])],
            data = div,
            menu = menu
        ))