from flask import Flask


app = Flask(__name__)
app.config.update(dict(
    SECRET_KEY = 'your_secret_key',
    CSRF_ENABLED = True,
    RQ_REDIS_URL = 'redis://redis:6379/0',
    RQ_QUEUES = ['default'],
    ))

app.config['MONGODB_SETTINGS'] = {
                        'db': 'devices',
                        'host': 'mongo-prod',
                        'port': 27017
                        }


from app import views

