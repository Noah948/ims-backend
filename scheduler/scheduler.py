# this file is used to schedule the tasks that need to be run periodically.

from apscheduler.schedulers.blocking import BlockingScheduler

scheduler = BlockingScheduler(
    timezone="Asia/Kolkata"
)