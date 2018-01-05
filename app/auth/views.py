from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, ResetPasswordRequestForm, \
                            ResetPasswordForm, ChangeEmailForm
from . import auth
from .. import db
from ..email import send_email


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('Invalid username or password.')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('main.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data)
        db.session.add(user)
        # db.session.commit()  有 SQLALCHEMY_COMMIT_ON_TEARDOWN = True，所以这里可以不添加commit，会自动处理。
        # 但这里因为要提前赋予新用户的id，所以先提交过去。
        db.session.commit()
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        flash('You have confirmed your account. Thanks!')
    else:
        flash('The confirmation link is invalid or has expired.')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    if current_user.is_authenticated and not current_user.confirmed and request.endpoint[:5] != 'auth.' \
                                                                            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():  # 这个不需要邮箱验证，所以直接在这里就可以处理。有些比较重要的比如重置密码，更换邮箱，这个需要发到邮箱去验证。
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been updated.')
            return redirect(url_for('main.index'))
        flash('Your old password is error.')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        u = User.query.filter_by(email=form.email.data).first()
        if u is None:
            flash('Email is error.')
        else:
            token = u.generate_reset_token()
            flash('A confirmation email has been sent to you by email.')
            send_email(u.email, 'Confrim Your Account',
                       'auth/email/reset_password_request', user=u, token=token)
            return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)  # 和reset_password可以使用同一份模板，为了方便。


@auth.route('/reset_password/<string:token>', methods=['GET', 'POST'])
def reset_password(token):   # 先调用get请求之后，下一次form.validate_on_submit():进去的时候，token还在？！
    form = ResetPasswordForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            db.session.commit()
            flash('your password has been reset.')
            return redirect(url_for('auth.login'))
        else:
            flash('your password reset failure.')
            return redirect(url_for('main.index'))

    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email_request')
@login_required
def change_email_request():
    token = current_user.generate_confirmation_token()
    flash('A confirmation email has been sent to you by email.')
    send_email(current_user.email, 'Confrim Your Account',
               'auth/email/change_email_request', user=current_user, token=token)
    return redirect(url_for('main.index'))


@auth.route('/change_email/<string:token>', methods=['GET', 'POST'])
@login_required
def change_email(token):
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.change_email(token, form.email.data):
            db.session.commit()
            flash('your email has been changed.')
            logout_user()
            return redirect(url_for('auth.login'))
        else:
            flash('your email change failure.')
            return redirect(url_for('main.index'))
    return render_template('auth/change_email.html', form=form)
