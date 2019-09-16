from .tool.func import *

def func_upload_2():
    

    if ban_check() == 1:
        return re_error('/ban')
    
    if flask.request.method == 'POST':
        if captcha_post(flask.request.form.get('g-recaptcha-response', '')) == 1:
            return re_error('/error/13')
        else:
            captcha_post('', 0)

        data = flask.request.files.get('f_data', None)
        if not data:
            return re_error('/error/9')

        if int(wiki_set(3)) * 1024 * 1024 < flask.request.content_length:
            return re_error('/error/17')
        
        value = os.path.splitext(data.filename)[1]
        if not value in ['.jpeg', '.jpg', '.gif', '.png', '.webp', '.JPEG', '.JPG', '.GIF', '.PNG', '.WEBP']:
            return re_error('/error/14')
    
        if flask.request.form.get('f_name', None):
            name = flask.request.form.get('f_name', None) + value
        else:
            name = data.filename
        
        piece = os.path.splitext(name)
        if re.search('[^ㄱ-힣0-9a-zA-Z_\- ]', piece[0]):
            return re_error('/error/22')

        e_data = sha224(piece[0]) + piece[1]

        sqlQuery("select title from data where title = ?", ['file:' + name])
        if sqlQuery("fetchall"):
            return re_error('/error/16')

        sqlQuery("select html from html_filter where kind = 'file'")
        db_data = sqlQuery("fetchall")
        for i in db_data:
            t_re = re.compile(i[0])
            if t_re.search(name):
                return redirect('/file_filter')
            
        ip = ip_check()

        if flask.request.form.get('f_lice_sel', 'direct_input') == 'direct_input':
            if flask.request.form.get('f_lice', None):
                lice = flask.request.form.get('f_lice', None)
            else:
                if custom()[2] == 0:
                    lice = ip
                else:
                    lice = '[[user:' + ip + ']]'

            lice += '[[category:direct_input]]'
        else:
            lice = flask.request.form.get('f_lice_sel', None)
            if flask.request.form.get('f_lice', None):
                lice += ' : '  + flask.request.form.get('f_lice', None)

            lice += '[[category:' + re.sub('\]', '_', flask.request.form.get('f_lice_sel', None)) + ']]'
            
        if os.path.exists(os.path.join(app_var['path_data_image'], e_data)):
            os.remove(os.path.join(app_var['path_data_image'], e_data))
            
            data.save(os.path.join(app_var['path_data_image'], e_data))
        else:
            data.save(os.path.join(app_var['path_data_image'], e_data))

        file_d = '[[file:' + name + ']][br][br]{{{[[file:' + name + ']]}}}[br][br]' + lice
        
        sqlQuery("insert into data (title, data) values (?, ?)", ['file:' + name, file_d])
        sqlQuery("insert into acl (title, decu, dis, why, view) values (?, 'admin', '', '', '')", ['file:' + name])

        render_set(
            title = name,
            data = file_d,
            num = 1
        )

        history_plus(
            'file:' + name,
            file_d,
            get_time(), 
            ip, 
            '(upload)',
            '0'
        )
        
        sqlQuery("commit")
        
        return redirect('/w/file:' + name)      
    else:
        license_list = '''
            <option value="direct_input">''' + load_lang('direct_input') + '''</option>
        '''

        sqlQuery("select html from html_filter where kind = 'image_license'")
        db_data = sqlQuery("fetchall")
        for i in db_data:
            license_list += '''
                <option value="''' + i[0] + '''">''' + i[0] + '''</option>
            '''

        return easy_minify(flask.render_template(skin_check(), 
            imp = [load_lang('upload'), wiki_set(), custom(), other2([0, 0])],
            data =  '''
                <a href="/file_filter">(''' + load_lang('file_filter_list') + ''')</a>
                <hr class=\"main_hr\">
                ''' + load_lang('max_file_size') + ''' : ''' + wiki_set(3) + '''MB
                <hr class=\"main_hr\">
                <form method="post" enctype="multipart/form-data" accept-charset="utf8">
                    <input type="file" name="f_data">
                    <hr class=\"main_hr\">
                    <input placeholder="''' + load_lang('file_name') + '''" name="f_name" type="text">
                    <hr class=\"main_hr\">
                    <select name="f_lice_sel">
                        ''' + license_list + '''
                    </select>
                    <hr class=\"main_hr\">
                    <input placeholder="''' + load_lang('license') + '''" name="f_lice" type="text">
                    <hr class=\"main_hr\">
                    ''' + captcha_get() + '''
                    <button id="save" type="submit">''' + load_lang('save') + '''</button>
                </form>
            ''',
            menu = [['other', load_lang('return')]]
        ))  