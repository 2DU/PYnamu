from .tool.func import *

def list_user_2(conn):
    curs = conn.cursor()

    if tool_acl_check('user_log') == 1:
        return re_error('/ban')
    
    num = int(number_check(flask.request.args.get('num', '1')))
    if num * 50 > 0:
        sql_num = num * 50 - 50
    else:
        sql_num = 0

    list_data = '<ul>'

    admin_one = admin_check(1)

    curs.execute(db_change("select id, date from user order by date desc limit ?, 50"), [sql_num])
    user_list = curs.fetchall()
    for data in user_list:
        if admin_one == 1:
            curs.execute(db_change("select block from ban where block = ?"), [data[0]])
            if curs.fetchall():
                ban_button = ' <a href="/ban/' + url_pas(data[0]) + '">(' + load_lang('ban_release') + ')</a>'
            else:
                ban_button = ' <a href="/ban/' + url_pas(data[0]) + '">(' + load_lang('ban') + ')</a>'
        else:
            ban_button = ''

        list_data += '<li>' + ip_pas(data[0]) + ban_button

        if data[1] != '':
            list_data += ' (' + data[1] + ')'

        list_data += '</li>'

    if num == 1:
        list_data += '''
            </ul>
        '''

    list_data += next_fix('/user_log?num=', num, user_list)

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('member_list'), wiki_set(), custom(), other2([0, 0])],
        data = list_data,
        menu = [['other', load_lang('return')]]
    ))