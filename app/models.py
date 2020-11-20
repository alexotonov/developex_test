from app import db
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash


class Card(db.Model):
    __tablename__ = 'card'
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.BigInteger, unique=True)
    pin_code_hash = db.Column(db.String(128))
    amount = db.Column(db.Float)
    tries = db.Column(db.SmallInteger, default=0)
    active = db.Column(db.Boolean, default=True)
    history = relationship('History')

    def __init__(self, number: int, pin_code: int, amount: float = 0.0):
        self.number = number
        self.set_pin_code(str(pin_code))
        self.amount = amount

    def check_pin_code(self, pin_code: str):
        return check_password_hash(self.pin_code_hash, pin_code)

    def set_pin_code(self, code):
        self.pin_code_hash = generate_password_hash(code)

    def add_history(self, operation_code: str, data: dict = None):
        record = History(self.id, operation_code)
        if data is not None:
            record.data = data
        db.session.add(record)
        db.session.commit()


class History(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    card_id = db.Column(db.Integer, ForeignKey('card.id'))
    operation_code = db.Column(db.SmallInteger)
    data = db.Column(db.JSON)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, card_id: int, code: str):
        self.card_id = card_id
        self.code = code


class Operation(db.Model):
    __tablename__ = 'operation'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(10))
    description = db.Column(db.String(120))

    def __init__(self, code: str, description: str):
        self.code = code
        self.description = description


class Token(db.Model):
    __tablename__ = 'token'
    id = db.Column(db.Integer, primary_key=True)
    hex = db.Column(db.String(128), index=True)
    card_id = db.Column(db.Integer)
    active = db.Column(db.Boolean, default=False)
    time = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, hex: str, card_id: int):
        self.hex = hex
        self.card_id = card_id

    def get_card(self):
        return Card.query.get(self.card_id)
