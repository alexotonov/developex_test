from uuid import uuid4
from datetime import datetime

from flask import render_template, redirect, url_for

from app import app, db
from app.forms import CardForm, PinForm, OptionsForm, BalanceForm, CashForm, BillForm
from app.models import Card, Token
from app.utils import validate_token
from app.operations import Operations


@app.route('/', methods=['GET', 'POST'])
@app.route('/card', methods=['GET', 'POST'])
def card():
    card_form = CardForm()
    if card_form.validate_on_submit():
        number = card_form.number.data.replace('-', '')
        card = Card.query.filter_by(number=number).first()
        if card is None:
            return render_template('fail.html', message='Wrong card number', url=url_for('card'))
        elif not card.active:
            return render_template('fail.html', message='Card is blocked', url=url_for('card'))

        token_hex = uuid4().hex
        token = Token(token_hex, card.id)
        db.session.add(token)
        db.session.commit()
        return redirect(url_for('pin', token_hex=token_hex))

    return render_template('card.html', form=card_form)


@app.route('/<token_hex>/pin', methods=['GET', 'POST'])
def pin(token_hex):
    token = Token.query.filter_by(hex=token_hex).first()

    is_valid, template = validate_token(token, False)
    if not is_valid:
        return template

    card = token.get_card()
    if card is None:
        return render_template('fail.html', message='Invalid card number', url=url_for('card'))
    elif not card.active:
        return render_template('fail.html', message='Card is blocked', url=url_for('card'))

    pin_form = PinForm()
    if pin_form.validate_on_submit():
        if (card is not None
                and card.active
                and card.tries <= 3
                and card.check_pin_code(pin_form.pin.data)):
            card.tries = 0
            token.active = True
            db.session.commit()
            return redirect(url_for('options', token_hex=token_hex))

        if not card.check_pin_code(pin_form.pin.data):
            card.tries += 1
            if card.tries > 3:
                card.active = False
                card.tries = 0
                card.add_history(Operations.blocking)
                db.session.commit()
                message = 'Number of code entry attempts exceeded. Card is blocked'
                return render_template('fail.html', message=message, url=url_for('card'))
            else:
                db.session.commit()
                message = 'Wrong code'
                return render_template('fail.html', message=message, url=url_for('pin', token_hex=token_hex))

    return render_template('pin.html', token_hex=token_hex, form=pin_form)


@app.route('/<token_hex>/options', methods=['GET', 'POST'])
def options(token_hex):
    token = Token.query.filter_by(hex=token_hex).first()

    is_valid, template = validate_token(token)
    if not is_valid:
        return template

    opt_form = OptionsForm()
    if opt_form.validate_on_submit():
        if opt_form.balance.data:
            return redirect(url_for('balance', token_hex=token_hex))
        elif opt_form.cash.data:
            return redirect(url_for('cash', token_hex=token_hex))
        elif opt_form.ext.data:
            return redirect(url_for('card'))
    return render_template('options.html', form=opt_form, token_hex=token_hex)


@app.route('/<token_hex>/balance', methods=['GET', 'POST'])
def balance(token_hex):
    token = Token.query.filter_by(hex=token_hex).first()

    is_valid, template = validate_token(token)
    if not is_valid:
        return template

    balance_form = BalanceForm()
    if balance_form.validate_on_submit():
        if balance_form.back.data:
            return redirect(url_for('options', token_hex=token_hex))
        elif balance_form.ext.data:
            return redirect(url_for('card'))

    card = token.get_card()
    if card is None:
        return render_template('fail.html', message='Invalid card',
                               url=url_for('balance', token_hex=token_hex))

    card.add_history(Operations.balance)
    return render_template('balance.html', form=balance_form, balance=card.amount, number=card.number,
                           token_hex=token_hex, date=datetime.utcnow().strftime('%d.%m.%Y'))


@app.route('/<token_hex>/cash', methods=['GET', 'POST'])
def cash(token_hex):
    token = Token.query.filter_by(hex=token_hex).first()

    is_valid, template = validate_token(token)
    if not is_valid:
        return template

    card = token.get_card()
    if card is None:
        return render_template('fail.html', message='Invalid card',
                               url=url_for('cash', token_hex=token_hex))

    cash_form = CashForm()
    if cash_form.validate_on_submit():
        if cash_form.back.data:
            return redirect(url_for('options', token_hex=token_hex))
        elif cash_form.ext.data:
            return redirect(url_for('card'))
        elif cash_form.amount.data and float(cash_form.amount.data) > 0:
            amount = float(cash_form.amount.data)
            if card.amount < amount:
                return render_template('fail.html', message='Not enough money',
                                       url=url_for('cash', token_hex=token_hex))

            card.amount = round(card.amount - amount, 2)
            card.add_history(Operations.withdrawal, {'amount': amount})
            db.session.commit()
            bill_form = BillForm()
            return render_template('bill.html', form=bill_form, card=card, amount=amount,
                                   token_hex=token_hex, date=datetime.utcnow().strftime('%d.%m.%Y'))

    return render_template('cash.html', form=cash_form, balance=card.amount, token_hex=token_hex,
                           date=datetime.utcnow().strftime('%d.%m.%Y'))


@app.route('/<token_hex>/bill', methods=['GET', 'POST'])
def bill(token_hex):
    token = Token.query.filter_by(hex=token_hex).first()

    is_valid, template = validate_token(token)
    if not is_valid:
        return template

    bill_form = BillForm()
    if bill_form.validate_on_submit():
        if bill_form.back.data:
            return redirect(url_for('cash', token_hex=token_hex))
        elif bill_form.ext.data:
            return redirect(url_for('card'))

    return render_template('cash.html', form=bill_form, balance=card.amount, token_hex=token_hex,
                           date=datetime.utcnow().strftime('%d.%m.%Y'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
