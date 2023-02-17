#!/usr/local/envs/flask/lib/python3.10
import datetime
import os
import stripe
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for, jsonify

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_mail import Mail, Message
from time import time
import uuid

import config
if config.test:
    from mockdbhelper import MockDBHelper as DBHelper
else:
    from dbhelper import DBHelper

from passwordhelper import PasswordHelper
from bitlyhelper import BitlyHelper
from qrcodehelper import QrcodeHelper
from user import User

from forms import RegistrationForm
from forms import LoginForm
from forms import CreateTableForm
from forms import ContactForm


app = Flask(__name__)
app.secret_key = "Gxf613UhGRkzAKd47R5daLrUelnlUL4L6AU4z0uu++TNBpdzhAolufHqPQiiEdn34pbE97bmXbN"
login_manager = LoginManager(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 465 #587
app.config["MAIL_USE_TLS"] = False #True
app.config['MAIL_USE_SSL'] = True
app.config["MAIL_USERNAME"] = config.email
app.config["MAIL_PASSWORD"] = config.pwd

mail = Mail(app)

""" stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
}
"""
 
stripe_keys = {
    "secret_key": config.STRIPE_SECRET_KEY,
    "publishable_key": config.STRIPE_PUBLISHABLE_KEY,
    "price_id": config.STRIPE_PRICE_ID,
}

stripe.api_key = stripe_keys["secret_key"]

DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()
QH = QrcodeHelper()



def generate_confirmation_token():
    return str(uuid.uuid4().hex)

def send_confirmation_email(email, token):
    msg = Message(
        "Confirme seu endereço de e-mail",
        sender = ('Paulo Souza', config.email),
        recipients=[email],        
        html=render_template("confirm_email.html", 
                            confirm_url=f'{config.base_url}confirm/{token}'),
    )
    mail.send(msg)

def send_contact_email(name, email, msg):
    msg = Message(
        f"Contado de {name}",
        sender = (name, email),
        recipients = [config.email],        
        body = msg
    )
    mail.send(msg)

@login_manager.user_loader
def load_user(user_id):
    user_password = DB.get_user(user_id)
    if user_password:
        return User(user_id)


@app.route("/login", methods=["POST"])
def login():
    form = LoginForm(request.form)
    if form.validate():
        stored_user = DB.get_user(form.loginemail.data)
        if stored_user and PH.validate_password(form.loginpassword.data, stored_user['salt'], stored_user['hashed']) and stored_user['confirmed']:
            user = User(form.loginemail.data)
            login_user(user, remember=True)
            return redirect(url_for('account'))
        form.loginemail.errors.append("E-mail ou senha inválido")
    return render_template("home.html", loginform=form, registrationform=RegistrationForm())


@app.route("/register", methods=["POST"])
def register():
    form = RegistrationForm(request.form)
    if form.validate():
        if DB.get_user(form.email.data):
            form.email.errors.append("Endereço de e-mail já registrado")
            return render_template("home.html", loginform=LoginForm(), registrationform=form)

        """ customer = stripe.Customer.create(
            email=request.form['email'],
            source=request.form['stripe_token']
        ) """

        salt = PH.get_salt()
        hashed = PH.get_hash(form.password2.data + salt)
        token = generate_confirmation_token()
        DB.add_user(str(form.place.data), form.email.data, salt, hashed, token)

        send_confirmation_email(form.email.data, token)

        return render_template("home.html", loginform=LoginForm(), registrationform=form, onloadmessage="Registro bem sucedido! Verifique sua caixa postal.")
    return render_template("home.html", loginform=LoginForm(), registrationform=form)

@app.route("/confirm/<token>")
def confirm_email(token):
    if DB.confirm_email(token):
        return "Seu email foi confirmado!"
    else:
        return "Token inválido!"

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/")
def home():
    return render_template("home.html", loginform=LoginForm(), registrationform=RegistrationForm())


@app.route("/dashboard")
@login_required
def dashboard():
    now = datetime.datetime.now()
    requests = DB.get_requests(current_user.get_id())
    for req in requests:
        deltaseconds = (now - req['time']).seconds
        req['wait_minutes'] = "{}.{}".format((deltaseconds//60), str(deltaseconds % 60).zfill(2))
    return render_template("dashboard.html", requests=requests)


@app.route("/dashboard/resolve")
@login_required
def dashboard_resolve():
    request_id = request.args.get("request_id")
    DB.delete_request(request_id)
    return redirect(url_for('dashboard'))


@app.route("/account")
@login_required
def account():
    tables = DB.get_tables(current_user.get_id())
    user = DB.get_user(current_user.email)
    return render_template("account.html", 
                            createtableform=CreateTableForm(), 
                            tables=tables,
                            user = user)


@app.route("/account/createtable", methods=["POST"])
@login_required
def account_createtable():
    form = CreateTableForm(request.form)
    if form.validate():
        tableid = DB.add_table(form.tablenumber.data, current_user.get_id())
        long_url = f'{config.base_url}/newrequest/{tableid}'
        new_url = BH.shorten_url(long_url)
        new_qrc = QH.gen_code(form.tablenumber.data, new_url, long_url, tableid)
        if new_url is None:
            new_url = long_url
        DB.update_table(tableid, new_url, new_qrc)
        return redirect(url_for('account'))
    return render_template("account.html", createtableform=form, tables=DB.get_tables(current_user.get_id()))


@app.route("/account/deletetable")
@login_required
def account_deletetable():
    tableid = request.args.get("tableid")
    DB.delete_table(tableid)
    return redirect(url_for('account'))


@app.route("/newrequest/<tid>")
def new_request(tid):
    if DB.add_request(tid, datetime.datetime.now()):
        message = "Seu garçom está a caminho!"
        background_color = "green"
        sound = 'sounds/ok.wav'
        image = 'site/ok.png'
    else:
        message = "Por favor, seja paciente. Você será atendido o mais rápido possível!"
        background_color = "red"
        sound = 'sounds/again.wav'
        image = 'site/again.png'

    return render_template("request.html", message=message, 
                            background_color=background_color,
                            sound=sound, image=image)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm(request.form)
    if form.validate():

        send_contact_email(form.name.data, form.email.data, form.message.data)

        return render_template("contact.html", form=ContactForm(), 
                                onloadmessage="Agradecemos o seu contato. Responderemos ASAP.")
    return render_template("contact.html", form=ContactForm(request.form))

@app.route("/privacidade")
def privacidade():
    return render_template("privacidade.html")

@app.route("/termos")
def termos():
    return render_template("termos.html")

@app.route('/webhook', methods=['POST'])
def webhook():
    event = None
    payload = request.data
    sig_header = request.headers['STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        raise e
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        raise e

    # Handle the event
    
    # Handle the event
    if event['type'] == 'checkout.session.async_payment_failed':
      session = event['data']['object']
    elif event['type'] == 'checkout.session.async_payment_succeeded':
      session = event['data']['object']
    elif event['type'] == 'checkout.session.completed':
      session = event['data']['object']
    elif event['type'] == 'checkout.session.expired':
      session = event['data']['object']
    elif event['type'] == 'customer.created':
      customer = event['data']['object']
    elif event['type'] == 'customer.deleted':
      customer = event['data']['object']
    elif event['type'] == 'customer.updated':
      customer = event['data']['object']
    elif event['type'] == 'customer.subscription.created':
      subscription = event['data']['object']
    elif event['type'] == 'customer.subscription.deleted':
      subscription = event['data']['object']
    elif event['type'] == 'customer.subscription.paused':
      subscription = event['data']['object']
    elif event['type'] == 'customer.subscription.resumed':
      subscription = event['data']['object']
    elif event['type'] == 'customer.subscription.trial_will_end':
      subscription = event['data']['object']
    elif event['type'] == 'customer.subscription.updated':
      subscription = event['data']['object']
    elif event['type'] == 'person.created':
      person = event['data']['object']
    elif event['type'] == 'person.deleted':
      person = event['data']['object']
    elif event['type'] == 'person.updated':
      person = event['data']['object']
    # ... handle other event types
    else:
      print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)


if __name__ == '__main__':
    app.run()
