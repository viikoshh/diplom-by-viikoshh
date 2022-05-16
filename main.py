from flask import Flask, render_template,session, request, redirect, Markup
from flask_sqlalchemy import SQLAlchemy
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_menu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
#app.secret_key = 'секретный ключ'


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Integer, nullable=False)
    composition = db.Column(db.Text, nullable=False)
    KBJU = db.Column(db.Text, nullable=False)
    discover_text = db.Column(db.String, nullable=True)
    discover_url = db.Column(db.Text, nullable=True)
    season = db.Column(db.String, nullable=True)
    time_day = db.Column(db.String, nullable=True)
    category = db.Column(db.String, nullable=True)

    def __repr__(self):
        return


class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name_client = db.Column(db.String(100), nullable=True)
    login = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    telephone = db.Column(db.String(100), nullable=True)
    categorya = db.Column(db.String(100), nullable=True)
    allergy = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return


@app.route('/')
def index():
    items = Item.query.order_by(Item.id).all()
    return render_template('index.html', data=items)


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/sign', methods=['POST', 'GET'])
def sign():
    #if 'hash' in session:
    #    connection = sqlite3.connect('base_menu.db')
    #    cur = connection.cursor()
    #    cur.execute("SELECT * FROM name_client WHERE name_client='" + session['name_client'] + "'")
    #    rows = cur.fetchall()
#
    #    for row in rows:
    #        print(row)
    #    if (len(rows)):
    #        password = rows[0][3]
    #        hash = generate_password_hash(password)
    #        result = check_password_hash(hash, password)
    #        print(result)
    #        #content = Markup("Вы уже авторизованы<br><a href='/delete-session'>Выйти из сессии</a>")
    #        auth_error_of_sign = Markup("Вы уже авторизованы")
    #        return render_template('sign.html', auth_error_of_sign=auth_error_of_sign)

    if request.method == "POST":
        name_client = request.form['name_client']
        login = request.form['login']
        password = request.form['password']
        email = request.form['email']
        telephone = request.form['telephone']
        categorya = request.form['categorya']
        allergy = request.form['allergy']

        password_hash = generate_password_hash(password)

        connection = sqlite3.connect('base_menu.db')
        cur = connection.cursor()
        cur.execute("SELECT * FROM client WHERE login='" + login + "'")
        rows = cur.fetchall()
        if (len(rows)):
            login_incorrect = Markup('<span class="errorMsg">Такой логин уже существует!</span>')
            connection.close()
            return render_template('sign.html', login_incorrect=login_incorrect)

        cur.execute("SELECT * FROM client WHERE email='" + email + "'")
        rows = cur.fetchall()
        if (len(rows)):
            email_incorrect = Markup('<span class="errorMsg">Такой email уже существует!</span>')
            connection.close()
            return render_template('sign.html', email_incorrect=email_incorrect)

        client = Client(name_client=name_client, login=login, password_hash=password_hash, email=email, telephone=telephone,categorya=categorya, allergy=allergy)

        try:
            db.session.add(client)
            db.session.commit()
            return redirect('/')
        except:
            message_error = Markup('<span class="errorMsg">Возникла ошибка! Проверьте, все ли поля заполнены</span>')
            connection.close()
            return render_template('sign.html', message_error=message_error)

    else:
        return render_template('sign.html')


@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == "POST":
        name = request.form['name']
        photo = request.form['photo']
        price = request.form['price']
        weight = request.form['weight']
        composition = request.form['composition']
        KBJU = request.form['KBJU']
        discover_text = request.form['discover_text']
        discover_url = request.form['discover_url']
        season = request.form['season']
        time_day = request.form['time_day']
        category = request.form['category']
        connection = sqlite3.connect('base_menu.db')

        item = Item(name=name, photo=photo, price=price, weight=weight, composition=composition, KBJU=KBJU, discover_text=discover_text, discover_url=discover_url, season=season, time_day=time_day, category=category)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return "Не все поля заполнены!"
    else:
        return render_template('create.html')


if __name__ == '__main__':
    app.run(debug=True)