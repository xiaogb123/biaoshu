from redis import Redis
from rq import Queue
from app.core.config import settings

queue = Queue(connection=Redis.from_url(settings.REDIS_URL))