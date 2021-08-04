import qrcode
import os
from flask import render_template, redirect, url_for, flash, request, abort
from dynamic_qr import app, db
from dynamic_qr.forms import RegistrationForm, LoginForm, QRForm
from dynamic_qr.models import User, QRCode
from flask_login import login_user, current_user, logout_user, login_required


def generate_qr(filename):
    """
    Creates a QR Code based on an intermediary url
    The QR image will be stored in static/qr/<filename>
    Filepath will be stored inside of the database
    """
    url = "https://qr.royalhaskoningdhv.com/qr/{}".format(filename)

    qr = qrcode.QRCode(
        version=1,
        box_size=10,
        border=5)
    qr.add_data(url)
    qr.make(fit=True)

    picture_name = '{}.png'.format(filename)
    picture_path = os.path.join(app.root_path, 'static/qr_codes', picture_name)
    img = qr.make_image(fill='black', back_color='white')
    img.save(picture_path)
    return picture_name


@login_required
@app.route('/')
@app.route('/home', methods=['GET', 'POST'])
def home():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = QRForm()
    if form.validate_on_submit():
        if QRCode.query.filter_by(filename='{}.png'.format(
                form.filename.data)).first():
            flash('Name already exists!')
            return redirect(url_for('home'))
        path = generate_qr(form.filename.data)
        uid = current_user.id
        new_code = QRCode(filename=path,
                          endpoint=form.endpoint.data,
                          user_id=uid)
        db.session.add(new_code)
        db.session.commit()
        flash('Your QR code has been generated and added to your account!')
        return redirect(url_for('account'))
    legend = "Create a dynamic QR Code"
    return render_template("home.html", title='Home', form=form, legend=legend)


@login_required
@app.route('/account')
def account():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    page = request.args.get('page', type=int)
    user = User.query.filter_by(username=current_user.username).first_or_404()
    pagination = user.qr.paginate(page=page, per_page=25)
    qr_codes = pagination.items
    return render_template('account.html', title='Account',
                           pagination=pagination, qr_codes=qr_codes)


@login_required
@app.route('/qr/<int:id>/update', methods=['GET', 'POST'])
def edit(id):
    qr = QRCode.query.get_or_404(id)
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if qr.author != current_user:
        abort(403)
    form = QRForm()
    if form.validate_on_submit():
        qr.endpoint = form.endpoint.data
        db.session.add(qr)
        db.session.commit()
        flash('Your QR code has been generated and added to your account!')
        return redirect(url_for('account'))
    elif request.method == "GET":
        form.filename.data = os.path.splitext(qr.filename)[0]
        form.endpoint.data = qr.endpoint
    legend = "Edit your dynamic QR Code endpoint"
    return render_template("home.html", title='Home', form=form, legend=legend)


@login_required
@app.route('/qr/<int:id>/delete', methods=['GET', 'POST'])
def delete(id):
    qr = QRCode.query.get_or_404(id)
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    if qr.author != current_user:
        abort(403)
    db.session.delete(qr)
    db.session.commit()
    picture_path = os.path.join(app.root_path, 'static/qr_codes', qr.filename)
    os.remove(picture_path)
    flash('Your QR Code has been deleted!', 'success')
    return redirect(url_for('account'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user)
        return redirect(url_for('home'))
    return render_template('login.html', title='Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/qr/<filename>')
def redirect_qr(filename):
    fname = str(filename) + ".png"
    url = QRCode.query.filter_by(filename=fname).first()
    return redirect(url.haul_away())
