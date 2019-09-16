from .tool.func import *

def topic_stop_2(name, sub):
    

    if admin_check(3) != 1:
        return re_error('/error/3')

    ip = ip_check()
    time = get_time()

    if flask.request.method == 'POST':
        sqlQuery("select id from topic where title = ? and sub = ? order by id + 0 desc limit 1", [name, sub])
        topic_check = sqlQuery("fetchall")
        if topic_check:
            stop_d = flask.request.form.get('stop_d', '')
            why_d = flask.request.form.get('why', '')
            agree_d = flask.request.form.get('agree', '')

            sqlQuery("update rd set stop = ?, agree = ? where title = ? and sub = ?", [
                stop_d,
                agree_d,
                name, 
                sub
            ])

            if stop_d == 'S':
                t_state = 'Stop'
            elif stop_d == 'O':
                t_state = 'Close'
            else:
                t_state = 'Normal'

            sqlQuery("insert into topic (id, title, sub, data, date, ip, block, top) values (?, ?, ?, ?, ?, ?, '', '1')", [
                str(int(topic_check[0][0]) + 1), 
                name, 
                sub, 
                t_state + (' (Agree)' if agree_d != '' else '') + (('[br][br]Why : ' + why_d) if why_d else ''), 
                time, 
                ip
            ])

            rd_plus(name, sub, time)

        return redirect('/topic/' + url_pas(name) + '/sub/' + url_pas(sub))    
    else:
        stop_d_list = ''
        agree_check = ''

        sqlQuery("select stop, agree from rd where title = ? and sub = ? limit 1", [name, sub])
        rd_d = sqlQuery("fetchall")
        if rd_d[0][0] == 'O':
            stop_d_list += '''
                <option value="O">Close</option>
                <option value="">Normal</option>
                <option value="S">Stop</option>
            '''
        elif rd_d[0][0] == 'S':
            stop_d_list += '''
                <option value="S">Stop</option>
                <option value="">Normal</option>
                <option value="O">Close</option>
            '''
        else:
            stop_d_list += '''
                <option value="">Normal</option>
                <option value="S">Stop</option>
                <option value="O">Close</option>
            '''

        if rd_d[0][1] == 'O':
            agree_check = 'checked="checked"'
        else:
            agree_check = ''

        return easy_minify(flask.render_template(skin_check(),
            imp = [name, wiki_set(), custom(), other2([' (topic_tool)', 0])],
            data = '''
                <hr class=\"main_hr\">
                <form method="post">
                    <select name="stop_d">
                        ''' + stop_d_list + '''
                    </select>
                    <hr class=\"main_hr\">
                    <input type="checkbox" name="agree" value="O" ''' + agree_check + '''> Agree
                    <hr class=\"main_hr\">
                    <input placeholder="''' + load_lang('why') + '''" name="why" type="text">
                    <hr class=\"main_hr\">
                    <span>''' + load_lang('markup_enabled') + '''</span>
                    <hr class=\"main_hr\">
                    <button type="submit">''' + load_lang('save') + '''</button>
                </form>
            ''',
            menu = [['topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/tool', load_lang('return')]]
        ))
