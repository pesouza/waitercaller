#!/usr/local/environments/flask/lib/python3.6
import datetime

from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for

from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_mail import Mail, Message
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


app = Flask(__name__)
app.secret_key = "Gxf613UhGRkzAKd47R5daLrUelnlUL4L6AU4z0uu++TNBpdzhAolufHqPQiiEdn34pbE97bmXbN"
login_manager = LoginManager(app)

mail = Mail(app)

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = config.email
app.config["MAIL_PASSWORD"] = config.pwd

DB = DBHelper()
PH = PasswordHelper()
BH = BitlyHelper()
QH = QrcodeHelper()

def generate_confirmation_token():
    return str(uuid.uuid4().hex)

def send_confirmation_email(email, token):
    msg = Message(
        "Confirme seu endereço de e-mail",
        sender = config.email,
        recipients=[email],        
        html=render_template("confirm_email.html", 
                            confirm_url=f'{config.base_url}/confirm/{token}'),
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
        new_url = BH.shorten_url(config.base_url + "/newrequest/" + str(tableid))
        new_qrc = QH.gen_code(form.tablenumber.data, new_url)
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
        image = 'images/ok.png'
    else:
        message = "Por favor, seja paciente. Você será atendido o mais rápido possível!"
        background_color = "red"
        sound = 'sounds/again.wav'
        image = 'images/again.png'

    return render_template("request.html", message=message, 
                            background_color=background_color,
                            sound=sound, image=image)


if __name__ == '__main__':
    app.run(debug=True)
