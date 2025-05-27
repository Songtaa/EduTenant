# from rq import  Worker, Connection


# from .queues import redis, queues

# if __name__ == '__main__':
#     with Connection(redis):
#         worker = Worker( queues, connection=redis )
#         worker.work()

from rq import Worker
from redis import from_url

# Import connection directly from redis
from .queues import redis, queues

if __name__ == '__main__':
    worker = Worker(queues=list(queues.values()), connection=redis)
    worker.work()



