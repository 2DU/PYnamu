from .tool.func import *

def login_logout_2(conn):
    curs = conn.cursor()
    
    resp = flask.make_response(redirect('/user'))

    flask.session.pop('state', None)
    flask.session.pop('id', None)

    resp.set_cookie('autologin_token', '', expires=0)
    resp.set_cookie('autologin_username', '', expires=0)

    return resp
