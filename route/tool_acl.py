from .tool.func import *

def tool_acl_2(conn):
    curs = conn.cursor()

    if admin_check() != 1:
        return re_error('/error/3')
    
    acl_list = [
        'all',
        'search',
        'inter_wiki',
        'list_acl',
        'admin_log',
        'admin_list',
        'block_log',
        'give_log',
        'not_close_topic',
        'old_page',
        'please',
        'title_index',
        'topic_record',
        'user_log',
        'recent_changes',
        'recent_discuss'
    ]
    acl_desc = [
        load_lang('default'),
        load_lang('search'),
        load_lang('filter'),
        load_lang('acl_document_list'),
        load_lang('authority_use_list'),
        load_lang('admin_list'),
        load_lang('recent_ban'),
        load_lang('admin_group_list'),
        load_lang('open_discussion_list'),
        load_lang('old_page'),
        load_lang('need_document'),
        load_lang('all_document_list'),
        load_lang('discussion_record'),
        load_lang('member_list'),
        load_lang('recent_change'),
        load_lang('recent_discussion')
    ]
    choice_list = [
        '',
        'user',
        'admin',
        '50_edit',
        'email',
        'owner'
    ]
    choice_desc = [
        load_lang('default'),
        load_lang('member_acl'),
        load_lang('admin_acl'),
        load_lang('50_edit_acl'),
        load_lang('email_acl'),
        load_lang('owner_acl')
    ]

    if flask.request.method == 'POST':
        for i in acl_list:
            new_acl = flask.request.form.get(i, '')
            curs.execute(db_change('select acl from tool_acl where tool = ?'), [i])
            old_acl = curs.fetchall()
            if old_acl and old_acl[0]:
                curs.execute(db_change('update tool_acl set acl = ? where tool = ?'), [new_acl, i])
            else:
                curs.execute(db_change('insert into tool_acl (acl, tool) values (?, ?)'), [new_acl, i])
            conn.commit()
        return redirect('/tool_acl')

    select_options = ''
    body = '<form action="" accept-charset="utf-8" method="post">'
    for i in range(len(acl_list)):    
        acl_now = ''
        curs.execute(db_change('select acl from tool_acl where tool = ?'), [acl_list[i]])
        acl_data = curs.fetchall()
        if acl_data and acl_data[0][0]:
            acl_now = acl_data[0][0]
        body += '''
                <span>''' + acl_desc[i] + '''</span>
                <hr class=\"main_hr\">
                <select name="''' + acl_list[i] + '''">'''         
        for i in range(len(choice_list)):
            if acl_now == choice_list[i]:
                body += '<option value="' + choice_list[i] + '" selected>' + choice_desc[i] + '</option>'
            else:
                body += '<option value="' + choice_list[i] + '">' + choice_desc[i] + '</option>'
        body += '''
                </select>
                <hr>
                '''
    body += '<button type="submit">' + load_lang('save') + '</button></form>'

    return easy_minify(flask.render_template(skin_check(),
        imp = [load_lang('tool_acl_setting'), wiki_set(), custom(), other2([0, 0])],
        data = body,
        menu = [['tool_acl_setting', load_lang('return')]]
    ))