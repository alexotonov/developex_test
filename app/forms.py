from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired


class CardForm(FlaskForm):
    number = StringField('Card number', validators=[DataRequired()])


class PinForm(FlaskForm):
    pin = PasswordField('Code', validators=[DataRequired()])


class OptionsForm(FlaskForm):
    balance = SubmitField('Balance')
    cash = SubmitField('Money withdrawal')
    ext = SubmitField('Exit')


class BalanceForm(FlaskForm):
    back = SubmitField('Back')
    ext = SubmitField('Exit')


class CashForm(FlaskForm):
    amount = StringField('Amount')
    back = SubmitField('Back')
    ext = SubmitField('Exit')


class BillForm(FlaskForm):
    back = SubmitField('Back')
    ext = SubmitField('Exit')


class BackForm(FlaskForm):
    back = SubmitField('Back')
