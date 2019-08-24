from .tool.func import *
import pymysql

def search_deep_2(conn, name):
    curs = conn.cursor()

    if name == '':
        return redirect()

    num = int(number_check(flask.request.args.get('num', '1')))
    if num * 50 > 0:
        sql_num = num * 50 - 50
    else:
        sql_num = 0

    div = '<ul>'
    
    div_plus = ''
    test = ''
    
    curs.execute("select title from data where title = %s", [name])
    if curs.fetchall():
        link_id = ''
    else:
        link_id = 'id="not_thing"'
    
    div =   '''
            <ul>
                <li>
                    <a ''' + link_id + ' href="/w/' + url_pas(name) + '">' + name + '''</a>
                </li>
            </ul>
            <hr class=\"main_hr\">
            <ul>
            '''

    # 여기 개선 필요
    curs.execute(
        "select distinct title, case when title like %s then "
        "%s else %s end from data where title like %s or data like %s "
        "order by case when title like %s "
        "then 1 else 2 end limit %s, 50",
        ("%" + name + "%", "제목", "내용", "%" + name + "%", "%" + name + "%", "%" + name + "%", sql_num)
    )
    all_list = curs.fetchall()
    if all_list:
        test = all_list[0][1]
        
        for data in all_list:
            if data[1] != test:
                div_plus += '</ul><hr class=\"main_hr\"><ul>'
                
                test = data[1]

            div_plus += '<li><a href="/w/' + url_pas(data[0]) + '">' + data[0] + '</a> (' + data[1] + ')</li>'

    div += div_plus + '</ul>'
    div += next_fix('/search/' + url_pas(name) + '?num=', num, all_list)

    return easy_minify(flask.render_template(skin_check(), 
        imp = [name, wiki_set(), custom(), other2([' (' + load_lang('search') + ')', 0])],
        data = div,
        menu = 0
    ))