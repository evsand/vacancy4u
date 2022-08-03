import time

from flask import render_template, url_for, request, redirect, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from urllib.parse import urlparse

from pack import app, db, login_manager
from pack.forms import RegisterForm, LoginForm
from pack.models import Vacancies, Users
from parser.parser_vacancy import get_links, get_vacancy, get_link_resume


def is_url(url):
  try:
    result = urlparse(url)
    return all([result.scheme, result.netloc])
  except ValueError:
    return False


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/find', methods=['POST', 'GET'])
def find():
    if request.method == 'POST':
        link_resume = request.form['link_resume']
        if is_url(link_resume) == False:
            flash('Ссылка некоректна!')
            return redirect('https://www.youtube.com/watch?v=GJ2RdGHizs8')
        resume = get_link_resume(link_resume)
        for link_vac in get_links(resume):
            vacancy = get_vacancy(link_vac, resume)
            time.sleep(1)
            try:
                db.session.add(Vacancies(
                                vac_name=vacancy['name'], #rename
                                salary=vacancy['salary'],
                                skills=vacancy['tags'],
                                link=vacancy['link'],
                                low_rate=vacancy['lrate'],
                                ))
                db.session.commit()

            except Exception as e:
                return f"Ошибочка вышла {e}"
        #    print(f"link: {vac['link']}    concurrency: {vac['lrate'] * 100}%")
        return redirect('/result')
    return render_template('find.html')


@app.route('/result', methods=['POST', 'GET'])
@login_required
def result():
    vacancy = Vacancies.query.order_by(-Vacancies.low_rate).limit(3).all()

    return render_template('result.html', vacancy=vacancy)


@app.route("/register", methods=("POST", "GET"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # здесь должна быть проверка корректности введенных данных
        try:
            hash = generate_password_hash(request.form['psw'])
            u = Users(email=request.form['email'], psw=hash, login=request.form['login'])
            db.session.add(u)
            db.session.commit()
            flash('Регистрация прошла успешно', category='success')
        except:
            db.session.rollback()
            flash("Ошибка при добавлении в БД", category="error")

        return redirect(url_for('index'))

    return render_template("register1.html", title="Регистрация", form=form)


@app.route("/login", methods=["POST", "GET"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('profile'))
    form = LoginForm()
    #if form.validate_on_submit():
    if request.method == 'POST':
        psw = request.form['psw']
        remember = True if request.form.get('remember') else False
        user = Users.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.psw, psw):
            flash(f'Hello {user}', category='success')
            login_user(user, remember=remember)
            return redirect(request.args.get("next") or url_for("profile"))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html",  title="Авторизация", form=form)


@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html", title="Профиль")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта", "success")
    return redirect(url_for('index'))


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)