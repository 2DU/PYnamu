from .tool.func import *

def api_recent_change_2(conn):
    curs = conn.cursor()

    if tool_acl_check('recent_changes') == 1:
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

    curs.execute(db_change('' + \
        'select id, title, date, ip, send, leng from history ' + \
        "where not title like 'user:%' " + \
        'order by date desc ' + \
        'limit ?, ?' + \
    ''), [page, num])
    all_list = curs.fetchall()
    if all_list:
        return flask.jsonify(all_list)
    else:
        return flask.jsonify({})