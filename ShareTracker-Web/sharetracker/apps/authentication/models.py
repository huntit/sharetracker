# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from flask_login import UserMixin

from apps import db, login_manager

from apps.authentication.util import hash_pass

from flask import current_app as app

import os, csv

from sqlalchemy.orm import relationship


class Users(db.Model, UserMixin):

    __tablename__ = 'Users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    email = db.Column(db.String(64), unique=True)
    password = db.Column(db.LargeBinary)
    children = relationship("Portfolio")

    def __init__(self, **kwargs):
        for property, value in kwargs.items():
            # depending on whether value is an iterable or not, we must
            # unpack it's value (when **kwargs is request.form, some values
            # will be a 1-element list)
            if hasattr(value, '__iter__') and not isinstance(value, str):
                # the ,= unpack of a singleton fails PEP8 (travis flake8 test)
                value = value[0]

            if property == 'password':
                value = hash_pass(value)  # we need bytes here (not plain str)

            setattr(self, property, value)

    def __repr__(self):
        return str(self.username)


@login_manager.user_loader
def user_loader(id):
    return Users.query.filter_by(id=id).first()


@login_manager.request_loader
def request_loader(request):
    username = request.form.get('username')
    user = Users.query.filter_by(username=username).first()
    return user if user else None


class Portfolio(db.Model):
    __tablename__ = 'Portfolio'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=False)
    name = db.Column(db.String(256), unique=False, nullable=True)
    notes = db.Column(db.Text, unique=False, nullable=True)
    children = relationship("Portfolio_Stock")

    # constructor
    def __init__(self, user_id, name, notes):
        self.user_id = user_id
        self.name = name
        self.notes = notes

    def __repr__(self):
        return f"Portfolio(user_id = {self.user_id}, name = {self.name}, notes = {self.notes})"

class Portfolio_Stock(db.Model):
    __tablename__ = 'Portfolio_Stock'
    id = db.Column(db.Integer, primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey('Portfolio.id'), nullable=False)
    stock_code = db.Column(db.String(6), db.ForeignKey('Stock.code'), nullable=False)
    units = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, unique=False, nullable=True)
    children = relationship("Stock")

    def __repr__(self):
        return f"Portfolio_Stock(portfolio_id = {self.portfolio_id}, stock_code = {self.stock_code}, units = {self.units}, notes = {self.notes})"


class Stock(db.Model):
    __tablename__ = 'Stock'
    code = db.Column(db.String(6), primary_key=True)
    short_name = db.Column(db.String(256), unique=False)
    last = db.Column(db.Numeric(10, 3))

    def __repr__(self):
        return f"Stock(code = {self.code}, short_name = {self.short_name}, last = {self.last})"

# This function runs on table creation, to pre-populate data from a static CSV file
@db.event.listens_for(Stock.__table__, 'after_create')
def create_stocks(*args, **kwargs):

    # Pre-populate stock data by importing from a Metastock CSV file
    # Example of CSV:
    # ANZ, 220801, 22.8, 22.8, 22.42, 22.74, 7611230
    filename = f'{app.root_path}/static/ASXEQUITIESMetastock.txt'
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for index, row in enumerate(csv_reader):
          app.logger.info(row)
          db.session.add(Stock(code=row[0], short_name='', last=row[5]))

    db.session.commit()


