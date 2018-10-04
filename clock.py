import os

from message import Message
from apscheduler.schedulers.blocking import BlockingScheduler


access_token = 'WgdkiHLjL5Qe0AgGUhqAnXExQuPQIdvah67xTDQr'
group_id = '13388728'

sched = BlockingScheduler()

@sched.scheduled_job('cron', day_of_week='mon', hour=1, timezone='America/New_York')
def scheduled_job():
    msg.load()
    msg.update()
    msg.save()
