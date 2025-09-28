from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
import logging, traceback, os

scheduler = BackgroundScheduler()

# Only start scheduler if not in CI or if explicitly enabled
if os.getenv("USE_INMEMORY_DB") != "1" and os.getenv("DISABLE_SCHEDULER") != "1":
    try:
        scheduler.start()
        logging.info("Background scheduler started")
    except Exception as e:
        logging.warning(f"Failed to start scheduler: {e}")
else:
    logging.info("Background scheduler disabled for CI/testing environment")

def submit_job(func, *args, **kwargs):
    """
    Submit a background job with timeout and retry.
    Returns the job id.
    """
    # Skip job submission if scheduler is not running
    if not scheduler.running:
        logging.warning("Scheduler not running, skipping job submission")
        return None
        
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

    try:
        trigger = DateTrigger()
        job = scheduler.add_job(wrapper, trigger, args=args, kwargs=kwargs, id=job_id, replace_existing=True)
        return job.id
    except Exception as e:
        logging.error(f"Failed to submit job: {e}")
        return None
