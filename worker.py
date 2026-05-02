from redis import Redis
from rq import Worker, Queue

redis_conn = Redis(host="redis", port=6379)

queue = Queue(connection=redis_conn)

if __name__ == "__main__":
    worker = Worker([queue], connection=redis_conn)
    worker.work()