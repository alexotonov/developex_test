from app import db
from app.models import Token
from flask import render_template, url_for
from datetime import datetime


def validate_token(token: Token, check_activation: bool = True):
    is_valid = False
    template = None

    if token is None:
        template = render_template('fail.html', message='Invalid token', url=url_for('card'))
    elif (datetime.utcnow() - token.time).seconds > 5 * 60:
        db.session.delete(token)
        db.session.commit()
        template = render_template('fail.html', message='Token lifetime expired', url=url_for('card'))
    elif check_activation and not token.active:
        template = render_template('fail.html', message='Enter token activation\'s code',
                                   url=url_for('pin', token_hex=token.hex))
    else:
        is_valid = True

    return is_valid, template
