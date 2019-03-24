DEBUG = True

CELERY_BROKER_URL = 'amqp://rabbitmq:rabbitmq@127.0.0.1:5673'
CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/0'

SQLALCHEMY_DATABASE_URI = 'postgresql://docker:y9Brhf6v@127.0.0.1'
SQLALCHEMY_TRACK_MODIFICATIONS = False

SECRET_KEY = 'something-secret'
SIMPLELOGIN_USERNAME = 'demo'
SIMPLELOGIN_PASSWORD = 'demo'


LOG_FILENAME = 'captcha_app.log'

EXPLAIN_TEMPLATE_LOADING = False

HTML_TITLE = 'CaptchaBreaker'

MODEL_DIRECTORY = '/home/kamil/git/CaptchaBreaker/data'