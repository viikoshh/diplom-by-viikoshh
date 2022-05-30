from flask import Flask, render_template, session, request, redirect, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin,  login_required, login_user, current_user, logout_user
import sqlite3
import json
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
from random import sample, choice

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


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return


class Season(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_year = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return


class Time_day(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day_time = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return


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

    def __repr__(self):
        return


def AISeason():
    month = int(datetime.datetime.now().month)
    if month in range(5, 10):
        ses = Season.query.filter(Season.time_year == 'Летнее').first()
        h5 = "Освежитесь!"
    else:
        ses = Season.query.filter(Season.time_year == 'Зимнее').first()
        h5 = "Согрейтесь!"
    rec_ses = Item.query.filter(Item.season == ses.id)
    rec_id = []
    for i in rec_ses:
        rec_id.append(i.photo)
    a, b = tuple(sample(rec_id, 2))
    return a,b, h5


def AIDay():
    hour = int(datetime.datetime.now().hour)
    if hour in range(5, 12):
        ses = Time_day.query.filter(Time_day.day_time == 'Утреннее').first()
        h5 = "С завтрака все начинается!"
    elif hour in range(12, 18):
        ses = Time_day.query.filter(Time_day.day_time == 'Дневное').first()
        h5 = "Не забудьте пообедать"
    else:
        ses = Time_day.query.filter(Time_day.day_time == 'Вечернее').first()
        h5 = "Проведите вечер вкусно"
    rec_ses = Item.query.filter(Item.time_day == ses.id)
    rec_id = []
    for i in rec_ses:
        rec_id.append(i.photo)
    a, b = tuple(sample(rec_id, 2))
    return a, b, h5


def AILoveCat(id):
    love = Client.query.get(id)
    ses = Category.query.filter(Category.id == love.categorya).first()
    if ses is None:
        al = Category.query.order_by(Category.id).all()
        i = []
        for j in al:
            i.append(j.id)
        #ses = choice(i)
        ses = 2
        rec_ses = Item.query.filter(Item.category == ses)
    else:
        rec_ses = Item.query.filter(Item.category == ses.id)
    rec_id = []
    for i in rec_ses:
        rec_id.append(i.photo)
    a, b = tuple(sample(rec_id, 2))
    h5 = "То, что вам понравится"
    return a, b, h5


def Analyz_for_rec():
    #Фильтр для анализа и нахождения популярного блюда за последние два дня
    #filter_2_day = datetime.datetime.today() - datetime.timedelta(days=7)
    #order_all = Orders.query.filter(Orders.data >= filter_2_day).all()
    order_all = Orders.query.order_by(Orders.id).all()
    orders_old = []
    orders = []
    client = set()
    for i in order_all:
        orders_old.append([i.loginID, json.loads(i.orderlist)])
        orders.append([i.loginID, {}])
        client.add(i.loginID)
    for j in range(len(orders_old)):
        for k in orders_old[j][1]:
            orders[j][1][int(k)] = orders_old[j][1][k]
    count_client = len(client)
    item_all = Item.query.order_by(Item.id).all()
    dishes = {}
    for i in item_all:
        dishes[i.id] = [i.name, i.category]
    return orders, count_client, dishes


def maxdictkey(dictD):
    return max(dictD, key=dictD.get)


def recomendation(pid, noworder, orders, count_client, dishes):
    countID = {}
    countpidID = {}
    # инициализируем 0 все блюда
    for dishid in dishes.keys():
        countID[dishid] = 0
        countpidID[dishid] = 0
        # print(dish[0])
    # считаем популярность всех блюд, за исключением тех которые уже в заказе
    for order in orders:
        for i in order[1].keys():
            if i not in noworder.keys():
                countID[i] += order[1][i]
    # считаем популярность всех блюд именно этого клиента, за исключением тех которые уже в заказе
    for order in orders:
        if order[0] == pid:
            for i in order[1].keys():
                if i not in noworder.keys():
                    countpidID[i] += order[1][i]
    #print("Количество заказов", countID)
    maxdish = max(countID, key=countID.get)
    maxpiddish = max(countpidID, key=countpidID.get)
    #print("Больше всего заказываемое блюдо", maxdish)
    #print("Любимое блюдо пользователя, за исплючением тех, которые уже есть в заказе", maxpiddish)
    # вычисляем коэффициент
    pols = 1 * (countID[maxdish] / count_client)
    piddish = 1.2 * countpidID[maxpiddish]
    #print("Коэффициент клиента: ", piddish, " Коэффициент остальных: ", pols)
    return maxdictkey({maxdish: pols, maxpiddish: piddish})


#Набор заказов для получения рекомендаций на основе собранной корзины, длина списка может быть любой, но он должен быть один
set_order = ['2', '8']


def issubset_check(set_cat):
    if set(set_order).issubset(set_cat):
        return False
    elif set_cat.issubset(set_order):
        return True
    else:
        flag = False
        for i in set_order:
            if set(i).issubset(set_cat):
                flag = True
                break
        return flag


def dop_order(set_cat):
    recomend_cat = []
    is_sub = []
    for i in set_order:
        if set(i).issubset(set_cat):
            is_sub.append(i)
    for i in set_order:
        if i not in is_sub:
            recomend_cat.append(i)
    random_id = []
    for i in recomend_cat:
        dop_rec_items = Item.query.filter(Item.category == i)
        for k in dop_rec_items:
            random_id.append(k.id)
    dop_rec_i = choice(random_id)
    return dop_rec_i


@app.route('/logout/')
@login_required
def logout():
    for key in list(session.keys()):
        session.pop(key)
    logout_user()
    return redirect('/')


@app.route('/')
def index():
    if current_user:
        redirect('/menu')
    items = Item.query.order_by(Item.id).all()
    slide_1 = AISeason()
    slide_2 = AIDay()
    slide_3 = 0
    return render_template('index.html', data=items, s1=slide_1, s2=slide_2, s3=slide_3)


@app.route('/admin')
@login_required
def admin_index():
    items = Item.query.order_by(Item.id).all()
    return render_template('index_admin.html', data=items)


@app.route('/kitchen/order')
@login_required
def kitchen_order():
    data = str(datetime.datetime.now().date())
    orders_act = Orders.query.filter(Orders.data == data, Orders.status == 'Готовится')
    order_items_act = []
    for order_id in orders_act:
        arr = json.loads(order_id.orderlist)
        ord = []
        for pos in arr:
            pos = int(pos)
            item = Item.query.get(pos)
            ord.append([item.name, arr[str(pos)]])
        order_items_act.append(ord)
    orders_old = Orders.query.filter(Orders.data == data, Orders.status == 'Получен')
    order_items_old = []
    for order_id in orders_old:
        arr = json.loads(order_id.orderlist)
        ord = []
        for pos in arr:
            pos = int(pos)
            item = Item.query.get(pos)
            ord.append([item.name, arr[str(pos)]])
        order_items_old.append(ord)

    return render_template('kitchen_order.html', orders=order_items_act, orders_old=order_items_old)


@app.route('/admin/<int:id>/delete')
def admin_delete(id):
    item = Item.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return redirect('/admin')
    except:
        return "При удалении блюда произошла ошибка"


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


@app.route('/create', methods=['POST', 'GET'])
def create():
    categoryes = Category.query.order_by(Category.id).all()
    season = Season.query.order_by(Season.id).all()
    time_day = Time_day.query.order_by(Time_day.id).all()
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
        return render_template('create.html', categoryes=categoryes, season=season, time_day=time_day)


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
    categoryes = Category.query.order_by(Category.id).all()
    if request.method == "POST":
        name_client = request.form['name_client']
        login = request.form['login']
        email = request.form['email']
        telephone = request.form['telephone']
        categorya = request.form['categorya']
        #allergy = request.form['allergy']
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
        client = Client(name_client=name_client, login=login, password_hash=password_hash, email=email, telephone=telephone, categorya=categorya)
        try:
            db.session.add(client)
            db.session.commit()
            return redirect('/login')
        except:
            message_error = Markup('Возникла ошибка! Проверьте, все ли поля заполнены')
            connection.close()
            return render_template('sign.html', message_error=message_error)
    else:
        return render_template('sign.html', categoryes=categoryes)


@app.route('/menu', methods=['GET','POST'])
@login_required
def menu():
    log = current_user.login
    client = Client.query.filter(Client.login == log).first()
    id = client.id
    items = Item.query.order_by(Item.id).all()
    slide_1 = AISeason()
    slide_2 = AIDay()
    slide_3 = AILoveCat(id)
    if not session.get('status'):
        session['status'] = 'В ожидании заказа'
    if request.method == "POST":

        dishID_list = request.form.getlist('dishID')
        # если корзина ещё не создана
        if not session.get('order'):
            session['order'] = ''
            orderlist = {}
        else:
            orderl = session['order']
            orderlist = json.loads(orderl)
        # добавляем инфу о товаре в список
        for i in dishID_list:
            if i not in orderlist:
                orderlist[i] = 1
            else:
                orderlist[i] += 1
        order_cur = json.dumps(orderlist)
        session['order'] = order_cur
        return redirect('/cart')

    else:
        return render_template('index.html', data=items, s1=slide_1, s2=slide_2, s3=slide_3)


@app.route('/cart/delete')
def delete_cart():
    # если корзина ещё не создана
    if not session.get('order'):
        redirect('/menu')
    session.pop('order', None)
    session.pop('flag', None)
    session.pop('dop_id', None)
    return redirect('/menu')


@app.route('/cart', methods=['GET','POST'])
@login_required
def cart():
    orderl = session['order']
    orderlist = json.loads(orderl)
    connection = sqlite3.connect('base_menu.db')
    # connection = sqlite3.connect('///home/viikoshh/diplom-by-viikoshh/base_menu.db')
    cur = connection.cursor()
    order_items = list()
    for i in orderlist.keys():
        cur.execute("SELECT id,name,photo, price FROM item WHERE id='" + str(int(i)) + "'")
        sp = cur.fetchall()
        current_order = [*sp, orderlist[i], sp[0][-1]]
        order_items.append(current_order)
    order_id = {}
    orders = []
    for i in range(len(order_items)):
        if order_items[i][0][0] not in order_id:
            # order_id.add(order_items[i][0][0]);
            order_id[order_items[i][0][0]] = order_items[i][1]
            orders.append(order_items[i])
        else:
            for j in orders:
                if j == order_items[i]:
                    j[1] += order_items[i][1]
                    order_id[order_items[i][0][0]] = j[1]
        order_items[i][2] = order_items[i][1] * order_items[i][0][3]
    order_items = orders.copy()

    orders_all, count_client_all, items_all = Analyz_for_rec()
    id_rec = recomendation(current_user.login, order_id, orders_all, count_client_all, items_all)
    item_rec = Item.query.get(id_rec)

    #if not session.get('flag'):
    #    session['flag'] = False

    #if not session.get('dop_id'):
    #    session['dop_id'] = 8
    #if session['flag'] == False:
    #if flag == False:
    dop_rec = 0
    set_cat = set()
    for i in order_id.keys():
        print(order_id)
        item = Item.query.get(int(i))
        set_cat.add(item.category)
    flag = issubset_check(set_cat)
    if len(order_id) == 0:
        flag = False
    if flag == True:
        dop_rec_i = dop_order(set_cat)
        dop = Item.query.get(dop_rec_i)
        dop_id = dop.id
        dop_name = dop.name
        dop_photo = dop.photo
        dop_price = dop.price
        dop_rec = [dop_name, dop_photo]
        dop_item = [[dop_id, dop_name, dop_photo, dop_price], 1, dop_price]
        session['dop_id'] = dop_id
    #session['flag'] = True
    #else:
    #    dop_id = session['dop_id']
    #    order_id[dop_id] = 1
    #    dop = Item.query.get(dop_id)
    #    dop_name = dop.name
    #    dop_photo = dop.photo
    #    dop_price = dop.price
    #    dop_rec = [dop_name, dop_photo]
    #    dop_item = [[dop_id, dop_name, dop_photo, dop_price], 1, dop_price]
    #    flag = True



    order_cur = json.dumps(order_id)
    session['order'] = order_cur
    len_order = len(order_items)
    # print(session['order'])
    if request.method == "POST":
        if request.form['sub_cart'] == 'Вернуться к меню':
            count = request.form.getlist('count')
            empt = []
            for i in range(len(order_items)):
                c = int(count[i])
                if c > 0:
                    order_items[i][1] = c
                    order_items[i][2] = c * order_items[i][0][3]
                    order_id[order_items[i][0][0]] = order_items[i][1]
                else:
                    empt.append(order_items[i])
            for i in empt:
                order_items.remove(i)
                order_id.pop(i[0][0], 100)
            order_cur = json.dumps(order_id)
            session['order'] = order_cur
            return redirect('/menu')
        elif request.form['sub_cart'] == 'Очистить корзину':
            count = request.form.getlist('count')
            empt = []
            for i in range(len(order_items)):
                c = int(count[i])
                if c > 0:
                    order_items[i][1] = c
                    order_items[i][2] = c * order_items[i][0][3]
                    order_id[order_items[i][0][0]] = order_items[i][1]
                else:
                    empt.append(order_items[i])
            for i in empt:
                order_items.remove(i)
                order_id.pop(i[0][0], 100)
            order_cur = json.dumps(order_id)
            session['order'] = order_cur
            return redirect('/cart/delete')
        elif request.form['sub_cart'] == 'Подтвердить заказ':
            count = request.form.getlist('count')
            empt = []
            for i in range(len(order_items)):
                c = int(count[i])
                if c > 0:
                    order_items[i][1] = c
                    order_items[i][2] = c * order_items[i][0][3]
                    order_id[order_items[i][0][0]] = order_items[i][1]
                else:
                    empt.append(order_items[i])
            for i in empt:
                order_items.remove(i)
                order_id.pop(i[0][0], 100)
            order_cur = json.dumps(order_id)
            session['order'] = order_cur
            return redirect('/confirm_order')
        elif request.form['sub_cart'] == 'Добавить':

            count = request.form.getlist('count')
            empt = []
            for i in range(len(order_items)):
                c = int(count[i])
                if c > 0:
                    order_items[i][1] = c
                    order_items[i][2] = c * order_items[i][0][3]
                    order_id[order_items[i][0][0]] = order_items[i][1]
                else:
                    empt.append(order_items[i])
            for i in empt:
                order_items.remove(i)
                order_id.pop(i[0][0], 100)
            item = [[item_rec.id, item_rec.name, item_rec.photo, item_rec.price], 1, item_rec.price]
            order_id[item_rec.id] = 1
            order_items.append(item)
            order_cur = json.dumps(order_id)
            session['order'] = order_cur
            orders_all, count_client_all, items_all = Analyz_for_rec()
            id_rec = recomendation(current_user.login, order_id, orders_all, count_client_all, items_all)
            item_rec = Item.query.get(id_rec)





            return render_template('cart.html', order=order_items, len_order=len_order, recomend=item_rec, dop_rec=dop_rec, flag=flag)
        elif request.form['sub_cart'] == 'Добавить доп':
            dop_id = session['dop_id']
            dop = Item.query.get(dop_id)
            dop_name = dop.name
            dop_photo = dop.photo
            dop_price = dop.price
            dop_item = [[dop_id, dop_name, dop_photo, dop_price], 1, dop_price]
            count = request.form.getlist('count')
            empt = []
            for i in range(len(order_items)):
                c = int(count[i])
                if c > 0:
                    order_items[i][1] = c
                    order_items[i][2] = c * order_items[i][0][3]
                    order_id[order_items[i][0][0]] = order_items[i][1]
                else:
                    empt.append(order_items[i])
            for i in empt:
                order_items.remove(i)
                order_id.pop(i[0][0], 100)


            order_id[dop_id] = 1
            order_items.append(dop_item)
            order_cur = json.dumps(order_id)
            session['order'] = order_cur
            dop_rec = 0
            flag = 'False'
            id_rec = recomendation(current_user.login, order_id, orders_all, count_client_all, items_all)
            item_rec = Item.query.get(id_rec)
            #session[flag] = flag


            return render_template('cart.html', order=order_items, len_order=len_order, recomend=item_rec, dop_rec=dop_rec, flag=flag)

    return render_template('cart.html', order=order_items, len_order=len_order, recomend=item_rec, dop_rec=dop_rec, flag=flag)


@app.route('/confirm_order', methods=['GET','POST'])
@login_required
def confirm():
    orderlist = json.loads(session['order'])
    order_items = []
    cost = 0
    for i in orderlist:
        item = Item.query.get(i)
        order_items.append([item.name, orderlist[i], item.price * orderlist[i]])
        cost += item.price * orderlist[i]
    return render_template("confirm_order.html", order_items=order_items, cost=cost)


@app.route('/pay', methods=['GET','POST'])
@login_required
def pay():
    if request.method == "POST":
        loginID = current_user.login
        orderlist = session['order']
        status = 'Готовится'
        session['status'] = status
        data = str(datetime.datetime.now().date())
        if not session.get('data'):
            session['data'] = 0
        session['data'] = data
        order = Orders(loginID=loginID, orderlist=orderlist, status=status, data=data)

        session.pop('order', None)
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
        session['status'] = 'Получен'
        order_cur.status = 'Получен'
        session.pop('data', None)
        session.pop('status', None)
        try:
            db.session.commit()
            return redirect('/logout')
        except:
            return render_template('order.html')



    return render_template('order.html')


### Роботы
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