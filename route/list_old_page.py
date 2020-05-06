from .tool.func import *

def list_old_page_2(conn):
    curs = conn.cursor()

    if tool_acl_check('old_page') == 1:
        return re_error('/ban')
    
    num = int(number_check(flask.request.args.get('num', '1')))
    if num * 50 > 0:
        sql_num = num * 50 - 50
    else:
        sql_num = 0

    curs.execute(db_change('select data from other where name = "count_all_title"'))
    if int(curs.fetchall()[0][0]) > 30000:
        return re_error('/error/25')

    div = '<ul>'

    curs.execute(db_change('' + \
        'select title, date from history h ' + \
        "where title not like 'user:%' and title not like 'category:%' and title not like 'file:%' and " + \
        "exists (select title from data where title = h.title) and " + \
        "not exists (select title from back where link = h.title and type = 'redirect') " + \
        'group by title ' + \
        'order by date asc ' + \
        'limit ?, 50' + \
    ''), [sql_num])
    n_list = curs.fetchall()
    for data in n_list:
        div += '<li><a href="/w/' + url_pas(data[0]) + '">' + html.escape(data[0]) + '</a> (' + re.sub(r' .*$', '', data[1]) + ')</li>'

    div += '</ul>' + next_fix('/old_page?num=', num, n_list)

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('old_page'), wiki_set(), custom(), other2([0, 0])],
        data = div,
        menu = [['other', load_lang('return')]]
    ))
