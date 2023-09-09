import stripe
from flask import render_template, session, request, redirect, url_for, flash
from flask_login import current_user, login_required

from shop import app, db, bcrypt
from .forms import RegistrationForm, LoginForm

from shop.products.models import Addproduct, Brand, Category
from .models import CustomerOrder


@app.route('/')
def home():

    page = request.args.get('page', 1, type=int)
    products = Addproduct.query.filter(Addproduct.stock > 0).paginate(page=page, per_page=8)

    # brands oraz categories pozwala na wyswietlanie ich w navabar
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()

    return render_template('admin/home.html', title='Home Page', products=products, brands=brands,
                           categories=categories)


publishable_key = 'pk_test_51No8F9H3gzECPArcbQhH8ciWsngkL5njOSYU23y4wr30x0vpuKGbX0DApGfRx2VWnwqo5xpU6G79qZf7tZ48IGIg00aQ2ra0hG'
stripe.api_key = 'sk_test_51No8F9H3gzECPArcMPuSI2s6JW0gBysPHtOVLRvZznYpynk1WOcN0LOYf4RJUD77DgHV7uupSCzX4SAC1nbdOlHU00H8jutYZu'


@app.route('/payment', methods=['POST'])
@login_required
def payment():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    invoice = request.form.get('invoice')
    amount = request.form.get('amount')
    customer = stripe.Customer.create(
        email=request.form['stripeEmail'],
        source=request.form['stripeToken'],
    )
    charge = stripe.Charge.create(
        customer=customer.id,
        description='Myshop',
        amount=amount,
        currency='pln',
    )
    order = CustomerOrder.query.filter_by(customer_id=current_user.id, invoice=invoice).first()
    if order:
        order.status = 'Paid'
        db.session.commit()
    else:
        flash('Nie znaleziono zamówienia o podanym numerze faktury.', 'danger')

    return redirect(url_for('home'))