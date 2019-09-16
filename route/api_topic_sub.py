from .tool.func import *

def api_topic_sub_2(name, sub, time):
    

    if flask.request.args.get('num', None):
        sqlQuery("select id, data, date, ip, block, top from topic where title = ? and sub = ? and id + 0 = ? + 0 order by id + 0 asc", [
            name, 
            sub, 
            flask.request.args.get('num', '')
        ])
    elif flask.request.args.get('top', None):
        sqlQuery("select id, data, date, ip, block, top from topic where title = ? and sub = ? and top = 'O' order by id + 0 asc", [name, sub])
    else:
        sqlQuery("select id, data, date, ip, block, top from topic where title = ? and sub = ? order by id + 0 asc", [name, sub])

    data = sqlQuery("fetchall")
    if data:
        json_data = {}
        admin = admin_check(3)
                    
        for i in data:
            if i[4] != 'O' or (i[4] == 'O' and admin == 1):
                t_data_f = i[1]
                b_color = ''
            else:
                sqlQuery("select who from re_admin where what = ? order by time desc limit 1", ['blind (' + name + ' - ' + sub + '#' + str(i[0]) + ')'])
                who_blind = sqlQuery("fetchall")
                if who_blind:
                    t_data_f = '[[user:' + who_blind[0][0] + ']] block'
                    b_color = 'toron_color_grey'
                else:
                    t_data_f = 'block'
                    b_color = 'toron_color_grey'

            if flask.request.args.get('render', None):
                if i[0] == '1':
                    s_user = i[3]
                else:
                    if flask.request.args.get('num', None):
                        sqlQuery("select ip from topic where title = ? and sub = ? order by id + 0 asc limit 1", [name, sub])
                        g_data = sqlQuery("fetchall")
                        if g_data:
                            s_user = g_data[0][0]
                        else:
                            s_user = ''
                    
                if flask.request.args.get('top', None):
                    t_color = 'toron_color_red'
                elif i[3] == s_user:
                    t_color = 'toron_color_green'
                elif i[5] == '1':
                    t_color = 'toron_color_blue'
                else:
                    t_color = 'toron_color'
                    
                ip = ip_pas(i[3])
                
                sqlQuery('select acl from user where id = ?', [i[3]])
                u_acl = sqlQuery("fetchall")
                if u_acl and u_acl[0][0] != 'user':
                    ip += ' <a href="javascript:void(0);" title="' + load_lang('admin') + '">★</a>'

                if admin == 1 or b_color != 'toron_color_grey':
                    ip += ' <a href="/topic/' + url_pas(name) + '/sub/' + url_pas(sub) + '/admin/' + i[0] + '">(' + load_lang('discussion_tool') + ')</a>'

                sqlQuery("select end from ban where block = ?", [i[3]])
                if sqlQuery("fetchall"):
                    ip += ' <a href="javascript:void(0);" title="' + load_lang('blocked') + '">†</a>'
                    
                if t_data_f == '':
                    t_data_f = '[br]'
            
                all_data = '''
                    <table id="toron">
                        <tbody>
                            <tr>
                                <td id="''' + t_color + '''">
                                    <a href="javascript:void(0);" id="''' + i[0] + '">#' + i[0] + '</a> ' + ip + ' <span style="float: right;">' + i[2] + '''</span>
                                </td>
                            </tr>
                            <tr>
                                <td id="''' + b_color + '">' + render_set(data = t_data_f) + '''</td>
                            </tr>
                        </tbody>
                    </table>
                    <hr class="main_hr">
                '''
                
                json_data[i[0]] = {
                    "data" : all_data
                }
            else:
                json_data[i[0]] = {
                    "data" : t_data_f,
                    "date" : i[2],
                    "ip" : i[3],
                    "block" : i[4],
                }

        return flask.jsonify(json_data)
    else:
        return flask.jsonify({})