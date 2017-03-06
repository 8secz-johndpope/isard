# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3

#!flask/bin/python
# coding=utf-8
import json
import time

from flask import render_template, Response, request, redirect, url_for
from flask_login import login_required

from webapp import app
from ...lib import admin_api

app.adminapi = admin_api.isardAdmin()

import rethinkdb as r
from ...lib.flask_rethink import RethinkDB
db = RethinkDB(app)
db.init_app(app)

from .decorators import isAdmin

'''
LANDING ADMIN PAGE
'''
@app.route('/admin')
@login_required
@isAdmin
def admin():
    return redirect(url_for('admin_hypervisors'))
 
@app.route('/admin/table/<table>/get')
@login_required
def admin_table_get(table):
    result=app.adminapi.get_admin_table(table)
    return json.dumps(result), 200, {'ContentType':'application/json'} 

'''
CONFIG
'''
@app.route('/admin/config', methods=["GET", "POST"])
@login_required
@isAdmin
def admin_config():
    if request.method == 'POST':
        return json.dumps(app.adminapi.get_admin_config(1)), 200, {'ContentType': 'application/json'}
    return render_template('admin/pages/config.html',nav="Config")


@app.route('/admin/disposables', methods=["POST"])
@login_required
@isAdmin
def admin_disposables():
    result=app.adminapi.get_admin_table('disposables')
    return json.dumps(result), 200, {'ContentType':'application/json'} 

@app.route('/admin/config/update', methods=['POST'])
@login_required
@isAdmin
def admin_config_update():
    if request.method == 'POST':
        dict=app.isardapi.f.unflatten_dict(request.form)
        #~ print(dict)
        if 'auth' in dict:
            dict['auth']['local']={'active':False} if 'local' not in dict['auth']  else {'active':True}
            dict['auth']['ldap']['active']=False if 'active' not in dict['auth']['ldap'] else True
        if 'engine' in dict:
            if 'carbon' in dict['engine']:
                dict['engine']['carbon']['active']=False if 'active' not in dict['engine']['carbon'] else True
        if 'disposable_desktops' in dict:
            dict['disposable_desktops'].pop('id',None)
            dict['disposable_desktops']['active']=False if 'active' not in dict['disposable_desktops'] else True
        if app.adminapi.update_table_dict('config',1,dict):
            return json.dumps('Updated'), 200, {'ContentType':'application/json'}
    return json.dumps('Could not update.'), 500, {'ContentType':'application/json'}


'''
BACKUP & RESTORE
'''
@app.route('/admin/backup', methods=['POST'])
@login_required
@isAdmin
def admin_backup():
    if request.method == 'POST':
        app.adminapi.backup_db()
        return json.dumps('Updated'), 200, {'ContentType':'application/json'}
    return json.dumps('Method not allowed.'), 500, {'ContentType':'application/json'}

@app.route('/admin/restore', methods=['POST'])
@login_required
@isAdmin
def admin_restore():
    if request.method == 'POST':
        app.adminapi.restore_db(request.get_json(force=True)['pk'])
        return json.dumps('Updated'), 200, {'ContentType':'application/json'}
    return json.dumps('Method not allowed.'), 500, {'ContentType':'application/json'}

@app.route('/admin/backup_remove', methods=['POST'])
@login_required
@isAdmin
def admin_backup_remove():
    if request.method == 'POST':
        app.adminapi.remove_backup_db(request.get_json(force=True)['pk'])
        return json.dumps('Updated'), 200, {'ContentType':'application/json'}
    return json.dumps('Method not allowed.'), 500, {'ContentType':'application/json'}
    
@app.route('/admin/stream/backups')
@login_required
@isAdmin
def admin_stream_backups():
    return Response(admin_backups_stream(), mimetype='text/event-stream')

def admin_backups_stream():
    with app.app_context():
        for c in r.table('backups').changes(include_initial=False).run(db.conn):
            if c['new_val'] is None:
                yield 'retry: 5000\nevent: %s\nid: %d\ndata: %s\n\n' % ('Deleted',time.time(),json.dumps(c['old_val']))
                continue
            if c['old_val'] is None:
                yield 'retry: 5000\nevent: %s\nid: %d\ndata: %s\n\n' % ('New',time.time(),json.dumps(app.isardapi.f.flatten_dict(c['new_val'])))   
                continue             
            if 'detail' not in c['new_val']: c['new_val']['detail']=''
            yield 'retry: 2000\nevent: %s\nid: %d\ndata: %s\n\n' % ('Status',time.time(),json.dumps(app.isardapi.f.flatten_dict(c['new_val'])))
                    


