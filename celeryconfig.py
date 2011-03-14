# -*-coding: UTF-8-*-

"""Options for Celery

http://docs.celeryproject.org/en/v2.2.4/getting-started/first-steps-with-celery.html
"""

BROKER_HOST = "localhost"
BROKER_PORT = 5672
BROKER_USER = "texturejam"
BROKER_PASSWORD = "texturejam"
BROKER_VHOST = "texturejam"

CELERY_RESULT_BACKEND = "amqp"

CELERY_IMPORTS = (
    "recipes.tasks",
)
