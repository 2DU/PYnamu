from .tool.func import *

def list_please_2(conn):
    curs = conn.cursor()

    if tool_acl_check('please') == 1:
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

    curs.execute(db_change("select distinct title from back where type = 'no' order by title asc limit ?, 50"), [sql_num])
    data_list = curs.fetchall()
    for data in data_list:
        div += '<li><a id="not_thing" href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a></li>'

    div += '</ul>' + next_fix('/please?num=', num, data_list)

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('need_document'), wiki_set(), custom(), other2([0, 0])],
        data = div,
        menu = [['other', load_lang('return')]]
    ))
