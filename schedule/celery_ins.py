# encoding=utf-8

"""
    @author: lyz
    @date: 2019/5/29
"""

from celery import Celery


def make_celery(app, broker='CELERY_BROKER_URL', backend='CELERY_BACKEND_URL'):
    celery = Celery(app.import_name,
                    broker=app.config[broker],
                    backend=app.config[backend],
                    )

    celery.conf.update(
        CELERY_DEFAULT_QUEUE='pool_queue',
        CELERY_TASK_SERIALIZER='json',
        CELERY_ACCEPT_CONTENT=['json'],
        CELERY_RESULT_SERIALIZER='json',
        CELERY_TIMEZONE='Asia/Shanghai',
        CELERY_ENABLE_UTC=True,
        CELERY_TASK_RESULT_EXPIRES=1200,
        CELERYD_CONCURRENCY=12,
        CELERYD_FORCE_EXECV=True,
        CELERY_TASK_PUBLISH_RETRY=3,
        CELERYD_TASK_SOFT_TIME_LIMIT=360,
        CELERYD_TASK_TIME_LIMIT=600,
    )

    task_base = celery.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery