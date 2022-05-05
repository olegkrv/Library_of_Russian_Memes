import sqlite3


import uuid
from flask import Flask, render_template, request, redirect, abort
from flask_login import LoginManager, login_required, login_user, logout_user, UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import DataRequired
import sqlalchemy.ext.declarative as dec
from data import db_session
from data.memes import Memes
from data.users import User

SqlAlchemyBase = dec.declarative_base()

__factory = None

sqlite_connection = sqlite3.connect('db/blogs.db')
cursor = sqlite_connection.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)
CATEGORY_NAMES = ['pictures', 'formulaics', 'adjacents']


CLASSES_NAMES = [('С текстом', 'Без текста'), ('Идейный', 'Визуальный'), ('Ситуационный', 'Классического типа')]
CLASSES_NAMES_MORE = [('С текстом', 'Без текста'), ('Идейные', 'Визуальные'), ('Ситуационные', 'Классического типа')]
CATEGORY_NAMES_RU = ['Пикча', 'Шаблонный', 'Смежный']


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Зарегистрироваться')


class MemesForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Содержимое")
    submit = SubmitField('Применить')
    image = FileField('Выберите файл')
    typpe = StringField('Тип', validators=[DataRequired()])
    meme_class = StringField('Класс', validators=[DataRequired()])


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def meme():
    db_session.global_init("db/blogs.db")
    return render_template('BASEEEED.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('Registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('Registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        print('sassdssf')
        db_sess.commit()
        current_user = user
        print(type(user), type(current_user))
        return redirect('/login')
    else:
        print(form.name.errors, form.email.errors, form.about.errors)
    return render_template('Registration.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('Authorization.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('Authorization.html', title='Авторизация', form=form)


@app.route('/add_meme', methods=['GET', 'POST'])
@login_required
def add_meme():
    form = MemesForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        memes = Memes()
        memes.title = form.title.data
        memes.content = form.content.data
        filename = str(uuid.uuid4())
        memes.image = filename
        form.image.data.save('static/images/upload/{}.jpg'.format(filename))
        memes.typpe = form.typpe.data
        if memes.typpe not in CATEGORY_NAMES_RU:
            return render_template('Add_meme.html', title='Добавление мема',
                                   form=form, message='Введённого типа не существует')
        memes.meme_class = form.meme_class.data
        categ_number = CATEGORY_NAMES_RU.index(memes.typpe)
        if memes.meme_class not in CLASSES_NAMES[categ_number]:
            return render_template('Add_meme.html', title='Добавление мема',
                                   form=form,
                                   message='Введённого класса не существует или нет конкретно в этой типе')
        current_user.memes.append(memes)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/')
    return render_template('Add_meme.html', title='Добавление мема',
                           form=form)


@app.route("/library/<categ>")
def categ_index(categ):
    if categ not in CATEGORY_NAMES:
        abort(404)
    categ_number = CATEGORY_NAMES.index(categ)
    db_sess = db_session.create_session()
    ru_categ = CATEGORY_NAMES_RU[categ_number]
    memes = db_sess.query(Memes).filter(Memes.typpe == ru_categ).all()
    titles1 = []
    titles2 = []
    for i in memes:
        if i.typpe == CLASSES_NAMES[categ_number][0]:
            titles1.append(i.title)
            print(1, i.title)
        elif i.typpe == CLASSES_NAMES[categ_number][1]:
            titles2.append(i.title)
            print(2, i.title)
    l1 = len(titles1) // 4 + 1
    l2 = len(titles2) // 4 + 1
    print(l1, l2)
    return render_template("Inside_category.html", memes=memes, sektor=ru_categ, category=categ,
                           cnm=CLASSES_NAMES_MORE[categ_number], cls_nm=CLASSES_NAMES[categ_number],
                           l=[l1, l2])


@app.route("/library")
def index():
    db_sess = db_session.create_session()
    news = db_sess.query(Memes)
    return render_template("Library.html", news=news)


@app.route("/library/<categ>/<meme_id>")
def FIindex(categ, meme_id):
    if categ not in CATEGORY_NAMES:
        abort(404)
    categ_number = CATEGORY_NAMES.index(categ)
    ru_categ = CATEGORY_NAMES_RU[categ_number]
    db_sess = db_session.create_session()
    memes = db_sess.query(Memes).filter(Memes.typpe == ru_categ, Memes.id == meme_id).one()
    if not memes:
        abort(404)
    return render_template("Meme.html", memes=memes, sektor=categ_number, category=categ, ru_categ=ru_categ,
                           cls=memes.meme_class)


@app.route("/classification")
def classif():
    with open('Text.txt') as t:
        text = t.readlines()
    return render_template('Classification.html', text=text)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
