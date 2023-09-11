
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.memory import MemoryJobStore

from pytz import utc

scheduler = BackgroundScheduler(jobstores={"sms_service": MemoryJobStore()}, timezone=utc)

