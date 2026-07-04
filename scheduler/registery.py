# this file is used to register all the scheduler jobs that need to be run periodically.

from scheduler.scheduler import scheduler
from scheduler.jobs.cleanup import register_cleanup_jobs


def register_jobs() -> None:
    register_cleanup_jobs(scheduler)