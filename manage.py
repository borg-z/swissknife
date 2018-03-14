
from flask_script import Manager
from app import app
from rq import Connection, Worker
import redis
from app.tasks import update_graph

manager = Manager(app)


REDIS_URL = 'redis://redis:6379/0'
QUEUES = ['default']


@manager.command
def runworker():
    redis_url = app.config['REDIS_URL']
    redis_connection = redis.from_url(redis_url)
    with Connection(redis_connection):
        worker = Worker(app.config['QUEUES'])
        worker.work()




if __name__ == "__main__":
    manager.run()
