import os
import secrets

from flask import redirect, render_template, url_for, flash, request, session, current_app
from flask_login import login_required, current_user

from shop import db, app, photos, search
from .forms import Addproducts
from .models import Brand, Category, Addproduct
from ..admin.models import CustomerOrder
from ..customers.models import Register


@app.route('/products')
@login_required
def products():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    products = Addproduct.query.all()
    return render_template('admin/products.html', title="Admin Page", products=products, brands=brands,
                           categories=categories)


@app.route('/all_orders')
@login_required
def all_orders():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))

    orders = CustomerOrder.query.order_by(CustomerOrder.date_created.desc()).join(Register, CustomerOrder.customer_id
                                                                                  == Register.id).all()
    products = Addproduct.query.all()

    return render_template('admin/all_orders.html', title="Admin Page", products=products, brands=brands,
                           orders=orders)


@app.route('/products/<int:id>')
def single_page(id):
    product = Addproduct.query.get_or_404(id)
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('products/single_page.html', title="Single Product Page", product=product, brands=brands,
                           categories=categories)


@app.route('/addproduct', methods=['GET', 'POST'])
@login_required
def addproduct():
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    form = Addproducts(request.form)
    brands = Brand.query.all()
    categories = Category.query.all()
    if request.method == "POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        addproduct = Addproduct(name=name, price=price, discount=discount, stock=stock, colors=colors,
                                description=description, category_id=category, brand_id=brand, image_1=image_1,
                                image_2=image_2, image_3=image_3)

        db.session.add(addproduct)
        flash(f'The product {name} was added in database', 'success')
        db.session.commit()

        return redirect(url_for('products'))

    return render_template('products/addproduct.html', form=form, title='Add a Product', brands=brands,
                           categories=categories)


@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
@login_required
def updateproduct(id):
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    form = Addproducts(request.form)
    brands = Brand.query.all()
    categories = Category.query.all()
    updateproduct = Addproduct.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')

    # zmiana danych w bazie danych:
    if request.method == "POST":
        updateproduct.name = form.name.data
        updateproduct.price = form.price.data
        updateproduct.discount = form.discount.data
        updateproduct.stock = form.stock.data
        updateproduct.colors = form.colors.data
        updateproduct.description = form.description.data
        updateproduct.brand_id = brand
        updateproduct.category_id = category
        flash(f'The product {updateproduct.name} was updated', 'success')

        # usuwanie aktualnie zapisanego zdjęcia produktu i zapisywanie nowego
        # jeśli nie możemy znaleźć starego zdjęcia poprostu je zapisujemy w ramach exept
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + updateproduct.image_1))
                updateproduct.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                updateproduct.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + updateproduct.image_2))
                updateproduct.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                updateproduct.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + updateproduct.image_3))
                updateproduct.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                updateproduct.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        db.session.commit()

        return redirect(url_for('products'))

    # formsy które wyświetlają aktualny stan wpisany do bazy danych:
    form.name.data = updateproduct.name
    form.price.data = updateproduct.price
    form.discount.data = updateproduct.discount
    form.stock.data = updateproduct.stock
    form.colors.data = updateproduct.colors
    form.description.data = updateproduct.description

    return render_template('products/updateproduct.html', form=form, title='Update Product', brands=brands,
                           categories=categories, updateproduct=updateproduct)


@app.route('/deleteproduct/<int:id>', methods=["POST"])
@login_required
def deleteproduct(id):
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    product = Addproduct.query.get_or_404(id)
    if request.method == 'POST':
        # usuwamy zdjęcia
        try:
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
            os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
        except Exception as error:
            print(error)

        # usuwamy produkt
        db.session.delete(product)
        db.session.commit()
        flash(f'The product {product.name} has been deleted', 'success')
        return redirect(url_for('products'))


@app.route('/brands')
@login_required
def brands():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brands.html', title="Brands Page", brands=brands, categories=categories)


@app.route('/brand/<int:id>')
def get_brand(id):
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    page = request.args.get('page', 1, type=int)

    # zapobiega błędowi przy paginate dla kategorii
    get_brand = Brand.query.filter_by(id=id).first_or_404()

    get_brand_products = Addproduct.query.filter_by(brand=get_brand).paginate(page=page, per_page=8)
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/home.html', title='Home Page', get_brand_products=get_brand_products, brands=brands,
                           categories=categories, get_brand=get_brand)


@app.route('/addbrand', methods=['GET', 'POST'])
@login_required
# dodawanie nowyh branów
def addbrand():
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    # getbrand za pomocą forms pobiera nowy brand, następnie jest jest przypisywany do Brand(z models.py)
    # oraz dodawany do bazy danych
    if request.method == "POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The brand {getbrand} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addbrand'))

    return render_template('products/addbrand.html', categories=categories, brands=brands)


@app.route('/addcategory', methods=['GET', 'POST'])
@login_required
def addcategory():
    categories = Category.query.order_by(Category.id.desc()).all()
    brands = Brand.query.order_by(Brand.id.desc()).all()
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    if request.method == "POST":
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        flash(f'The category {getcategory} was added to your database', 'success')
        db.session.commit()
        return redirect(url_for('addcategory'))

    return render_template('products/addcategory.html', categories=categories, brands=brands)


@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
@login_required
def updatebrand(id):
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == 'POST':
        updatebrand.name = brand
        flash(f'The brand has been updated', 'success')
        db.session.commit()
        return redirect(url_for('brands'))
    return render_template('products/updatebrand.html', title='Update Brand Page', updatebrand=updatebrand,
                           brands=brands, categories=categories)


@app.route('/deletebrand/<int:id>', methods=['POST'])
@login_required
def deletebrand(id):
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    brand = Brand.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(brand)
        db.session.commit()
        flash(f'The brand {brand.name} has been deleted', 'success')
        return redirect(url_for('brands'))


@app.route('/categories')
@login_required
def categories():
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    categories = Category.query.order_by(Category.id.desc()).all()
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/categories.html', title="Categories Page", categories=categories, brands=brands)


@app.route('/categories/<int:id>')
def get_category(id):
    page = request.args.get('page', 1, type=int)

    # zapobiega błędowi przy paginate dla kategorii
    get_category = Category.query.filter_by(id=id).first_or_404()

    get_category_products = Addproduct.query.filter_by(category=get_category).paginate(page=page, per_page=8)
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/home.html', title='Home Page', get_category_products=get_category_products,
                           categories=categories, brands=brands, get_category=get_category)


@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
@login_required
def updatecategory(id):
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == 'POST':
        updatecategory.name = category
        flash(f'The category has been updated', 'success')
        db.session.commit()
        return redirect(url_for('categories'))
    return render_template('products/updatebrand.html', title='Update Categories Page', updatecategory=updatecategory,
                           brands=brands, categories=categories)


@app.route('/deletecategory/<int:id>', methods=['POST'])
@login_required
def deletecategory(id):
    if current_user.type != 'Admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('home'))
    category = Category.query.get_or_404(id)
    if request.method == 'POST':
        db.session.delete(category)
        db.session.commit()
        flash(f'The category {category.name} has been deleted', 'success')
        return redirect(url_for('categories'))


@app.route('/search')
def search():
    searchword = request.args.get('q')
    products = Addproduct.query.msearch(searchword, fields=['name', 'description'])
    brands = Brand.query.order_by(Brand.id.desc()).all()
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('products/search.html', products=products, brands=brands, categories=categories)
