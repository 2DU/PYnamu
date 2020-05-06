from .tool.func import *

def list_not_close_topic_2(conn):
    curs = conn.cursor()

    if tool_acl_check('not_close_topic') == 1:
        return re_error('/ban')
    
    div = '<ul>'

    curs.execute(db_change('select title, sub, date, code from rd where stop != "O" order by date desc'))
    n_list = curs.fetchall()
    for data in n_list:
        div += '<li>' + data[2] + ' | <a href="/thread/' + data[3] + '">' + html.escape(data[1]) + '</a> (' + html.escape(data[0]) + ')</li>'

    div += '</ul>'

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('open_discussion_list'), wiki_set(), custom(), other2([0, 0])],
        data = div,
        menu = [['manager', load_lang('return')]]
    ))