from .tool.func import *

def view_diff_data_2(name):
    

    first = number_check(flask.request.args.get('first', '1'))
    second = number_check(flask.request.args.get('second', '1'))

    sqlQuery("select title from history where title = ? and (id = ? or id = ?) and hide = 'O'", [name, first, second])
    if sqlQuery("fetchall") and admin_check(6) != 1:
        return re_error('/error/3')

    sqlQuery("select data from history where id = ? and title = ?", [first, name])
    first_raw_data = sqlQuery("fetchall")
    if first_raw_data:
        sqlQuery("select data from history where id = ? and title = ?", [second, name])
        second_raw_data = sqlQuery("fetchall")
        if second_raw_data:
            first_data = html.escape(first_raw_data[0][0])            
            second_data = html.escape(second_raw_data[0][0])

            if first == second:
                result = '-'
            else:            
                diff_data = difflib.SequenceMatcher(None, first_data, second_data)
                result = re.sub('\r', '', diff(diff_data))
            
            return easy_minify(flask.render_template(skin_check(), 
                imp = [name, wiki_set(), custom(), other2([' (' + load_lang('compare') + ')', 0])],
                data = '<pre>' + result + '</pre>',
                menu = [['history/' + url_pas(name), load_lang('return')]]
            ))

    return redirect('/history/' + url_pas(name))