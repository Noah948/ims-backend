from scheduler.scheduler import scheduler
from scheduler.registery import register_jobs


def main():
    register_jobs()

    print("Scheduler started...")

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        print("Scheduler stopped.")


if __name__ == "__main__":
    main()

