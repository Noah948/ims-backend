# this file is used to schedule the tasks that need to be run periodically.

# use this scheduler when you want to have only one server instance running
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler(
    timezone="Asia/Kolkata"
)

# use this scheduler when you want to have multiple server instances
# so with this you can have mustiple servers running + this scheduler isolated 

# from apscheduler.schedulers.blocking import BlockingScheduler

# scheduler = BlockingScheduler(
#     timezone="Asia/Kolkata"
# )