# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from apps.home import blueprint
from flask import render_template, redirect, request, url_for
from flask_login import login_required, current_user
from jinja2 import TemplateNotFound
from apps.authentication.models import Portfolio, Portfolio_Stock, Stock
from apps import db
from collections import namedtuple

@blueprint.route('/index')
@login_required
def index():

    return render_template('home/index.html', segment='index')

@blueprint.route('/add_portfolio', methods=['POST'])
@login_required
def add_portfolio():
    if request.method == 'POST':
        name = request.form['portfolio_name']
        notes = request.form['portfolio_notes']
        new_portfolio = Portfolio(current_user.id, name, notes)
        db.session.add(new_portfolio)
        db.session.commit()
        return redirect('/portfolio.html')


@blueprint.route('/<template>')
@login_required
def route_template(template):

    try:

        if not template.endswith('.html'):
            template += '.html'

        # Detect the current page
        segment = get_segment(request)

        if segment == 'portfolio.html':
            # https://stackoverflow.com/questions/17972020/how-to-execute-raw-sql-in-flask-sqlalchemy-app
            # SELECT * FROM Portfolio INNER JOIN Portfolio_Stock ON Portfolio.id == Portfolio_Stock.portfolio_id
            # INNER JOIN Stock ON Portfolio_Stock.stock_code == Stock.code WHERE Portfolio.user_id == 1
            result = db.session.execute("""SELECT Portfolio.id, Portfolio.name, stock.code, stock.short_name, 
                                           portfolio_stock.units, stock. last FROM Portfolio 
                                           INNER JOIN Portfolio_Stock ON Portfolio.id == Portfolio_Stock.portfolio_id
                                           INNER JOIN Stock ON Portfolio_Stock.stock_code == Stock.code 
                                           WHERE Portfolio.user_id = :val"""
                                        , {'val': current_user.id})
            # Convert results to a named tuple
            Record = namedtuple('Record', result.keys())
            records = [Record(*r) for r in result.fetchall()]
            # for r in records:
            #     print(r.id, r.name, r.code, r.short_name, r.units, r.last)
            #     print(r)
            portfolio = records
            portfolio_value = sum([(i.units * i.last) for i in portfolio])  # calc total value of the portfolio
            portfolio_name = portfolio[0].name
            print(portfolio_name)
            return render_template("home/" + template, segment=segment, portfolio=portfolio, portfolio_value=portfolio_value)

        # Serve the file (if exists) from app/templates/home/FILE.html
        return render_template("home/" + template, segment=segment)

    except TemplateNotFound:
        return render_template('home/page-404.html'), 404

    except:
        return render_template('home/page-500.html'), 500


# Helper - Extract current page name from request
def get_segment(request):

    try:

        segment = request.path.split('/')[-1]

        if segment == '':
            segment = 'index'

        return segment

    except:
        return None
