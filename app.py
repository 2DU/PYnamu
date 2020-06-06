import os
import re

for i_data in os.listdir("route"):
    f_src = re.search(r"(.+)\.py$", i_data)
    if f_src:
        f_src = f_src.group(1)

        exec("from route." + f_src + " import *")

# DB
version_list = json.loads(open('version.json', encoding='utf8').read())
app_var = json.loads(open('data/app_var.json', encoding='utf8').read())

print('Version : ' + version_list['master']['r_ver'])
print('DB set version : ' + version_list['master']['c_ver'])
print('Skin set version : ' + version_list['master']['s_ver'])
print('----')

while 1:
    try:
        set_data = json.loads(open('data/set.json', encoding='utf8').read())
        if not 'db_type' in set_data:
            try:
                os.remove('data/set.json')
            except:
                print('Please delete set.json')
                print('----')
                raise
        else:
            print('DB name : ' + set_data['db'])
            print('DB type : ' + set_data['db_type'])

            break
    except:
        if os.getenv('NAMU_DB') != None or os.getenv('NAMU_DB_TYPE') != None:
            set_data = {
                "db" : os.getenv('NAMU_DB') if os.getenv('NAMU_DB') else 'data',
                "db_type" : os.getenv('NAMU_DB_TYPE') if os.getenv('NAMU_DB_TYPE') else 'sqlite'
            }

            print('DB name : ' + set_data['db'])
            print('DB type : ' + set_data['db_type'])

            break
        else:
            new_json = ['', '']
            normal_db_type = ['sqlite', 'mysql']

            print('DB type (sqlite) [sqlite, mysql] : ', end = '')
            new_json[0] = str(input())
            if new_json[0] == '' or not new_json[0] in normal_db_type:
                new_json[0] = 'sqlite'

            all_src = []
            for i_data in os.listdir("."):
                f_src = re.search(r"(.+)\.db$", i_data)
                if f_src:
                    all_src += [f_src.group(1)]

            if all_src != [] and new_json[0] != 'mysql':
                print('DB name (data) [' + ', '.join(all_src) + '] : ', end = '')
            else:
                print('DB name (data) : ', end = '')

            new_json[1] = str(input())
            if new_json[1] == '':
                new_json[1] = 'data'

            with open('data/set.json', 'w', encoding='utf8') as f:
                f.write('{ "db" : "' + new_json[1] + '", "db_type" : "' + new_json[0] + '" }')

            set_data = json.loads(open('data/set.json', encoding='utf8').read())

            break

db_data_get(set_data['db_type'])

if set_data['db_type'] == 'mysql':
    try:
        set_data_mysql = json.loads(open('data/mysql.json', encoding='utf8').read())
    except:
        new_json = ['', '', '']

        while 1:
            print('DB user ID : ', end = '')
            new_json[0] = str(input())
            if new_json[0] != '':
                break

        while 1:
            print('DB password : ', end = '')
            new_json[1] = str(input())
            if new_json[1] != '':
                break
                
        print('DB host (localhost) : ', end = '')
        new_json[2] = str(input())
        if new_json[2] == '':
            new_json[2] == 'localhost'

        with open('data/mysql.json', 'w', encoding='utf8') as f:
            f.write('{ "user" : "' + new_json[0] + '", "password" : "' + new_json[1] + '", "host" : "' + new_json[2] + '" }')

        set_data_mysql = json.loads(open('data/mysql.json', encoding='utf8').read())

    conn = pymysql.connect(
        host = set_data_mysql['host'] if 'host' in set_data_mysql else 'localhost',
        user = set_data_mysql['user'],
        password = set_data_mysql['password'],
        charset = 'utf8mb4'
    )
    curs = conn.cursor()

    try:
        curs.execute(db_change('create database ? default character set utf8mb4;')%pymysql.escape_string(set_data['db']))
    except:
        pass

    curs.execute(db_change('use ?')%pymysql.escape_string(set_data['db']))
else:
    conn = sqlite3.connect(set_data['db'] + '.db', check_same_thread = False)
    curs = conn.cursor()

load_conn(conn)

create_data = {}
create_data['all_data'] = [
    'data',
    'cache_data',
    'history',
    'rd',
    'user',
    'user_set',
    'topic',
    'rb',
    'back',
    'custom',
    'other',
    'alist',
    're_admin',
    'alarm',
    'ua_d',
    'filter',
    'scan',
    'acl',
    'inter',
    'html_filter',
    'oauth_conn',
    'user_application',
    'token'
]
for i in create_data['all_data']:
    try:
        curs.execute(db_change('select test from ' + i + ' limit 1'))
    except:
        try:
            curs.execute(db_change('create table ' + i + '(test longtext)'))
        except:
            curs.execute(db_change("alter table " + i + " add test longtext default ''"))

setup_tool = 0
try:
    curs.execute(db_change('select data from other where name = "ver"'))
    ver_set_data = curs.fetchall()
    if not ver_set_data:
        setup_tool = 2
    else:
        if int(version_list['master']['c_ver']) > int(ver_set_data[0][0]):
            setup_tool = 1
except:
    setup_tool = 2

if setup_tool != 0:
    create_data['data'] = ['title', 'data']
    create_data['cache_data'] = ['title', 'data', 'id']
    create_data['history'] = ['id', 'title', 'data', 'date', 'ip', 'send', 'leng', 'hide', 'type']
    create_data['rd'] = ['title', 'sub', 'code', 'date', 'band', 'stop', 'agree', 'acl']
    create_data['user'] = ['id', 'pw', 'acl', 'date', 'encode']
    create_data['user_set'] = ['name', 'id', 'data']
    create_data['user_application'] = ['id', 'pw', 'date', 'encode', 'question', 'answer', 'ip', 'ua', 'token', 'email']
    create_data['topic'] = ['id', 'data', 'date', 'ip', 'block', 'top', 'code']
    create_data['rb'] = ['block', 'end', 'today', 'blocker', 'why', 'band', 'login', 'ongoing']
    create_data['back'] = ['title', 'link', 'type']
    create_data['custom'] = ['user', 'css']
    create_data['other'] = ['name', 'data', 'coverage']
    create_data['alist'] = ['name', 'acl']
    create_data['re_admin'] = ['who', 'what', 'time']
    create_data['alarm'] = ['name', 'data', 'date']
    create_data['ua_d'] = ['name', 'ip', 'ua', 'today', 'sub']
    create_data['filter'] = ['name', 'regex', 'sub']
    create_data['scan'] = ['user', 'title', 'type']
    create_data['acl'] = ['title', 'decu', 'dis', 'view', 'why']
    create_data['inter'] = ['title', 'link', 'icon']
    create_data['html_filter'] = ['html', 'kind', 'plus']
    create_data['oauth_conn'] = ['provider', 'wiki_id', 'sns_id', 'name', 'picture']
    create_data['token'] = ['username', 'key']

    for create_table in create_data['all_data']:
        for create in create_data[create_table]:
            try:
                curs.execute(db_change('select ' + create + ' from ' + create_table + ' limit 1'))
            except:
                curs.execute(db_change("alter table " + create_table + " add " + create + " longtext default ''"))

    if setup_tool == 1:
        update(int(ver_set_data[0][0]), set_data)
    else:
        set_init()

curs.execute(db_change('delete from other where name = "ver"'))
curs.execute(db_change('insert into other (name, data) values ("ver", ?)'), [version_list['master']['c_ver']])
conn.commit()

# Init
logging.basicConfig(level = logging.ERROR)

app = flask.Flask(__name__, template_folder = './')
app.config['JSON_AS_ASCII'] = False

flask_reggie.Reggie(app)

class EverythingConverter(werkzeug.routing.PathConverter):
    regex = '.*?'

app.jinja_env.filters['md5_replace'] = md5_replace
app.jinja_env.filters['load_lang'] = load_lang
app.jinja_env.filters['cut_100'] = cut_100

app.url_map.converters['everything'] = EverythingConverter

curs.execute(db_change('select name from alist where acl = "owner"'))
if not curs.fetchall():
    curs.execute(db_change('insert into alist (name, acl) values ("owner", "owner")'))

if not os.path.exists(app_var['path_data_image']):
    os.makedirs(app_var['path_data_image'])

if not os.path.exists('views'):
    os.makedirs('views')

print('----')
import route.tool.init as server_init

dislay_set_key = ['Host', 'Port', 'Language', 'Markup', 'Encryption method']
server_set_key = ['host', 'port', 'language', 'markup', 'encode']
server_set = {}

for i in range(len(server_set_key)):
    curs.execute(db_change('select data from other where name = ?'), [server_set_key[i]])
    server_set_val = curs.fetchall()
    if not server_set_val:
        server_set_val = server_init.init(server_set_key[i])

        curs.execute(db_change('insert into other (name, data) values (?, ?)'), [server_set_key[i], server_set_val])
        conn.commit()
    else:
        server_set_val = server_set_val[0][0]

    print(dislay_set_key[i] + ' : ' + server_set_val)

    server_set[server_set_key[i]] = server_set_val

curs.execute(db_change('select data from other where name = "key"'))
rep_data = curs.fetchall()
if not rep_data:
    rep_key = ''.join(random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(16))
    if rep_key:
        curs.execute(db_change('insert into other (name, data) values ("key", ?)'), [rep_key])
else:
    rep_key = rep_data[0][0]

if set_data['db_type'] == 'sqlite':
    def back_up():
        print('----')

        curs.execute(db_change('select data from other where name = "backup_where"'))
        back_up_where = curs.fetchall()
        if back_up_where and back_up_where[0][0] != '':
            back_up_where = back_up_where[0][0]
        else:
            back_up_where = 'back_' + set_data['db'] + '.db'
        
        try:
            shutil.copyfile(
                set_data['db'] + '.db', 
                back_up_where
            )

            print('Back up : OK')
        except:
            print('Back up : Error')

        threading.Timer(60 * 60 * back_time, back_up).start()

    try:
        curs.execute(db_change('select data from other where name = "back_up"'))
        back_up_time = curs.fetchall()

        back_time = int(back_up_time[0][0])
    except:
        back_time = 0

    print('----')
    if back_time != 0:
        print('Back up state : ' + str(back_time) + ' hours')

        back_up()
    else:
        print('Back up state : Turn off')

def mysql_dont_off():
    try:
        urllib.request.urlopen('http://localhost:' + server_set['port'] + '/')
    except:
        pass

    threading.Timer(60 * 60 * 6, mysql_dont_off).start()

mysql_dont_off()

curs.execute(db_change('select data from other where name = "count_all_title"'))
if not curs.fetchall():
    curs.execute(db_change('insert into other (name, data) values ("count_all_title", "0")'))

conn.commit()

print('Now running... http://localhost:' + server_set['port'])

if os.path.exists('custom.py'):
    from custom import custom_run

    custom_run(conn, app)

# Func
@app.route('/del_alarm')
def alarm_del():
    return alarm_del_2(conn)

@app.route('/alarm')
def alarm():
    return alarm_2(conn)

@app.route('/<regex("inter_wiki|edit_top|image_license|(?:edit|email|file|name|extension)_filter"):tools>')
def inter_wiki(tools = None):
    return inter_wiki_2(conn, tools)

@app.route('/<regex("del_(?:inter_wiki|edit_top|image_license|(?:edit|email|file|name|extension)_filter)"):tools>/<name>')
def inter_wiki_del(tools = None, name = None):
    return inter_wiki_del_2(conn, tools, name)

@app.route('/<regex("plus_(?:inter_wiki|edit_top|image_license|(?:edit|email|file|name|extension)_filter)"):tools>', methods=['POST', 'GET'])
@app.route('/<regex("plus_(?:inter_wiki|edit_top|image_license|(?:edit|email|file|name|extension)_filter)"):tools>/<name>', methods=['POST', 'GET'])
def inter_wiki_plus(tools = None, name = None):
    return inter_wiki_plus_2(conn, tools, name)

@app.route('/setting')
@app.route('/setting/<int:num>', methods=['POST', 'GET'])
def setting(num = 0):
    return setting_2(conn, num, set_data['db_type'])

@app.route('/not_close_topic')
def list_not_close_topic():
    return list_not_close_topic_2(conn)

@app.route('/old_page')
def list_old_page():
    return list_old_page_2(conn)

@app.route('/acl_list')
def list_acl():
    return list_acl_2(conn)

@app.route('/image_file_list')
def list_image_file():
    return list_image_file_2(conn)

@app.route('/admin_plus/<name>', methods=['POST', 'GET'])
def give_admin_groups(name = None):
    return give_admin_groups_2(conn, name)

@app.route('/delete_admin_group/<name>', methods=['POST', 'GET'])
def delete_admin_group(name = None):
    return delete_admin_group_2(conn, name)

@app.route('/admin_list')
def list_admin():
    return list_admin_2(conn)

@app.route('/hidden/<everything:name>')
def give_history_hidden(name = None):
    return give_history_hidden_2(conn, name)

@app.route('/add_history/<everything:name>', methods=['POST', 'GET'])
def give_history_add(name = None):
    return give_history_add_2(conn, name)

@app.route('/user_log')
def list_user():
    return list_user_2(conn)

@app.route('/admin_log', methods=['POST', 'GET'])
def list_admin_use():
    return list_admin_use_2(conn)

@app.route('/give_log')
def list_give():
    return list_give_2(conn)

@app.route('/restart', methods=['POST', 'GET'])
def server_restart():
    return server_restart_2(conn)

@app.route('/update', methods=['GET', 'POST'])
def server_now_update():
    return server_now_update_2(conn, version_list['master']['r_ver'])

@app.route('/xref/<everything:name>')
def view_xref(name = None):
    return view_xref_2(conn, name)

@app.route('/please')
def list_please():
    return list_please_2(conn)

@app.route('/recent_discuss')
def recent_discuss():
    return recent_discuss_2(conn)

@app.route('/block_log')
@app.route('/<regex("block_user|block_admin"):tool>/<name>')
def list_block(name = None, tool = None):
    return list_block_2(conn, name, tool)

@app.route('/search', methods=['POST'])
def search():
    return search_2(conn)

@app.route('/goto', methods=['POST'])
@app.route('/goto/<everything:name>', methods=['POST'])
def search_goto(name = 'test'):
    return search_goto_2(conn, name)

@app.route('/search/<everything:name>')
def search_deep(name = 'test'):
    return search_deep_2(conn, name)

@app.route('/raw/<everything:name>')
@app.route('/thread/<int:topic_num>/raw/<int:num>')
def view_raw(name = None, topic_num = None, num = None):
    return view_raw_2(conn, name, topic_num, num)

@app.route('/revert/<everything:name>', methods=['POST', 'GET'])
def edit_revert(name = None):
    return edit_revert_2(conn, name)

@app.route('/edit/<everything:name>', methods=['POST', 'GET'])
def edit(name = 'Test'):
    return edit_2(conn, name)

@app.route('/backlink_reset/<everything:name>')
def edit_backlink_reset(name = 'Test'):
    return edit_backlink_reset_2(conn, name)

@app.route('/delete/<everything:name>', methods=['POST', 'GET'])
def edit_delete(name = None):
    return edit_delete_2(conn, name, app_var)

@app.route('/many_delete', methods=['POST', 'GET'])
def edit_many_delete(name = None):
    return edit_many_delete_2(conn, app_var)

@app.route('/move/<everything:name>', methods=['POST', 'GET'])
def edit_move(name = None):
    return edit_move_2(conn, name)

@app.route('/other')
def main_other():
    return main_other_2(conn)

@app.route('/manager', methods=['POST', 'GET'])
@app.route('/manager/<int:num>', methods=['POST', 'GET'])
def main_manager(num = 1):
    return main_manager_2(conn, num, version_list['master']['r_ver'])

@app.route('/title_index')
def list_title_index():
    return list_title_index_2(conn)

@app.route('/thread/<int:topic_num>/b/<int:num>')
def topic_block(topic_num = 1, num = 1):
    return topic_block_2(conn, topic_num, num)

@app.route('/thread/<int:topic_num>/notice/<int:num>')
def topic_top(topic_num = 1, num = 1):
    return topic_top_2(conn, topic_num, num)

@app.route('/thread/<int:topic_num>/setting', methods=['POST', 'GET'])
def topic_stop(topic_num = 1):
    return topic_stop_2(conn, topic_num)

@app.route('/thread/<int:topic_num>/acl', methods=['POST', 'GET'])
def topic_acl(topic_num = 1):
    return topic_acl_2(conn, topic_num)

@app.route('/thread/<int:topic_num>/delete', methods=['POST', 'GET'])
def topic_delete(topic_num = 1):
    return topic_delete_2(conn, topic_num)

@app.route('/thread/<int:topic_num>/tool')
def topic_tool(topic_num = 1):
    return topic_tool_2(conn, topic_num)

@app.route('/thread/<int:topic_num>/change', methods=['POST', 'GET'])
def topic_change(topic_num = 1):
    return topic_change_2(conn, topic_num)

@app.route('/thread/<int:topic_num>/admin/<int:num>')
def topic_admin(topic_num = 1, num = 1):
    return topic_admin_2(conn, topic_num, num)

@app.route('/thread/<int:topic_num>', methods=['POST', 'GET'])
def topic(topic_num = 1):
    return topic_2(conn, topic_num)

@app.route('/topic/<everything:name>', methods=['POST', 'GET'])
def topic_close_list(name = 'test'):
    return topic_close_list_2(conn, name)

@app.route('/tool/<name>')
def user_tool(name = None):
    return user_tool_2(conn, name)

@app.route('/login', methods=['POST', 'GET'])
def login():
    return login_2(conn)

@app.route('/oauth/<regex("discord|naver|facebook|kakao"):platform>/<regex("init|callback"):func>', methods=['GET', 'POST'])
def login_oauth(platform = None, func = None):
    return login_oauth_2(conn, platform, func)

@app.route('/change', methods=['POST', 'GET'])
def user_setting():
    return user_setting_2(conn, server_init)

@app.route('/pw_change', methods=['POST', 'GET'])
def login_pw_change():
    return login_pw_change_2(conn)

@app.route('/check/<name>')
def give_user_check(name = None):
    return give_user_check_2(conn, name)

@app.route('/register', methods=['POST', 'GET'])
def login_register():
    return login_register_2(conn)

@app.route('/<regex("need_email|pass_find|email_change"):tool>', methods=['POST', 'GET'])
def login_need_email(tool = 'pass_find'):
    return login_need_email_2(conn, tool)

@app.route('/<regex("check_key|check_pass_key|email_replace"):tool>', methods=['POST', 'GET'])
def login_check_key(tool = 'check_pass_key'):
    return login_check_key_2(conn, tool)

@app.route('/logout')
def login_logout():
    return login_logout_2(conn)

@app.route('/ban', methods=['POST', 'GET'])
@app.route('/ban/<name>', methods=['POST', 'GET'])
def give_user_ban(name = None):
    return give_user_ban_2(conn, name)

@app.route('/acl/<everything:name>', methods=['POST', 'GET'])
def give_acl(name = None):
    return give_acl_2(conn, name)

@app.route('/admin/<name>', methods=['POST', 'GET'])
def give_admin(name = None):
    return give_admin_2(conn, name)

@app.route('/diff/<everything:name>')
def view_diff_data(name = None):
    return view_diff_data_2(conn, name)

@app.route('/down/<everything:name>')
def view_down(name = None):
    return view_down_2(conn, name)

@app.route('/w/<everything:name>')
def view_read(name = None):
    return view_read_2(conn, name)

@app.route('/topic_record/<name>')
def list_user_topic(name = 'test'):
    return list_user_topic_2(conn, name)

@app.route('/recent_changes')
@app.route('/<regex("record"):tool>/<name>')
@app.route('/<regex("history"):tool>/<everything:name>', methods=['POST', 'GET'])
def recent_changes(name = None, tool = 'record'):
    return recent_changes_2(conn, name, tool)

@app.route('/history_tool/<everything:name>')
def recent_history_tool(name = None):
    return recent_history_tool_2(conn, name)

@app.route('/history_delete/<everything:name>', methods=['POST', 'GET'])
def recent_history_delete(name = None):
    return recent_history_delete_2(conn, name)

@app.route('/upload', methods=['GET', 'POST'])
def func_upload():
    return func_upload_2(conn)

@app.route('/user')
def user_info():
    return user_info_2(conn)

@app.route('/<regex("watch_list|star_doc"):tool>')
def watch_list(tool = 'star_doc'):
    return watch_list_2(conn, tool)

@app.route('/<regex("watch_list|star_doc"):tool>/<everything:name>')
def watch_list_name(tool = 'star_doc', name = 'Test'):
    return watch_list_name_2(conn, tool, name)

@app.route('/custom_head', methods=['GET', 'POST'])
def user_custom_head_view():
    return user_custom_head_view_2(conn)

@app.route('/count')
@app.route('/count/<name>')
def user_count_edit(name = None):
    return user_count_edit_2(conn, name)

@app.route('/random')
def func_title_random():
    return func_title_random_2(conn)

@app.route('/image/<name>')
def main_image_view(name = None):
    return main_image_view_2(conn, name, app_var)

@app.route('/skin_set')
@app.route('/main_skin_set')
def main_skin_set():
    return main_skin_set_2(conn)

@app.route('/application_submitted')
def application_submitted():
    return application_submitted_2(conn)

@app.route('/applications', methods = ['POST', 'GET'])
def applications():
    return applications_2(conn)

# API
@app.route('/api/w/<everything:name>', methods=['POST', 'GET'])
def api_w(name = ''):
    return api_w_2(conn, name)

@app.route('/api/raw/<everything:name>')
def api_raw(name = ''):
    return api_raw_2(conn, name)

@app.route('/api/version')
def api_version():
    return api_version_2(conn, version_list['master']['r_ver'], version_list['master']['c_ver'])

@app.route('/api/skin_info')
@app.route('/api/skin_info/<name>')
def api_skin_info(name = ''):
    return api_skin_info_2(conn, name)

@app.route('/api/markup')
def api_markup():
    return api_markup_2(conn)

@app.route('/api/user_info/<name>')
def api_user_info(name = ''):
    return api_user_info_2(conn, name)

@app.route('/api/thread/<topic_num>')
def api_topic_sub(name = '', topic_num = 1):
    return api_topic_sub_2(conn, topic_num)

@app.route('/api/search/<name>')
def api_search(name = ''):
    return api_search_2(conn, name)

@app.route('/api/recent_changes')
def api_recent_change():
    return api_recent_change_2(conn)

@app.route('/api/sha224/<everything:name>')
def api_sha224(name = 'test'):
    return api_sha224_2(conn, name)

@app.route('/api/title_index')
def api_title_index():
    return api_title_index_2(conn)

@app.route('/api/image/<name>')
def api_image_view(name = ''):
    return api_image_view_2(conn, name, app_var)

# File
@app.route('/views/<everything:name>')
def main_views(name = None):
    return main_views_2(conn, name)

@app.route('/<data>')
def main_file(data = None):
    return main_file_2(conn, data)

# End
@app.errorhandler(404)
def main_error_404(e):
    return main_error_404_2(conn)

app.secret_key = rep_key
app.wsgi_app = werkzeug.debug.DebuggedApplication(app.wsgi_app, True)
app.debug = True

if __name__ == "__main__":
    if sys.platform == 'win32' and sys.version_info[0:2] >= (3, 8):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    http_server = tornado.httpserver.HTTPServer(tornado.wsgi.WSGIContainer(app))
    http_server.listen(int(server_set['port']), address = server_set['host'])

    tornado.ioloop.IOLoop.instance().start()