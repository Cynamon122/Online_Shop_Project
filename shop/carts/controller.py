from flask import redirect, request, session, render_template, url_for

from shop import app
from shop.products.controller import brands, categories
from shop.products.models import Addproduct, Brand, Category


def mager_dicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False


# dodawanie do koszyka
@app.route('/addcart', methods=["POST"])
def addcart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        colors = request.form.get('colors')
        product = Addproduct.query.filter_by(id=product_id).first()

        if product_id and quantity and colors and request.method == "POST":
            # przekazujemy do nowego dictonary
            dict_item = {product_id: {'name': product.name, 'price': product.price, 'discount': product.discount,
                                      'colors': product.colors, 'quantity': quantity, 'image': product.image_1, }}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    print("success")
                else:
                    session['Shoppingcart'] = mager_dicts(session['Shoppingcart'], dict_item)
                    return redirect(request.referrer)
            else:
                session['Shoppingcart'] = dict_item
                return redirect(request.referrer)

    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@app.route('/carts')
def getcart():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    products = Addproduct.query.all()
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    total = 0
    for key, product in session['Shoppingcart'].items():
        discount = (product['discount'] / 100) * float(product['price'])
        total += float(product['price']) * int(product['quantity'])
        total -= discount
    return render_template('products/carts.html', total=total, brands=brands, categories=categories, products=products)


@app.route('/deleteitem/<int:id>')
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('getcart'))
    except Exception as e:
        print(e)
        return redirect(url_for('getcart'))


@app.route('/clear_cart')
def clear_cart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)
