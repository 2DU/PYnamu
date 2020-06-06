from .tool.func import *

def login_2(conn):
    curs = conn.cursor()

    ip = ip_check()
    if ip_or_user(ip) == 0:
        return redirect('/user')

    if ban_check(tool = 'login') == 1:
        return re_error('/ban')

    if flask.request.method == 'POST':
        if captcha_post(flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
            return re_error('/error/13')
        else:
            captcha_post('', 0)

        agent = flask.request.headers.get('User-Agent')

        curs.execute(db_change("select pw, encode from user where id = ?"), [flask.request.form.get('id', None)])
        user = curs.fetchall()
        if not user:
            return re_error('/error/2')

        pw_check_d = pw_check(
            flask.request.form.get('pw', ''),
            user[0][0],
            user[0][1],
            flask.request.form.get('id', None)
        )
        if pw_check_d != 1:
            return re_error('/error/10')

        flask.session['state'] = 1
        flask.session['id'] = flask.request.form.get('id', None)

        curs.execute(db_change("select css from custom where user = ?"), [flask.request.form.get('id', None)])
        css_data = curs.fetchall()
        if css_data:
            flask.session['head'] = css_data[0][0]
        else:
            flask.session['head'] = ''

        curs.execute(db_change("insert into ua_d (name, ip, ua, today, sub) values (?, ?, ?, ?, '')"), [flask.request.form.get('id', None), ip_check(1), agent, get_time()])

        res = flask.make_response(flask.redirect('/user'))
        
        #먼저 기존 쿠키를 터뜨리고 생성
        res.set_cookie('autologin_username', '', expires=0)
        res.set_cookie('autologin_token', '', expires=0)
        
        if flask.request.form.get('autologin', 0) != 0:
            expdt = datetime.datetime.now()
            expdt = expdt + datetime.timedelta(days=180)

            rndtkn = ''.join(random.choice("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ") for i in range(64))

            #create table token ( username text default '', key text default '' )
            #일부러 update로 안 함
            curs.execute(db_change("delete from token where username = ?"), [flask.request.form.get('id', '')])
            curs.execute(db_change("insert into token (username, key) values (?, ?)"), [flask.request.form.get('id', ''), rndtkn])

            res.set_cookie("autologin_token", value=sha224(pw_encode(flask.request.form.get('pw', '')) + sha224(rndtkn)), expires = expdt, secure = True, httponly = True)
            res.set_cookie("autologin_username", value=flask.request.form.get('id', ''), expires = expdt, secure = True, httponly = True)
            
        conn.commit()

        return res
    else:
        oauth_check = 0
        oauth_content = '<hr class=\"main_hr\"><div class="oauth-wrapper"><ul class="oauth-list">'
        oauth_supported = load_oauth('_README')['support']
        for i in range(len(oauth_supported)):
            oauth_data = load_oauth(oauth_supported[i])
            if oauth_data['client_id'] != '' and oauth_data['client_secret'] != '':
                oauth_content += '''
                    <li>
                        <a href="/oauth/{}/init">
                            <div class="oauth-btn oauth-btn-{}">
                                <div class="oauth-btn-logo oauth-btn-{}"></div>
                                {}
                            </div>
                        </a>
                    </li>
                '''.format(
                    oauth_supported[i],
                    oauth_supported[i],
                    oauth_supported[i],
                    load_lang('oauth_signin_' + oauth_supported[i])
                )

                oauth_check = 1

        oauth_content += '</ul></div>'

        if oauth_check == 0:
            oauth_content = ''

        http_warring = '<hr class=\"main_hr\"><span>' + load_lang('http_warring') + '</span>'

        return easy_minify(flask.render_template(skin_check(),
            imp = [load_lang('login'), wiki_set(), custom(), other2([0, 0])],
            data =  '''
                    <form method="post">
                        <input placeholder="''' + load_lang('id') + '''" name="id" type="text">
                        <hr class=\"main_hr\">
                        <input placeholder="''' + load_lang('password') + '''" name="pw" type="password">
                        <hr class=\"main_hr\">
                        <label><input type=checkbox name=autologin> ''' + load_lang('autologin') + '''</label>
                        <hr class=\"main_hr\">
                        ''' + captcha_get() + '''
                        <button type="submit">''' + load_lang('login') + '''</button>
                        ''' + oauth_content + '''
                        ''' + http_warring + '''
                    </form>
                    ''',
            menu = [['user', load_lang('return')]]
        ))
