from .tool.func import *

def api_search_2(conn, name):
    curs = conn.cursor()

    if tool_acl_check('search') == 1:
        return flask.jsonify({})
    
    num = int(number_check(flask.request.args.get('num', '10')))
    if not num > 0:
        num = 1

    if num > 1000:
        num = 1

    page = int(number_check(flask.request.args.get('page', '1')))
    if page * num > 0:
        page = page * num - num
    else:
        page = 0

    curs.execute(db_change('select data from other where name = "count_all_title"'))
    if int(curs.fetchall()[0][0]) < 30000:
        curs.execute(db_change("" + \
            "select distinct title, case " + \
            "when title >= '' and title like ? then 'title' else 'data' end from data " + \
            "where title >= '' and (title like ? or data like ?) order by case " + \
            "when title >= '' and title like ? then 1 else 2 end limit ?, ?"),
            ['%' + name + '%', '%' + name + '%', '%' + name + '%', '%' + name + '%', page, num]
        )
    else:
        curs.execute(db_change("select title from data where title >= '' and title like ? order by title limit ?, ?"),
            ['%' + name + '%', page, num]
        )
    all_list = curs.fetchall()
    if all_list:
        return flask.jsonify(all_list)
    else:
        return flask.jsonify({})