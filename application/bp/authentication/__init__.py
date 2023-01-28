from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, current_user, logout_user

from application.database import User, db, Profile, Group
from application.bp.authentication.forms import RegisterForm, LoginForm, ProfileForm, GroupForm

authentication = Blueprint('authentication', __name__, template_folder='templates')


@authentication.route('/users')
def users():
    user_records = User.all()
    return render_template('users.html', users=user_records)


@authentication.route('/dashboard')
@login_required
def dashboard():
    user_records = User.all()
    return render_template('dashboard.html')


@authentication.route('/users/<user_id>')
def user_by_id(user_id):
    user = User.find_by_id(user_id)
    return render_template('user.html', user=user)


@authentication.route('/groups/new', methods=['GET', 'POST'])
@login_required
def group():
    form = GroupForm()
    if form.validate_on_submit():
        group = Group(form.title.data)
        group.save()
        return redirect(url_for('authentication.groups', page='1'))

    return render_template('group_form.html', form=form)


@authentication.route('/groups/list/<int:page>', methods=['GET', 'POST'])
@login_required
def groups(page):
    page = page
    per_page = 1000
    pagination = Group.query.paginate(page=page, per_page=per_page, error_out=False)
    data = pagination.items
    return render_template('groups.html', data=data, Model=Group, pagination=pagination)


@authentication.route('/groups/<group_id>/delete', methods=['POST', 'GET'])
@login_required
def group_delete(group_id):
    group = Group.find_by_id(group_id)
    group.delete()
    return redirect(url_for('authentication.groups', page='1'))


@authentication.route('/groups/<group_id>/edit', methods=['POST', 'GET'])
@login_required
def group_edit(group_id):
    group = Group.find_by_id(group_id)
    form = GroupForm(obj=group)
    if form.validate_on_submit():
        group.title = form.title.data
        group.save()
        return redirect(url_for('authentication.groups', page='1'))

    return render_template('group_form.html', form=form)


@authentication.route('/groups/<group_id>', methods=['POST', 'GET'])
@login_required
def group_view(group_id):
    group = Group.find_by_id(group_id)
    return render_template('group.html', data=group)


@authentication.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User.find_user_by_email(form.email.data)
        if user is None:
            user = User(form.email.data, form.password.data)
            user.save()
            return redirect(url_for('authentication.login'))
        else:
            flash('Already Registered')
    return render_template('registration.html', form=form)


@authentication.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if form.validate_on_submit():
        profile = Profile(form.first_name.data, form.last_name.data, form.phone.data)
        current_user.profile = profile
        current_user.save()

    return render_template('profile.html', form=form)


@authentication.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.find_user_by_email(form.email.data)
        if user is None:
            flash('User Not Found')
        elif user.check_password(form.password.data):
            flash('Welcome')
            user.authenticated = True
            user.save()
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page or url_for('authentication.dashboard'))
        else:
            flash('Password Incorrect')
    return render_template('login.html', form=form)


@authentication.route('/logout')
@login_required
def logout():
    current_user.authenticated = False
    current_user.save()
    logout_user()
    flash('You have been logged out')
    return redirect(url_for('homepage.homepage'))
