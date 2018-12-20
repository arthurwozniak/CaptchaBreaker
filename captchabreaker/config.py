DEBUG = True

CELERY_BROKER_URL = 'amqp://rabbitmq:rabbitmq@127.0.0.1:5672'
CELERY_RESULT_BACKEND = 'rpc://'

SQLALCHEMY_DATABASE_URI = 'postgresql://docker:y9Brhf6v@127.0.0.1'
SQLALCHEMY_TRACK_MODIFICATIONS = False

LOG_FILENAME = 'captcha_app.log'

EXPLAIN_TEMPLATE_LOADING = False