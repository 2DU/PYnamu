from .tool.func import *

def recent_discuss_2():
    

    div = ''
    
    if flask.request.args.get('what', 'normal') == 'normal':
        div += '<a href="/recent_discuss?what=close">(' + load_lang('close_discussion') + ')</a>'
       
        m_sub = 0
    else:
        div += '<a href="/recent_discuss">(' + load_lang('open_discussion') + ')</a>'
        
        m_sub = ' (' + load_lang('closed') + ')'

    div +=  '''
            <hr class=\"main_hr\">
            <table id="main_table_set">
                <tbody>
                    <tr>
                        <td id="main_table_width_half">''' + load_lang('discussion_name') + '''</td>
                        <td id="main_table_width_half">''' + load_lang('time') + '''</td>
                    </tr>
            '''
    
    if m_sub == 0:
        sqlQuery("select title, sub, date from rd where not stop = 'O' order by date desc limit 50")
    else:
        sqlQuery("select title, sub, date from rd where stop = 'O' order by date desc limit 50")
        
    for data in sqlQuery("fetchall"):
        title = html.escape(data[0])
        sub = html.escape(data[1])

        div += '<tr><td><a href="/topic/' + url_pas(data[0]) + '/sub/' + url_pas(data[1]) + '">' + title + '</a> (' + sub + ')</td><td>' + data[2] + '</td></tr>'
    
    div += '</tbody></table>'
            
    return easy_minify(flask.render_template(skin_check(), 
        imp = [load_lang('recent_discussion'), wiki_set(), custom(), other2([m_sub, 0])],
        data = div,
        menu = 0
    ))