from celery import Celery


app = Celery(
    'parser',
    broker='amqp://admin:mypass@rabbit//',
    backend='rpc://',
    include=['parser.tasks'],
)


if __name__ == '__main__':
    app.start()