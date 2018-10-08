import os
from apscheduler.schedulers.blocking import BlockingScheduler
from message import Message


access_token = os.getenv('access_token')
group_id = os.getenv('group_id')

sched = BlockingScheduler()


@sched.scheduled_job('cron', day_of_week='mon', hour=1, timezone='America/New_York')
def scheduled_job():
    file_path = os.path.join(os.path.dirname(__file__), 'src')
    msg = Message(access_token, group_id, file_path)
    msg.load()
    msg.update()
    msg.save()
