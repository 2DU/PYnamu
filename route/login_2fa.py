from .tool.func import *
import hmac
import hashlib
import os
import time
import math
import base64
import urllib.parse
import random

import segno

def login_2fa_2(conn):
    curs = conn.cursor()

    if not (flask.session and 'b_id' in flask.session):
        return redirect('/user')

    ip = ip_check()
    if ip_or_user(ip) == 0:
        return redirect('/user')

    if ban_check(None, 'login') == 1:
        return re_error('/ban')

    if flask.request.method == 'POST':
        if captcha_post(flask.request.form.get('g-recaptcha-response', flask.request.form.get('g-recaptcha', ''))) == 1:
            return re_error('/error/13')
        else:
            captcha_post('', 0)

        user_agent = flask.request.headers.get('User-Agent', '')
        user_id = flask.session['b_id']

        curs.execute(db_change('select data from user_set where name = "2fa_pw" and id = ?'), [user_id])
        user_1 = curs.fetchall()
        if user_1:
            curs.execute(db_change('select data from user_set where name = "2fa_pw_encode" and id = ?'), [user_id])
            user_1 = user_1[0][0]
            user_2 = curs.fetchall()[0][0]
            pw_check_d = 0
            if (user_2 == "totp"):
                code = dev_2fa_totp(user_1)
                time.sleep(random.random() * 0.5)
                if (code != flask.request.form.get('pw', '')):
                    pw_check_d = 1
            else:
                pw_check_d = pw_check(
                    flask.request.form.get('pw', ''),
                    user_1,
                    user_2,
                    user_id
                )
            if pw_check_d != 1:
                return re_error('/error/10')

        flask.session['id'] = user_id

        ua_plus(user_id, ip, user_agent, get_time())
        conn.commit()

        flask.session.pop('b_id', None)

        return redirect('/user')
    else:
        return easy_minify(flask.render_template(skin_check(),
            imp = [load_lang('login'), wiki_set(), custom(), other2([0, 0])],
            data =  '''
                    <form method="post">
                        <input placeholder="''' + load_lang('2fa_password') + '''" name="pw" type="password">
                        <hr class=\"main_hr\">
                        ''' + captcha_get() + '''
                        <button type="submit">''' + load_lang('login') + '''</button>
                        ''' + http_warring() + '''
                    </form>
                    ''',
            menu = [['user', load_lang('return')]]
        ))
