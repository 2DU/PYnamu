from .tool.func import *

def list_title_index_2(conn):
    curs = conn.cursor()

    if tool_acl_check('title_index') == 1:
        return re_error('/ban')
    
    page = int(number_check(flask.request.args.get('page', '1')))
    num = int(number_check(flask.request.args.get('num', '100')))
    if page * num > 0:
        sql_num = page * num - num
    else:
        sql_num = 0

    all_list = sql_num + 1

    if num > 1000:
        return re_error('/error/3')

    data = '<a href="/title_index?num=250">(250)</a> <a href="/title_index?num=500">(500)</a> <a href="/title_index?num=1000">(1000)</a>'

    curs.execute(db_change("select title from data order by title asc limit ?, ?"), [sql_num, num])
    title_list = curs.fetchall()
    if title_list:
        data += '<hr class=\"main_hr\"><ul>'

    for list_data in title_list:
        data += '<li>' + str(all_list) + '. <a href="/w/' + url_pas(list_data[0]) + '">' + list_data[0] + '</a></li>'
        all_list += 1

    if page == 1:
        count_end = []

        curs.execute(db_change('select data from other where name = "count_all_title"'))
        if int(curs.fetchall()[0][0]) < 30000:
            curs.execute(db_change("select count(title) from data"))
            count = curs.fetchall()
            if count:
                count_end += [count[0][0]]
            else:
                count_end += [0]

            sql_list = ['category:', 'user:', 'file:']
            for sql in sql_list:
                curs.execute(db_change("select count(title) from data where title like ?"), [sql + '%'])
                count = curs.fetchall()
                if count:
                    count_end += [count[0][0]]
                else:
                    count_end += [0]

            count_end += [count_end[0] - count_end[1]  - count_end[2]  - count_end[3]]

            data += '''
                </ul>
                <hr class=\"main_hr\">
                <ul>
                    <li>''' + load_lang('all') + ' : ' + str(count_end[0]) + '''</li>
                </ul>
                <hr class=\"main_hr\">
                <ul>
                    <li>''' + load_lang('category') + ' : ' + str(count_end[1]) + '''</li>
                    <li>''' + load_lang('user_document') + ' : ' + str(count_end[2]) + '''</li>
                    <li>''' + load_lang('file') + ' : ' + str(count_end[3]) + '''</li>
                    <li>''' + load_lang('other') + ' : ' + str(count_end[4]) + '''</li>
            '''
        else:
            data += '''
                </ul>
                <hr class=\"main_hr\">
                <ul>
                    <li>''' + load_lang('all') + ' : ' + all_title[0][0] + '''</li>
            '''

    data += '</ul>' + next_fix('/title_index?num=' + str(num) + '&page=', page, title_list, num)
    sub = ' (' + str(num) + ')'

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('all_document_list'), wiki_set(), custom(), other2([sub, 0])],
        data = data,
        menu = [['other', load_lang('return')]]
    ))
