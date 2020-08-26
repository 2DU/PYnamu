from .tool.func import *

def main_views_2(conn, name):
    curs = conn.cursor()
    
    if re.search(r'[.][.]\/', name):
        return re_error('/error/3')

    if re.search(r'\/', name):
        m = re.search(r'^(.*)\/(.*)$', name)
        if m:
            n = m.groups()
            plus = '/' + n[0]
            rename = n[1]
        else:
            plus = ''
            rename = name
    else:
        plus = ''
        rename = name

    mime_type = re.search(r'\.([^\.]+)$', rename).group(1)
    if mime_type:
        if mime_type in ['.jpeg', '.jpg', '.gif', '.png', '.webp', '.JPEG', '.JPG', '.GIF', '.PNG', '.WEBP']:
            mime_type = 'image/' + mime_type
        else:
            mime_type = 'text/' + mime_type
    else:
        mime_type = 'text/plain'

    return flask.send_from_directory('./views' + plus, rename, mimetype = mime_type)
