from .tool.func import *

def list_acl_2(conn):
    curs = conn.cursor()

    div = '<ul>'

    if tool_acl_check('list_acl') == 1:
        return re_error('/ban')
    
    curs.execute(db_change("select title, why from acl where decu != '' or dis != '' or view != '' order by title desc"))
    list_data = curs.fetchall()
    for data in list_data:
        if not re.search(r'^user:', data[0]) and not re.search(r'^file:', data[0]):
            curs.execute(db_change("select time from re_admin where what like ? order by time desc limit 1"), ['acl (' + data[0] + ')%'])
            time_data = curs.fetchall()
            if time_data:
                time_data = time_data[0][0] + ' | '
            else:
                time_data = ''
                
            if data[1] != '':
                why = ' | ' + data[1]
            else:
                why = ''

            div += '' + \
                '<li>' + \
                    time_data + \
                    '<a href="/acl/' + url_pas(data[0]) + '">' + data[0] + '</a>' + \
                     why + \
                '</li>' + \
            ''

    div += '</ul>'

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('acl_document_list'), wiki_set(), custom(), other2([0, 0])],
        data = div,
        menu = [['other', load_lang('return')]]
    ))