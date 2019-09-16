from .tool.func import *

def inter_wiki_2(tools):
    
    
    div = ''
    admin = admin_check()

    if tools == 'inter_wiki':
        del_link = 'del_inter_wiki'
        plus_link = 'plus_inter_wiki'
        title = load_lang('interwiki_list')
        div = ''

        sqlQuery('select title, link from inter')
    elif tools == 'email_filter':
        del_link = 'del_email_filter'
        plus_link = 'plus_email_filter'
        title = load_lang('email_filter_list')
        div =   '''
                <ul>
                    <li>gmail.com</li>
                    <li>naver.com</li>
                    <li>daum.net</li>
                    <li>hanmail.net</li>
                    <li>hanmail2.net</li>
                </ul>
                '''

        sqlQuery("select html from html_filter where kind = 'email'")
    elif tools == 'name_filter':
        del_link = 'del_name_filter'
        plus_link = 'plus_name_filter'
        title = load_lang('id_filter_list')
        div = ''

        sqlQuery("select html from html_filter where kind = 'name'")
    elif tools == 'edit_filter':
        del_link = 'del_edit_filter'
        plus_link = 'manager/9'
        title = load_lang('edit_filter_list')
        div = ''

        sqlQuery("select name from filter")
    elif tools == 'file_filter':
        del_link = 'del_file_filter'
        plus_link = 'plus_file_filter'
        title = load_lang('file_filter_list')
        div = ''

        sqlQuery("select html from html_filter where kind = 'file'")
    elif tools == 'file_filter':
        del_link = 'del_file_filter'
        plus_link = 'plus_file_filter'
        title = load_lang('file_filter_list')
        div = ''

        sqlQuery("select html from html_filter where kind = 'file'")  
    elif tools == 'image_license':
        del_link = 'del_image_license'
        plus_link = 'plus_image_license'
        title = load_lang('image_license_list')
        div = ''

        sqlQuery("select html from html_filter where kind = 'image_license'")  
    else:
        del_link = 'del_edit_top'
        plus_link = 'plus_edit_top'
        title = load_lang('edit_tool_list')
        div = ''

        sqlQuery("select html, plus from html_filter where kind = 'edit_top'")

    db_data = sqlQuery("fetchall")
    if db_data:
        div += '<ul>'

        for data in db_data:
            if tools == 'inter_wiki':
                div += '<li>' + data[0] + ' : <a id="out_link" href="' + data[1] + '">' + data[1] + '</a>'
            elif tools == 'edit_filter':
                div += '<li><a href="/plus_edit_filter/' + url_pas(data[0]) + '">' + data[0] + '</a>'
            else:
                div += '<li>' + data[0]

                if tools == 'edit_top':
                    div += ' : ' + data[1]

            if admin == 1:
                div += ' <a href="/' + del_link + '/' + url_pas(data[0]) + '">(' + load_lang('delete') + ')</a>'

            div += '</li>'

        div += '</ul>'

        if admin == 1:
            div += '<hr class=\"main_hr\"><a href="/' + plus_link + '">(' + load_lang('add') + ')</a>'
    else:
        if admin == 1:
            div += '<a href="/' + plus_link + '">(' + load_lang('add') + ')</a>'

    return easy_minify(flask.render_template(skin_check(), 
        imp = [title, wiki_set(), custom(), other2([0, 0])],
        data = div,
        menu = [['other', load_lang('return')]]
    ))