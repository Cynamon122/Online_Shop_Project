import secrets
import stripe

from flask import render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user

from shop import app, db, bcrypt
from .forms import CustomerRegisterForm, CustomerLoginFrom
from .models import Register
from ..admin.models import CustomerOrder
from ..products.models import Brand, Category


@app.route('/customer/register', methods=['GET', 'POST'])
def customer_register():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    form = CustomerRegisterForm()
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = Register(name=form.name.data,
                            username=form.username.data,
                            email=form.email.data,
                            password=hash_password,
                            country=form.country.data,
                            city=form.city.data,
                            contact=form.contact.data,
                            address=form.address.data,
                            zipcode=form.zipcode.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data} Thank you for registering', 'success')
        db.session.commit()
        return redirect(url_for('customer_login'))
    return render_template('customer/register.html', form=form, brands=brands, categories=categories)


@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    form = CustomerLoginFrom()
    if form.validate_on_submit():
        user = Register.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('You are login now!', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash('Incorrect email or password', 'danger')
        return redirect(url_for('customer_login'))
    return render_template('/customer/login.html', form=form, brands=brands, categories=categories)


@app.route('/customer/logout')
def customer_logout():
    logout_user()
    return redirect(url_for('customer_login'))


@app.route('/get_order')
@login_required
def get_order():

    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = CustomerOrder(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            session.pop('Shoppingcart')
            flash('Your order has been sent successfully', 'success')
            return redirect(url_for('orders', invoice=invoice))

        except Exception as e:
            print(e)
            flash("Something went wrong", "danger")
            return redirect(url_for('getcart'))


@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    if current_user.is_authenticated:
        grand_total = 0
        sub_total = 0
        customer_id = current_user.id
        customer = Register.query.filter_by(id=customer_id).first()
        orders = CustomerOrder.query.filter_by(customer_id=customer_id).order_by(CustomerOrder.id.desc()).first()
        for _key, product in orders.orders.items():
            discount = (product['discount'] / 100) * float(product['price'])
            sub_total += float(product['price']) * int(product['quantity'])
            sub_total -= discount
            grand_total = ("%.2f" % float(sub_total))
    else:
        return redirect(url_for('customer_login'))
    return render_template('customer/order.html', invoice=invoice, sub_total=sub_total, grand_total=grand_total,
                           customer=customer, orders=orders, brands=brands, categories=categories)
