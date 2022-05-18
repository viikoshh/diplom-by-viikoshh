from flask import Flask, render_template, session, request, redirect, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,  login_required, login_user, current_user, logout_user
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

app = Flask(__name__)
app.debug = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_menu.db'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////home/viikoshh/diplom-by-viikoshh/base_menu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'hP51NJG8DrIj1oQi63Z5syHaQ8TTUwX6eT4UvCPYWoaXET4zSYxdn5f50ZPLoFGtoCeM3WDWaFKFpJ3axvdNtjJj1rXnWtJdYP'
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(id):
    return Client.query.get(int(id))


class Orders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    loginID = db.Column(db.String(100), nullable=False)
    orderlist = db.Column(db.Text, nullable=False)
    status = db.Column(db.String, nullable=False)
    data = db.Column(db.String, nullable=False)

    def __repr__(self):
        return


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


class Client(UserMixin, db.Model):
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


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    items = Item.query.order_by(Item.id).all()

    return render_template('index.html', data=items)


@app.route('/admin')
@login_required
def admin_index():
    items = Item.query.order_by(Item.id).all()
    return render_template('index_admin.html', data=items)


@app.route('/admin/<int:id>/delete')
def admin_delete(id):
    item = Item.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/admin')
    except:
        return "При удалении статьи произошла ошибка"


@app.route('/admin/<int:id>/update', methods=['GET', 'POST'])
@login_required
def admin_update(id):
    item = Item.query.get(id)
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
        #connection = sqlite3.connect('base_menu.db')

        item = Item(name=name, photo=photo, price=price, weight=weight, composition=composition, KBJU=KBJU, discover_text=discover_text, discover_url=discover_url, season=season, time_day=time_day, category=category)

        try:
            db.session.commit()
            return redirect('/admin')
        except:
            return "Error"

    else:
        item = Item.query.get(id)
        return render_template('item_update.html', item=item)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        login = request.form['login']
        password = request.form['password']

        user = Client.query.filter_by(login=login).first()
        if not user or not check_password_hash(user.password_hash, password):
            auth_error = Markup('Ошибка! Повторите попытку авторизации')
            return render_template('login.html', auth_error=auth_error)
        login_user(user)
        if current_user.login == 'admin_viikoshh':
            return redirect('/admin')
        else:
            return redirect('/menu')
    else:
        return render_template('login.html')


@app.route('/sign', methods=['GET','POST'])
def sign():
    if request.method == "POST":
        name_client = request.form['name_client']
        login = request.form['login']
        email = request.form['email']
        telephone = request.form['telephone']
        categorya = request.form['categorya']
        allergy = request.form['allergy']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        connection = sqlite3.connect('base_menu.db')
        #connection = sqlite3.connect('///home/viikoshh/diplom-by-viikoshh/base_menu.db')
        cur = connection.cursor()
        cur.execute("SELECT * FROM client WHERE login='" + login + "'")
        rows = cur.fetchall()
        if (len(rows)):
            login_incorrect = Markup('Такой логин уже существует!')
            connection.close()
            return render_template('sign.html', login_incorrect=login_incorrect)

        cur.execute("SELECT * FROM client WHERE email='" + email + "'")
        rows = cur.fetchall()
        if (len(rows)):
            email_incorrect = Markup('Такой email уже существует!')
            connection.close()
            return render_template('sign.html', email_incorrect=email_incorrect)
        client = Orders(name_client=name_client, login=login, password_hash=password_hash, email=email, telephone=telephone, categorya=categorya, allergy=allergy)
        try:
            db.session.add(client)
            db.session.commit()
            return redirect('/menu')
        except:
            message_error = Markup('Возникла ошибка! Проверьте, все ли поля заполнены')
            connection.close()
            return render_template('sign.html', message_error=message_error)
        connection.close()
    else:
        return render_template('sign.html')


@app.route('/menu', methods=['GET','POST'])
@login_required
def menu():
    items = Item.query.order_by(Item.id).all()
    if request.method == "POST":
        dishID_list = request.form.getlist('dishID')
        # если корзина ещё не создана
        if not session.get('cart'):
            session['cart'] = []
        # добавляем инфу о товаре в список
        session['cart'] += dishID_list
        return redirect('/cart')

    else:
        return render_template('index.html', data=items)


@app.route('/cart/delete')
def delete_cart():
    # если корзина ещё не создана
    if not session.get('cart'):
        redirect('/menu')
    session.pop('cart', None)
    return redirect('/menu')


@app.route('/cart', methods=['GET','POST'])
@login_required
def cart():
    orderlist = session['cart']
    connection = sqlite3.connect('base_menu.db')
    # connection = sqlite3.connect('///home/viikoshh/diplom-by-viikoshh/base_menu.db')
    cur = connection.cursor()
    order_items = list()
    for i in orderlist:
        cur.execute("SELECT id,name,photo, price FROM item WHERE id='" + str(int(i)) + "'")
        sp = cur.fetchall()
        current_order = [*sp, 1, sp[0][-1]]
        order_items.append(current_order)
    order_id = set()
    orders = []
    for i in order_items:
        if i[0][0] not in order_id:
            order_id.add(i[0][0]);
            orders.append(i)
    order_items = orders.copy()
    # Если заказ еще не сформирован
    if not session.get('order'):
        session['order'] = []
    order_cur = json.dumps(list(order_id))
    session['order'] = order_cur
    #print(session['order'])
    if request.method == "POST":
        count = request.form.getlist('count')
        cost = 0
        for i in range(len(order_items)):
            order_items[i][1] = int(count[i])
            order_items[i][2] = int(count[i]) * order_items[i][0][3]
            cost += order_items[i][2]
        return redirect('/pay')

    #    redirect('/cart')
    #session.pop('cart', None)
    return render_template('cart.html', order=order_items)
    #return render_template('cart.html')


@app.route('/pay', methods=['GET','POST'])
@login_required
def pay():
    if request.method == "POST":
        loginID = current_user.login
        orderlist= session['order']
        status = 'Готовится'
        data = str(datetime.datetime.now())
        if not session.get('data'):
            session['data'] = 0
        session['data'] = data
        order = Orders(loginID=loginID, orderlist=orderlist, status=status, data=data)
        try:
            db.session.add(order)
            db.session.commit()
            return redirect('/order')
        except:
            return "Что-то пошло не так"


    return render_template('pay.html')


@app.route('/order', methods=['GET','POST'])
@login_required
def order():
    connection = sqlite3.connect('base_menu.db')
    # connection = sqlite3.connect('///home/viikoshh/diplom-by-viikoshh/base_menu.db')
    cur = connection.cursor()
    cur.execute("SELECT id FROM orders WHERE loginID='" + str(current_user.login) + "' AND data='"+ session['data']+"'")
    id = cur.fetchall()
    order_cur = Orders.query.get(id[0])
    if request.method == "POST":
        order_cur.status = 'Получен'
        try:
            db.session.commit()
            print('OK')
            return redirect('/logout')
        except:
            print('ERROR')
            return render_template('order.html')



    return render_template('order.html')


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
        #connection = sqlite3.connect('base_menu.db')

        item = Item(name=name, photo=photo, price=price, weight=weight, composition=composition, KBJU=KBJU, discover_text=discover_text, discover_url=discover_url, season=season, time_day=time_day, category=category)

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/admin')
        except:
            return "Не все поля заполнены!"

    else:
        return render_template('create.html')


### НАЧАЛО ИЗМЕНЕНИЙ
# from time import time
import time


# Класс робот
class Robot():
    starttime = None
    endtime = None
    state = "ready"
    velocity = 0  # m/s
    table = 0
    tables = list()  # INT(table):INT(distance in meters)

    def __init__(self, tables, velocity):
        self.tables = tables
        self.velocity = velocity
        # Отправить к столу

    def sendToTable(self, table):
        if table not in self.tables:
            print("no table")
            return None
        self.checkCondition()
        if self.state != "ready":
            return None
        self.table = table
        self.starttime = time.time();
        self.endtime = self.starttime + self.tables[table] / self.velocity

        self.state = "delivering"
        return self.endtime - self.starttime
        # вернуть на базу

    def comeback(self):
        self.checkCondition()
        if self.state != "waiting":
            return None
        self.starttime = time.time();
        self.endtime = self.starttime + self.tables[self.table] / self.velocity
        self.state = "comeback"
        return self.endtime - self.starttime
        # проверить состояние

    def checkCondition(self):
        if self.state == "ready":
            return self.state
        if (self.state == "delivering"):
            if time.time() < self.endtime:
                return self.state
            else:
                self.endtime = None
                self.starttime = None
                self.state = "waiting"
                return self.state
        if self.state == "comeback":
            if time.time() < self.endtime:
                return self.state
            else:
                self.endtime = None
                self.starttime = None
                self.state = "ready"
                return self.state
        if self.state == "waiting":
            return self.state

        # ОБЪЯВЛЕНИЕ СТОЛОВ К РОБОТАМ И ДИСТАНЦИИ ДО НИХ


a1 = {1: 10, 2: 10, 3: 5, 4: 20}
a2 = {5: 10, 6: 10, 7: 5, 8: 10}
a3 = {9: 10, 10: 10, 11: 5, 12: 30}
# ОБЪЯВЛЕНИЕ ТРЕХ РОБОТОВ
robotsList = list()
robotsList.append(Robot(a1, 1))
robotsList.append(Robot(a2, 1))
robotsList.append(Robot(a3, 1))


# print(tr1.sendToTable(5))

def updateStatelist():
    st = list()
    for robot in robotsList:
        st.append(robot.checkCondition())
    return st


@app.route('/robots/', methods=['GET', 'POST'])
def robots():
    global robotsList
    result = "no commands"
    st = updateStatelist()
    if request.method == "POST":
        if "type" in request.form:
            typeOfRequest = request.form['type']
            # если нажато "отправить робота к столу"
            if typeOfRequest == "send" and 'table' in request.form:
                try:
                    table = int(request.form['table'])
                    print("table ", table)
                except ValueError as err:
                    result = "failure"
                else:
                    id = 0
                    # пробуем отправить любого из доступных роботов
                    # если у робота нет возможности доехать до стола он возвращает None
                    for robot in robotsList:
                        time = robot.sendToTable(table)
                        if time is not None:
                            result = "success"
                            st = updateStatelist()
                            return json.dumps(
                                {"statelist": st, "result": result, "time": int(time), "id": id, "dst": "table",
                                 "table": table})
                            break
                        id += 1
                        result = "failure"
                    return json.dumps({"statelist": st, "result": result})
                # Если нажато вернуть робота
            if typeOfRequest == "comeback" and 'robot' in request.form:
                robot = int(request.form['robot'])
                if robot < len(robotsList):
                    time = robotsList[robot].comeback()
                    if time:
                        result = "success. time: " + str(time)
                        st = updateStatelist()
                        return json.dumps(
                            {"statelist": st, "result": result, 'id': robot, "time": int(time), "dst": "station",
                             "table": robotsList[robot].table})
                    else:
                        result = "failure"
                else:
                    result = "list out of range"
                return json.dumps({"statelist": st, "result": result})
                # если нажато "обновить"
            if typeOfRequest == "refresh":
                return json.dumps({"statelist": st, "result": result})

    return render_template('robots.html', statelist=st, result=result)


### КОНЕЦ ИЗМЕНЕНИЙ




if __name__ == '__main__':
    app.run(debug=True)