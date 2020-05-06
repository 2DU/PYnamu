from .tool.func import *

def list_user_topic_2(conn, name):
    curs = conn.cursor()

    if tool_acl_check('topic_record') == 1:
        return re_error('/ban')
    
    num = int(number_check(flask.request.args.get('num', '1')))
    if num * 50 > 0:
        sql_num = num * 50 - 50
    else:
        sql_num = 0

    div = '''
        <table id="main_table_set">
            <tbody>
                <tr>
                    <td id="main_table_width">''' + load_lang('discussion_name') + '''</td>
                    <td id="main_table_width">''' + load_lang('writer') + '''</td>
                    <td id="main_table_width">''' + load_lang('time') + '''</td>
                </tr>
    '''
    sub = '(' + html.escape(name) + ')'
    pas_name = ip_pas(name)

    curs.execute(db_change("select code, id, date from topic where ip = ? order by date desc limit ?, 50"), [name, sql_num])
    data_list = curs.fetchall()
    for data in data_list:
        title = html.escape(data[0])

        curs.execute(db_change("select title, sub from rd where code = ?"), [data[0]])
        other_data = curs.fetchall()
        
        div += '' + \
            '<tr>' + \
                '<td>' + \
                    '<a href="/thread/' + data[0] + '#' + data[1] + '">' + other_data[0][1] + '#' + data[1] + '</a> (' + other_data[0][0] + ')' + \
                '</td>' + \
                '<td>' + pas_name + '</td>' + \
                '<td>' + data[2] + '</td>' + \
            '</tr>' + \
        ''

    div += '' + \
            '</tbody>' + \
        '</table>' + \
    ''
    div += next_fix('/topic_record/' + url_pas(name) + '?num=', num, data_list)
    
    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('discussion_record'), wiki_set(), custom(), other2([sub, 0])],
        data = div,
        menu = [
            ['other', load_lang('other')], 
            ['user', load_lang('user')], 
            ['count/' + url_pas(name), load_lang('count')], 
            ['record/' + url_pas(name), load_lang('record')]
        ]
    ))