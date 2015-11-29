from flask import render_template, redirect, url_for
from flask import request, jsonify, abort
from sqlalchemy import exc
from flask_restful import Api
import wtforms
from checkouts import app, db
import forms
from models import User, Asset, Checkout
import utils

@app.route('/', methods=['GET'])
def index():
    """
    Route path.  Redirects to the checkouts endpoint.

    @path '/'
    """
    return redirect(url_for('checkouts_list'))

@app.route('/checkouts', methods=['GET'])
def checkouts_list():
    """
    Lists the checkouts based on the given query parameters and page.

    @path '/checkouts'
    @query 'page'
    @query 'returned'
    """
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1

    returned = request.args.get('returned', False)
    try:
        returned = bool(returned)
    except ValueError:
        returned = False

    query = None
    if returned:
        query = Checkout.query.filter(Checkout.checkin_time != None)
    else:
        query = Checkout.query.filter(Checkout.checkin_time == None)

    sorted_query = query.order_by(Checkout.checkin_time.asc())
    obj = sorted_query.paginate(page, 20, False)
    return render_template('checkouts.jinja2', obj=obj, returned=returned)

@app.route('/checkouts/new', methods=['GET', 'POST'])
def checkouts_select_user():
    """
    Selects the user for whom the checkout is being made.

    @path '/checkouts/new'
    """
    form = forms.UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        form.populate_obj(user)
        user.save()
        return redirect(url_for('checkouts_select_asset', _id=user._id))

    return render_template('checkout.jinja2', user=None, form=form)

@app.route('/checkouts/<int:_id>/new', methods=['GET', 'POST'])
def checkouts_select_asset(_id):
    """
    Selects the asset for the user that is being checked out.

    @path '/checkouts/:id/new'
    @param 'id'
    """
    users = User.query.filter_by(_id=_id)
    if users.count() == 0:
        abort(404)

    form = forms.AssetForm(request.form)
    user = users[0]
    if request.method == 'POST' and form.validate():
        asset = Asset()
        form.populate_obj(asset)
        asset.save()
        return redirect(url_for('checkouts_checkout',
                                user_id=user._id,
                                asset_id=asset._id))

    return render_template('checkout.jinja2', user=user, form=form)

@app.route('/checkouts/<int:user_id>/new/<int:asset_id>', methods=['GET'])
def checkouts_checkout(user_id, asset_id):
    """
    Checkouts out the specified asset to the specified user.

    @path '/checkouts/:user_id/new/:asset_id'
    @param 'user_id'
    @param 'asset_id'
    """
    users = User.query.filter_by(_id=user_id)
    if users.count() == 0:
        abort(404)

    assets = Asset.query.filter_by(_id=asset_id)
    if assets.count() == 0:
        abort(404)

    asset = assets[0]
    if asset.stock == 0:
        asset.total += 1
        asset.save()

    checkout = Checkout()
    checkout.user_id = user_id
    checkout.asset_id = asset_id
    checkout.save()

    return redirect(url_for('checkouts_list'))

@app.route('/checkouts/<int:_id>/remove', methods=['GET', 'POST'])
def checkouts_remove(_id):
    """
    Deletes an existing checkout.

    @path '/checkouts/:id/remove'
    @param 'id'
    """
    checkouts = Checkout.query.filter_by(_id=_id)
    if checkouts.count() == 0:
        abort(404)

    checkout = checkouts[0]
    checkout.delete()
    return redirect(url_for('checkouts_list'))

@app.route('/checkouts/<int:_id>/checkin', methods=['GET'])
def checkouts_checkin(_id):
    """
    Check-in an item.

    @path '/checkouts/:id/checkin'
    @param 'id'
    """
    checkouts = Checkout.query.filter_by(_id=_id)
    if checkouts.count() == 0:
        abort(404)

    checkout = checkouts[0]
    checkout.checkin_time = utils.current_time()
    checkout.save()
    return redirect(url_for('checkouts_list'))

@app.route('/users', methods=['GET'])
def users_list():
    """
    Lists the users.  Can query based on name an identifier or name.

    @path '/users'
    @query 'page'
    @query 'name'
    """
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1

    name = request.args.get('name', '')
    query = User.query.filter(User.name.contains(name) |
                              User.identifier.contains(name) |
                              User.first_name.contains(name))
    sorted_query = query.order_by(User.identifier.asc())
    obj = sorted_query.paginate(page, 20, False)
    return render_template('users.jinja2', obj=obj, name=name)

@app.route('/users/new', methods=['GET', 'POST'])
def users_add():
    """
    Creates a new user and saves it.  The new user must be unique with
    respect to a combination of their identifier and name.

    @path '/users/new'
    """
    form = forms.UserForm(request.form)
    if request.method == 'POST' and form.validate():
        user = User()
        form.populate_obj(user)
        user.save()
        return redirect(url_for('users_list'))
    return render_template('user.jinja2', form=form, created=True)

@app.route('/users/<int:_id>/remove', methods=['GET'])
def users_remove(_id):
    """
    Deletes an existing user.

    @path '/users/:id/remove'
    @param 'id'
    """
    users = User.query.filter_by(_id=_id)
    if users.count() == 0:
        abort(404)

    user = users[0]
    user.delete()
    return redirect(url_for('users_list'))

@app.route('/users/<int:_id>/update', methods=['GET', 'POST'])
def users_update(_id):
    """
    Updates an existing user.

    @path '/usets/:id/update'
    @param 'id'
    """
    users = User.query.filter_by(_id=_id)
    if users.count() == 0:
        abort(404)

    user = users[0]
    form = forms.UserForm(request.form)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(user)
            user.save()
            return redirect(url_for('users_list'))
    else:
        form = forms.UserForm(created=False,
                              identifier=user.identifier,
                              name=user.name,
                              first_name=user.first_name,
                              last_name=user.last_name,
                              refunded=user.refunded,
                              membership=user.membership.code)
    return render_template('user.jinja2', form=form, pk=user._id)

@app.route('/users/<int:_id>/profile', methods=['GET'])
def user_profile(_id):
    """
    Shows the profile for a specific user.

    @path '/users/:id/profile'
    @param 'id'
    @query 'page'
    """
    users = User.query.filter_by(_id=_id)
    if users.count() == 0:
        abort(404)

    user = users[0]
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1

    query = Checkout.query.filter_by(user_id=_id)
    sorted_query = query.order_by(Checkout.checkin_time.desc())
    obj = sorted_query.paginate(page, 20, False)
    return render_template('profile.jinja2', user=users[0], obj=obj)

@app.route('/assets', methods=['GET'])
def assets_list():
    """
    Lists the assets.  Can query based on name of the asset.

    @path '/assets'
    @query 'page'
    @query 'name'
    """
    page = request.args.get('page', 1)
    try:
        page = int(page)
    except ValueError:
        page = 1

    name = request.args.get('name', '')
    filtered = Asset.query.filter(Asset.name.contains(name))
    obj = filtered.paginate(page, 20, False)
    return render_template('assets.jinja2', obj=obj)

@app.route('/assets/new', methods=['GET', 'POST'])
def assets_add():
    """
    Creates a new asset and saves it.  The new asset must have a unique
    name.

    @path '/assets/new'
    """
    form = forms.AssetForm(request.form)
    if request.method == 'POST' and form.validate():
        asset = Asset()
        form.populate_obj(asset)
        asset.save()
        return redirect(url_for('assets_list'))
    return render_template('asset.jinja2', form=form, created=True)

@app.route('/assets/<int:_id>/remove', methods=['GET'])
def assets_remove(_id):
    """
    Deletes an existing asset.

    @path '/assets/:id/remove'
    @param 'id'
    """
    assets = Asset.query.filter_by(_id=_id)
    if assets.count() == 0:
        abort(404)

    asset = assets[0]
    asset.delete()
    return redirect(url_for('assets_list'))

@app.route('/assets/<int:_id>/update', methods=['GET', 'POST'])
def assets_update(_id):
    """
    Updates an existing asset.

    @path '/assets/:id/update'
    @param 'id'
    """
    assets = Asset.query.filter_by(_id=_id)
    if assets.count() == 0:
        abort(404)

    asset = assets[0]
    form = forms.AssetForm(request.form)
    if request.method == 'POST':
        if form.validate():
            form.populate_obj(asset)
            asset.save()
            return redirect(url_for('assets_list'))
    else:
        form = forms.AssetForm(name=asset.name,
                               asset_type=asset.asset_type.code,
                               total=asset.total,
                               created=False)
    return render_template('asset.jinja2', form=form, pk=asset._id)

@app.route('/search', methods=['GET'])
def search():
    """
    Search endpoint.  Used to query for suggestions for possible assets
    and users.  Returns a JSON object representing an array of resources
    where each resource contains a name and a unique id.

    @path '/search'
    @query 'q'
    @query 'resource' ['assets', 'users']
    """
    query = request.args.get('q', '')
    resource = request.args.get('resource', '')
    items = []
    if resource == 'assets':
        items = Asset.query.filter(Asset.name.contains(query)).limit(10)
        items = map(lambda i: { 'name': i.name, '_id': i._id }, items)
    elif resource == 'users':
        fmt = lambda i: '%s - %s' % (i.full_name, i.identifier)
        items = User.query.filter(User.name.contains(query) |
                                  User.identifier.contains(query) |
                                  User.first_name.contains(query))
        items = items.limit(10)
        items = map(lambda i: { 'name': fmt(i), '_id': i._id }, items)
    return jsonify(items=items)

@app.errorhandler(400)
@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(503)
def error_handler(error):
    """
    Returns the view to display errors.
    """
    return render_template('error.jinja2', error=error)
