from flask_wtf import Form
from wtforms import PasswordField
from wtforms import SubmitField
from wtforms.fields import EmailField
from wtforms import StringField
from wtforms import validators


class RegistrationForm(Form):
    place = StringField('place', validators=[validators.DataRequired()])
    email = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    password = PasswordField('password', validators=[validators.DataRequired(), 
                              validators.Length(min=8, message="Use uma senha com pelo menos 8 caracteres")])
    password2 = PasswordField('password2', validators=[validators.DataRequired(), 
                               validators.EqualTo('password', message='As senhas precisam ser iguais')])
    submit = SubmitField('submit', [validators.DataRequired()])


class LoginForm(Form):
    loginemail = EmailField('email', validators=[validators.DataRequired(), validators.Email()])
    loginpassword = PasswordField('password', validators=[validators.DataRequired(message="A senha é requerida")])
    submit = SubmitField('submit', [validators.DataRequired()]) 


class CreateTableForm(Form):
    tablenumber = StringField('tablenumber', validators=[validators.DataRequired()])
    submit = SubmitField('createtablesubmit', validators=[validators.DataRequired()])

class ContactForm(Form):
    name = StringField(label='Nome', validators=[validators.DataRequired()])
    email = StringField(label='E-mail', validators=[
      validators.DataRequired(), validators.Email(granular_message=True)])
    message= StringField(label='Mensagem', validators=[validators.DataRequired()])
    submit = SubmitField(label="Enviar")
