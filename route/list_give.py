from .tool.func import *

def list_give_2(conn):
    curs = conn.cursor()

    if tool_acl_check('give_log') == 1:
        return re_error('/ban')

    list_data = '<ul>'
    back = ''

    curs.execute(db_change("select distinct name from alist order by name asc"))
    for data in curs.fetchall():
        if back != data[0]:
            back = data[0]
            
        if admin_check(None) == 1:
            delGroupLnk = ' <a href="/delete_admin_group/' + url_pas(data[0]) + '">(' + load_lang("delete") + ')</a>'
        else:
            delGroupLnk = ""

        list_data += '<li><a href="/admin_plus/' + url_pas(data[0]) + '">' + data[0] + '</a>' + delGroupLnk + '</li>'

    list_data += '</ul><hr class=\"main_hr\"><a href="/manager/8">(' + load_lang('add') + ')</a>'

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('admin_group_list'), wiki_set(), custom(), other2([0, 0])],
        data = list_data,
        menu = [['manager', load_lang('return')]]
    ))    
