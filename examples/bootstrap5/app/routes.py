from flask import render_template, redirect, url_for, flash, session, request
from flask_modals import render_template_modal, response
from email_validator import validate_email, EmailNotValidError

from app import app
from app.utils import login, register, logout
from app.forms import LoginForm, RegistrationForm


@app.route('/')
def index():

    return render_template('index.html')


@app.route('/auth', methods=['GET', 'POST'])
def auth():
    '''This page has 2 modal forms. (For a simpler example, see the
    bootstrap 4 example.) Call `render_template_modal` instead of
    `render_template`. It takes the modal id as an argument apart from
    the arguments passed to `render_template`.
    '''

    form1 = RegistrationForm()
    form2 = LoginForm()
    modal = session.pop('modal', None)

    form = ''
    if 'password2' in request.form:
        form = 'form1'
        modal = 'register-modal'
    elif 'password' in request.form:
        form = 'form2'
        modal = 'login-modal'

    if form == 'form1' and form1.validate_on_submit():
        if register(form1):
            flash(
                'You have registered successfully! Please login.',
                'success'
            )
            return redirect(url_for('auth'))
        else:
            flash('Could not register.', 'danger')
            session['modal'] = 'register-modal'
            return redirect(url_for('auth'))

    if form == 'form2' and form2.validate_on_submit():
        if login(form2.username.data, form2.password.data):
            flash('You have logged in successfully!', 'success')
            session['flag'] = True
            return redirect(url_for('subscribe'))
        else:
            flash('Invalid credentials.', 'danger')
            session['modal'] = 'login-modal'
            return redirect(url_for('auth'))

    return render_template_modal('auth.html', form1=form1, form2=form2,
                                 modal=modal)


@app.route('/subscribe', methods=['GET', 'POST'])
def subscribe():
    '''Example of one modal page redirecting to another modal page.
    `flag` is not required if not redirecting from a modal page (auth).
    '''

    flag = session.pop('flag', False)
    if 'id' not in session:
        flash('You need to be logged in to access the page.', 'info')
        return redirect(url_for('index'))

    name = email = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        if not name:
            flash('Name is required.', 'danger')
        if not email:
            flash('Email is required.', 'danger')
        else:
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError:
                flash('Email is invalid.', 'danger')
            else:
                if name:
                    flash('You have been subscribed!', 'success')
                    return redirect(url_for('feedback'))

    modal = None if flag else 'modal-form'
    return render_template_modal('subscribe.html', modal=modal,
                                 name=name, email=email)


# Example of redirecting to the same page
#
# @app.route('/subscribe', methods=['GET', 'POST'])
# def subscribe():

#     flag = session.pop('flag', False)
#     if 'id' not in session:
#         flash('You need to be logged in to access the page.', 'info')
#         return redirect(url_for('index'))

#     name = email = ''
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         if not name:
#             flash('Name is required.', 'danger')
#         if not email:
#             flash('Email is required.', 'danger')
#         else:
#             try:
#                 valid = validate_email(email)
#                 email = valid.email
#             except EmailNotValidError:
#                 flash('Email is invalid.', 'danger')
#             else:
#                 if name:
#                     flash('You have been subscribed!', 'success')
#                     session['flag'] = True
#                     return redirect(url_for('subscribe'))

#     modal = None if flag else 'modal-form'
#     return render_template_modal('subscribe.html', modal=modal,
#                                  name=name, email=email)

# Example of rendering a template instead of redirecting
#
# @app.route('/subscribe', methods=['GET', 'POST'])
# def subscribe():

#     modal = None
#     if 'id' not in session:
#         flash('You need to be logged in to access the page.', 'info')
#         return redirect(url_for('index'))

#     name = email = ''
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         if not name:
#             flash('Name is required.', 'danger')
#         if not email:
#             flash('Email is required.', 'danger')
#         else:
#             try:
#                 valid = validate_email(email)
#                 email = valid.email
#             except EmailNotValidError:
#                 flash('Email is invalid.', 'danger')
#             else:
#                 if name:
#                     flash('You have been subscribed!', 'success')
#                     return render_template_modal(
#                         'subscribe.html', modal=None,
#                         name=name, email=email
#                     )
#         modal = 'modal-form'

#     return render_template_modal('subscribe.html', modal=modal,
#                                  name=name, email=email)

# Example of rendering a template instead of redirecting - less verbose.
#
# @app.route('/subscribe', methods=['GET', 'POST'])
# @response('subscribe.html')
# def subscribe():

#     modal = None
#     if 'id' not in session:
#         flash('You need to be logged in to access the page.', 'info')
#         return redirect(url_for('index'))

#     name = email = ''
#     if request.method == 'POST':
#         name = request.form['name']
#         email = request.form['email']
#         if not name:
#             flash('Name is required.', 'danger')
#         if not email:
#             flash('Email is required.', 'danger')
#         else:
#             try:
#                 valid = validate_email(email)
#                 email = valid.email
#             except EmailNotValidError:
#                 flash('Email is invalid.', 'danger')
#             else:
#                 if name:
#                     flash('You have been subscribed!', 'success')
#                     return {'modal': None, 'name': name, 'email': email}
#         modal = 'modal-form'

#     return {'modal': modal, 'name': name, 'email': email}


@app.route('/feedback', methods=['GET', 'POST'])
def feedback():

    email = feedback = ''
    if request.method == 'POST':
        email = request.form['email']
        feedback = request.form['feedback']

        if not email:
            flash('Email is required.', 'danger')
        if not feedback:
            flash('Feedback is required.', 'danger')

        if email:
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError:
                flash('Email is invalid.', 'danger')
            else:
                if feedback:
                    flash('Thanks for your feedback!', 'success')
                    return redirect(url_for('feedback'))

    return render_template('feedback.html', email=email, feedback=feedback)


@app.route('/logout')
def logout_user():

    logout()
    return redirect(url_for('index'))
