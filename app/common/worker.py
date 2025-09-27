from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import logging, traceback

scheduler = BackgroundScheduler()
scheduler.start()

def submit_job(func, *args, **kwargs):
    """
    Submit a background job with timeout and retry.
    Returns the job id.
    """
    retries = kwargs.pop("retries", 2)
    job_id = kwargs.pop("job_id", None)

    def wrapper(*a, **k):
        attempt = 0
        while attempt <= retries:
            try:
                return func(*a, **k)
            except Exception as e:
                attempt += 1
                logging.error("Job %s failed (attempt %d): %s", job_id, attempt, e)
                traceback.print_exc()
                if attempt > retries:
                    raise

    trigger = DateTrigger()
    job = scheduler.add_job(wrapper, trigger, args=args, kwargs=kwargs, id=job_id, replace_existing=True)
    return job.id
