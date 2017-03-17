# Copyright 2017 the Isard-vdi project authors:
#      Josep Maria Viñolas Auquer
#      Alberto Larraz Dalmases
# License: AGPLv3

#!/usr/bin/env python
# coding=utf-8
from decimal import Decimal
import random, queue
from threading import Thread
import time
from webapp import app
import rethinkdb as r

from .flask_rethink import RethinkDB
db = RethinkDB(app)
db.init_app(app)

from ..lib.log import *

from apscheduler.schedulers.gevent import GeventScheduler
from apscheduler.jobstores.rethinkdb import RethinkDBJobStore

from datetime import datetime, timedelta

class isardScheduler():
    def __init__(self):
        '''
        JOB SCHEDULER
        '''
        self.rStore=RethinkDBJobStore()
        self.scheduler = GeventScheduler()
        self.scheduler.add_jobstore('rethinkdb',self.rStore, database='isard', table='scheduler_jobs')
        #~ app.scheduler.remove_all_jobs()
        #~ scheduler.add_job(alarm, 'date', run_date=alarm_time, args=[datetime.now()])
        #~ app.sched.shutdown(wait=False)
        self.turnOn()
        
        
    def addCron(self,table,tbl_filter,tbl_update,hour,minute):
        id='cron_'+str(hour)+str(minute)
        self.scheduler.add_job(self.bulk_action,'cron', hour=hour, minute=minute, args=(table,tbl_filter,tbl_update), jobstore=self.rStore, replace_existing=True, id=id)
        with app.app_context():
            r.table('scheduler_jobs').get(id).update({'kind':'cron','table':table,'filter':tbl_filter,'update':tbl_update,'hour':hour,'minute':minute}).run(db.conn)

    def addDate(self,table,filter,update,seconds):
        alarm_time = datetime.now() + timedelta(seconds=seconds)
        self.scheduler.add_job(self.bulk_action,'date', run_date=alarm_time, args=[table,filter,update], jobstore=self.rStore, replace_existing=True, id='p1')

    def addInterval(self,table,filter,update,seconds):
        alarm_time = datetime.now() + timedelta(seconds=10)
        self.scheduler.add_job(self.bulk_action,'interval', run_date=alarm_time, args=[table,filter,update], jobstore=self.rStore, replace_existing=True, id='p1')

    def clean_stats(self):
        self.scheduler.add_job(self.remove_old_stats, 'interval', minutes=20, jobstore=self.rStore, replace_existing=True, id='clean_stats')
        with app.app_context():
            r.table('scheduler_jobs').get('clean_stats').update({'kind':'interval','table':'','filter':'','update':'','hour':0,'minute':20}).run(db.conn)
  
    def remove_old_stats():
        with app.app_context():
            r.table('domains_status').filter(r.row['when'] < int(time.time()) - 1200).delete().run(db.conn)  
            r.table('hypervisors_events').filter(r.row['when'] < int(time.time()) - 1200).delete().run(db.conn)  
            r.table('hypervisors_status').filter(r.row['when'] < int(time.time()) - 1200).delete().run(db.conn)  
                
    #~ def getJobs(self):
        #~ return self.scheduler.print_jobs()
        
    def turnOff(self):
        self.scheduler.shutdown()
    
    def turnOn(self):
        self.scheduler.start()
    
    def removeJobs(self):
        self.scheduler.remove_all_jobs()
    '''
    BULK ACTIONS
    '''
    def bulk_action(self,table,tbl_filter,tbl_update):
        with app.app_context():
            log.info('BULK ACTION: Table {}, Filter {}, Update {}'.format(table,filter, update))
            r.table(table).filter(filter).update(update).run(db.conn)
            #~ r.table(table).filter({'status':'Unknown'}).update({'status':'Stopping'}).run(db.conn)
   
