from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///base_menu.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# id  name  photo  price   weight  dop_info


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

    def __repr__(self):
        return


@app.route('/')
def index():
    items = Item.query.order_by(Item.id).all()
    return render_template('index.html', data=items)


@app.route('/login')
def login():
    return render_template('login.html')


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

        item = Item(name=name, photo=photo, price=price, weight=weight, composition=composition, KBJU=KBJU, discover_text=discover_text, discover_url=discover_url)

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