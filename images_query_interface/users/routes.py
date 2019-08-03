from flask import (render_template, url_for, flash,
                redirect, request, send_file, Blueprint)
from flask_login import (login_user, current_user,
                    logout_user, login_required)
from images_query_interface.forms import RegistrationForm, LoginForm, QueryForm
from images_query_interface import db, bcrypt
from images_query_interface.models import User
from images_query_interface.users.utils import send_verification_email
from images_query_interface.images.utils import dict_query2list_images
from images_query_interface.common_utils import ( list_images2list_filepaths,
                        dict_attributes, real_valued_attributes, form_attributes)
import time
users = Blueprint('users', __name__)
 


@users.route("/register", methods=['GET', 'POST'])
def register():
    return render_template('register_temp.html')
    # if current_user.is_authenticated:
    #     return redirect(url_for('main.home'))
    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
    #     send_verification_email(form.username.data, form.email.data, hashed_password)
    #     flash('You can login after database admin will verify your account', 'success')
    #     return redirect(url_for('users.login'))
    # return render_template('register.html', title='Register', form=form)

@login_required
@users.route("/account", methods=['GET', 'POST'])
def account():
    if current_user.history is not None:
        list_hist = eval(current_user.history)
    else:
        list_hist = []
    return render_template('account.html', title='Account',
     list_hist=list_hist, form_attributes=form_attributes, dict_attributes=dict_attributes)

@login_required
@users.route("/history/<string:str_dict_query>", methods=['GET', 'POST'])
def history(str_dict_query):

    time_start = time.time()

    dict_query = eval(str_dict_query)
    list_images = dict_query2list_images(dict_query)

    list_filepaths = list_images2list_filepaths(list_images)
    str_list_filepaths = str(list_filepaths)
    str_list_filepaths = (str_list_filepaths).replace('/','*')
    
    n_matches = len(list_images)

    time_end = time.time()
    execution_time = time_end-time_start

    return render_template('display_result.html', title='Results', dict_query=dict_query, form_attributes=form_attributes,
    list_attributes = dict_attributes.keys(), dict_attributes=dict_attributes, list_images = list_images,  
    str_list_filepaths = str_list_filepaths,execution_time=execution_time, n_matches=n_matches)


@users.route("/verify_token/<token>", methods=['GET', 'POST'])
def verify_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    account_info_dict = verify_token(token)
    if account_info_dict is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.register'))
    
    this_username = account_info_dict['username']
    this_email = account_info_dict['email']
    this_password = account_info_dict['password']
    this_user = User(username=this_user, email=this_email, password=this_password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('users.login'))



@users.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@users.route("/logout")
def logout(): 
    logout_user()
    return redirect(url_for('main.home'))

