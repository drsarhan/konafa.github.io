from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, ApiKeys
from binance_api import BinanceClient

app = Flask(__name__)
app.config.from_object('config')
db.init_app(app)

@app.before_first_request
def create_tables():
    db.create_all()
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        admin_user = User(username='admin', password=generate_password_hash('admin'))
        db.session.add(admin_user)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            if username == 'admin':
                return redirect(url_for('admin'))
            return redirect(url_for('main'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        if 'create_user' in request.form:
            new_username = request.form['new_username']
            new_password = request.form['new_password']
            user = User(username=new_username, password=generate_password_hash(new_password))
            db.session.add(user)
            db.session.commit()
        elif 'change_password' in request.form:
            user = User.query.get(session['user_id'])
            new_password = request.form['new_password']
            user.password = generate_password_hash(new_password)
            db.session.commit()
        elif 'save_api_keys' in request.form:
            api_key = request.form['api_key']
            secret_key = request.form['secret_key']
            api_keys = ApiKeys.query.filter_by(user_id=session['user_id']).first()
            if not api_keys:
                api_keys = ApiKeys(user_id=session['user_id'], api_key=api_key, secret_key=secret_key)
                db.session.add(api_keys)
            else:
                api_keys.api_key = api_key
                api_keys.secret_key = secret_key
            db.session.commit()
    return render_template('admin.html')

@app.route('/main', methods=['GET', 'POST'])
def main():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user = User.query.get(session['user_id'])
    api_keys = ApiKeys.query.filter_by(user_id=user.id).first()
    binance_client = BinanceClient(api_keys.api_key, api_keys.secret_key)
    balance = binance_client.get_balance()
    symbols = binance_client.get_available_symbols()
    if request.method == 'POST':
        if 'get_balance' in request.form:
            balance = binance_client.get_balance()
        elif 'buy' in request.form:
            symbol = request.form['buy_symbol']
            quantity = request.form['buy_quantity']
            binance_client.buy(symbol, quantity)
        elif 'sell' in request.form:
            symbol = request.form['sell_symbol']
            quantity = request.form['sell_quantity']
            binance_client.sell(symbol, quantity)
    return render_template('main.html', balance=balance, symbols=symbols)

if __name__ == '__main__':
    app.run(debug=True)