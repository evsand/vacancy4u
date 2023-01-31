from flask import Flask



app = Flask(__name__)

app.config['SECRET_KEY'] = '12515215616kkSECRET_KEYkfqpefq1251298'


app.config['CELERY_BROKER_URL'] = 'amqp://admin:mypass@rabbit:5672'
app.config['CELERY_RESULT_BACKEND'] = 'rpc://'


from pack import  routes