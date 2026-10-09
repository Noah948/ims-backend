# this file is used to register all the scheduler jobs that need to be run periodically.

from scheduler.scheduler import scheduler
from scheduler.jobs.cleanup import register_cleanup_jobs
from scheduler.jobs.subscription import register_subscription_jobs
from scheduler.jobs.snapshot import register_snapshot_jobs


def register_jobs() -> None:
    register_cleanup_jobs(scheduler)
    register_subscription_jobs(scheduler)
    register_snapshot_jobs(scheduler)
