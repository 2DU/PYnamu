from .tool.func import *

def edit_delete_2(name, app_var):
    

    ip = ip_check()
    if acl_check(name) == 1:
        return re_error('/ban')
    
    if flask.request.method == 'POST':
        if captcha_post(flask.request.form.get('g-recaptcha-response', '')) == 1:
            return re_error('/error/13')
        else:
            captcha_post('', 0)

        sqlQuery("select data from data where title = ?", [name])
        data = sqlQuery("fetchall")
        if data:
            today = get_time()
            leng = '-' + str(len(data[0][0]))
            
            history_plus(
                name, 
                '', 
                today, 
                ip, 
                flask.request.form.get('send', ''), 
                leng,
                'delete'
            )
            
            sqlQuery("select title, link from back where title = ? and not type = 'cat' and not type = 'no'", [name])
            for data in sqlQuery("fetchall"):
                sqlQuery("insert into back (title, link, type) values (?, ?, 'no')", [data[0], data[1]])
            
            sqlQuery("delete from back where link = ?", [name])
            sqlQuery("delete from data where title = ?", [name])
            sqlQuery("commit")

        file_check = re.search('^file:(.+)\.(.+)$', name)
        if file_check:
            file_check = file_check.groups()
            os.remove(os.path.join(
                app_var['path_data_image'],
                hashlib.sha224(bytes(file_check[0], 'utf-8')).hexdigest() + '.' + file_check[1]
            ))
            
        return redirect('/w/' + url_pas(name))
    else:
        sqlQuery("select title from data where title = ?", [name])
        if not sqlQuery("fetchall"):
            return redirect('/w/' + url_pas(name))

        return easy_minify(flask.render_template(skin_check(), 
            imp = [name, wiki_set(), custom(), other2([' (' + load_lang('delete') + ')', 0])],
            data =  '''
                    <form method="post">
                        ''' + ip_warring() + '''
                        <input placeholder="''' + load_lang('why') + '''" name="send" type="text">
                        <hr class=\"main_hr\">
                        ''' + captcha_get() + '''
                        <button type="submit">''' + load_lang('delete') + '''</button>
                    </form>
                    ''',
            menu = [['w/' + url_pas(name), load_lang('return')]]
        ))     