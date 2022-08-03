import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


#SECRET_KEY = os.urandom(32)
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '12515215616kkSECRET_KEYkfqpefq1251298'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vacancies.db'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для доступа к закрытым страницам'
login_manager.login_message_category = 'success'


from pack import models, routes