from gunicorn.config import Config

class MyConfig(Config):
    workers = 3
    worker_class = 'sync'
