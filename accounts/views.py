import random
import string
import random
import string
from flask import request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from .models import User, Profile, Campaign, Brand

def generate_random_token(length=10):
    '''Generate a random token consisting of letters and numbers.'''
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))


from flask import abort, render_template, request, redirect, url_for, flash
from flask import Blueprint
from flask_login import (
        current_user,
        login_required,
        login_user,
        logout_user
    )
from accounts import UPLOAD_FOLDER
from accounts.extensions import database as db
from accounts.models import User, Profile
from accounts.forms import (
        CampaignForm, 
        RegisterForm, 
        LoginForm, 
        ForgotPasswordForm,
        ResetPasswordForm,
        ChangePasswordForm,
        ChangeEmailForm,
        EditUserProfileForm
    )
from accounts.utils import (
        unique_security_token,
        remove_existing_file,
        get_unique_filename,
        send_reset_password,
        send_reset_email
    )
from datetime import datetime, timedelta
import re
import os

accounts = Blueprint('accounts', __name__, template_folder='templates')

@accounts.route('/register', methods=['GET', 'POST'], strict_slashes=False)
def register():
    form = RegisterForm()

    if current_user.is_authenticated:
        return redirect(url_for('accounts.index'))

    if form.validate_on_submit():
        username = form.data.get('username')
        first_name = form.data.get('first_name')
        last_name = form.data.get('last_name')
        email = form.data.get('email')
        password = form.data.get('password')
        company_name = form.data.get('company_name')
        sector = form.data.get('sector')
        role = form.data.get('role')
        other_role = form.data.get('other_role')

        try:
            user = User(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                company_name = company_name,
                sector = sector,
                role = role,
                other_role = other_role 
            )
            user.set_password(password)
            user.save()
            user.send_confirmation()
            flash("A confirmation link sent to your email. Please verify your account.", 'info')
            return redirect(url_for('accounts.login'))
        except Exception as e:
            flash("Something went wrong", 'error')
            return redirect(url_for('accounts.register'))

    return render_template('register.html', form=form)

@accounts.route('/login', methods=['GET', 'POST'], strict_slashes=False)
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        return redirect(url_for('accounts.index'))

    if form.validate_on_submit():
        username = form.data.get('username')
        password = form.data.get('password')

        user = User.get_user_by_username(username) or User.get_user_by_email(username)

        if not user:
            flash("User account doesn't exists.", 'error')
        elif not user.check_password(password):
            flash("Your password is incorrect. Please try again.", 'error')
        else:
            if not user.is_active():
                user.send_confirmation()
                flash("Your account is not activate.", 'error')
                return redirect(url_for('accounts.login'))

            login_user(user, remember=True, duration=timedelta(days=15))
            flash("You are logged in successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.login'))

    return render_template('login.html', form=form)


@accounts.route('/account/confirm?token=<string:token>', methods=['GET', 'POST'], strict_slashes=False)
def confirm_account(token=None):
    auth_user = User.query.filter_by(security_token=token).first_or_404()

    if auth_user and not auth_user.is_token_expire():
        if request.method == "POST" and ('submit' and 'csrf_token') in request.form:
            auth_user.active = True
            auth_user.security_token = None
            db.session.commit()
            login_user(auth_user, remember=True, duration=timedelta(days=15))
            flash(f"Welcome {auth_user.username}, You're registered successfully.", 'success')
            return redirect(url_for('accounts.index'))
        return render_template('confirm_account.html', token=token)

    return abort(404)


@accounts.route('/logout', strict_slashes=False)
@login_required
def logout():
    logout_user()
    flash("You're logout successfully.", 'success')
    return redirect(url_for('accounts.login'))


@accounts.route('/forgot/password', methods=['GET', 'POST'], strict_slashes=False)
def forgot_password():
    form = ForgotPasswordForm()

    if form.validate_on_submit():
        email = form.data.get('email')
        user = User.get_user_by_email(email=email)

        if user:
            user.security_token = unique_security_token()
            user.is_send = datetime.now()
            db.session.commit()
            send_reset_password(user)
            flash("A reset password link sent to your email. Please check.", 'success')
            return redirect(url_for('accounts.login'))

        flash("Email address is not registered with us.", 'error')
        return redirect(url_for('accounts.forgot_password'))

    return render_template('forget_password.html', form=form)


@accounts.route('/password/reset/token?<string:token>', methods=['GET', 'POST'], strict_slashes=False)
def reset_password(token=None):
    user = User.query.filter_by(security_token=token).first_or_404()

    if user and not user.is_token_expire():
        form = ResetPasswordForm()

        if form.validate_on_submit():
            password = form.data.get('password')
            confirm_password = form.data.get('confirm_password')

            if not (password == confirm_password):
                flash("Your new password field's not match.", 'error')
            elif not re.match(r"(?=^.{8,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$", password):
                flash("Please choose strong password. It contains at least one alphabet, number, and one special character.", 'warning')
            else:
                user.set_password(password)
                user.security_token = None
                db.session.commit()
                flash("Your password is changed successfully. Please login.", 'success')
                return redirect(url_for('accounts.login'))

            return redirect(url_for('accounts.reset_password', token=token))

        return render_template('reset_password.html', form=form, token=token)

    return abort(404)


@accounts.route('/change/password', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        old_password = form.data.get('old_password')
        new_password = form.data.get('new_password')
        confirm_password = form.data.get('confirm_password')

        user = User.query.get_or_404(current_user.id)
        
        if not user.check_password(old_password):
            flash("Your old password is incorrect.", 'error')
        elif not (new_password == confirm_password):
            flash("Your new password field's not match.", 'error')
        elif not re.match(r"(?=^.{8,}$)(?=.*\d)(?=.*[!@#$%^&*]+)(?![.\n])(?=.*[A-Z])(?=.*[a-z]).*$", new_password):
            flash("Please choose strong password. It contains at least one alphabet, number, and one special character.", 'warning')
        else:
            user.set_password(new_password)
            db.session.commit()
            flash("Your password changed successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.change_password'))
    return render_template('change_password.html', form=form)


@accounts.route('/change/email', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def change_email():
    form = ChangeEmailForm()

    if form.validate_on_submit():
        email = form.data.get('email')

        user = User.query.get_or_404(current_user.id)

        if email == user.email:
            flash("Email is already verified with your account.", 'warning')  
        elif email in [u.email for u in User.query.all() if email != user.email]:
            flash("Email address is already registered with us.", 'warning')  
        else:
            try:
                user.change_email = email
                user.security_token = unique_security_token()
                user.is_send = datetime.now()
                db.session.commit()
                send_reset_email(user=user)
                flash("A reset email link sent to your new email address. Please verify.", 'success')
                return redirect(url_for('accounts.index'))
            except Exception as e:
                flash("Something went wrong.", 'error')
                return redirect(url_for('accounts.change_email'))
            
        return redirect(url_for('accounts.change_email'))

    return render_template('change_email.html', form=form)


@accounts.route('/account/email/confirm?token=<string:token>', methods=['GET', 'POST'], strict_slashes=False)
def confirm_email(token=None):
    user = User.query.filter_by(security_token=token).first_or_404()

    if user and not user.is_token_expire():
        if request.method == "POST" and ('submit' and 'csrf_token') in request.form:
            try:
                user.email = user.change_email
                user.change_email = None
                user.security_token = None
                db.session.commit()
                flash(f"Your email address updated successfully.", 'success')
                return redirect(url_for('accounts.index'))
            except Exception as e:
                flash("Something went wrong", 'error')
                return redirect(url_for('accounts.index'))

        return render_template('confirm_email.html', token=token)

    return abort(404)

@accounts.route('/', strict_slashes=False)
@accounts.route('/home', strict_slashes=False)
@login_required
def index():
    profile = Profile.query.filter_by(user_id=current_user.id).first_or_404()
    return render_template('index.html', profile=profile)


@accounts.route('/profile', methods=['GET', 'POST'], strict_slashes=False)
@login_required
def profile():
    form = EditUserProfileForm()

    user = User.query.get_or_404(current_user.id)
    profile = Profile.query.filter_by(user_id=user.id).first_or_404()

    if form.validate_on_submit():
        username = form.data.get('username')
        first_name = form.data.get('first_name')
        last_name = form.data.get('last_name')
        profile_image = form.data.get('profile_image')
        about = form.data.get('about')

        if username in [user.username for user in User.query.all() if username != current_user.username]:
            flash("Username already exists. Choose another.", 'error')
        else:
            user.username = username
            user.first_name = first_name
            user.last_name = last_name
            profile.bio = about
            if profile_image and not getattr(profile_image, "filename") == "":
                if profile.avator != None or "":
                    path = os.path.join(UPLOAD_FOLDER, profile.avator)
                    remove_existing_file(path=path)
                profile.avator = get_unique_filename(profile_image.filename)
                profile_image.save(os.path.join(UPLOAD_FOLDER, profile.avator))
            db.session.commit()
            flash("Your profile update successfully.", 'success')
            return redirect(url_for('accounts.index'))

        return redirect(url_for('accounts.profile'))
        
    return render_template('profile.html', form=form, profile=profile)



# Campaign Page
@accounts.route('/campaign')
@login_required
def campaign():
    return render_template('campaign.html')



@accounts.route('/start_new_campaign', methods=['GET', 'POST'])
@login_required
def start_new_campaign():
    form = CampaignForm()
    if form.validate_on_submit():
        campaign_id_token = ''.join(random.choices(string.ascii_letters + string.digits, k=10))

        selected_platforms = request.form.getlist('platforms')
        form.platforms.data = ','.join(selected_platforms)

        campaign = Campaign(
            campaign_id=campaign_id_token,
            campaign_name=form.data.get('campaign_name'),
            platforms=form.platforms.data,
            num_brands=form.data.get('num_brands'),
            user_id=current_user.id
        )

        campaign_image = form.image.data
        
        if campaign_image and campaign_image.filename:
            # Assuming the logic for remove_existing_file and get_unique_filename is available elsewhere in your code
            if campaign.image_path:
                path = os.path.join("", campaign.image_path)
                remove_existing_file(path=path)
            
            campaign_image_filename = get_unique_filename(campaign_image.filename)
            image_path = os.path.join(UPLOAD_FOLDER, campaign_image_filename)
            campaign_image.save(image_path)
            campaign.image_path = os.path.join("", campaign_image_filename)

        for i in range(1, form.num_brands.data + 1):
            brand_name = request.form.get(f'brand{i}_name')
            
            if not brand_name:
                flash(f"Brand {i} name is missing!", "danger")
                return redirect(url_for("accounts.start_new_campaign"))

            brand = Brand(name=brand_name, camp_id=campaign.campaign_id)

            # Facebook fields
            brand.facebook_urls = request.form.get(f'brand{i}_facebook_urls')
            brand.facebook_hashtags = request.form.get(f'brand{i}_facebook_hashtags')
            brand.facebook_groups = request.form.get(f'brand{i}_facebook_groups')
            
            # TikTok fields
            brand.tiktok_urls = request.form.get(f'brand{i}_tiktok_urls')
            brand.tiktok_hashtags = request.form.get(f'brand{i}_tiktok_hashtags')
            brand.tiktok_keywords = request.form.get(f'brand{i}_tiktok_keywords')

            # YouTube fields
            brand.youtube_urls = request.form.get(f'brand{i}_youtube_urls')
            brand.youtube_hashtags = request.form.get(f'brand{i}_youtube_hashtags')
            brand.youtube_searchterms = request.form.get(f'brand{i}_youtube_searchterms')

            # Twitter fields
            brand.twitter_profiles = request.form.get(f'brand{i}_twitter_profiles')
            brand.twitter_keywords = request.form.get(f'brand{i}_twitter_keywords')
            brand.twitter_country = request.form.get(f'brand{i}_twitter_country')
            brand.twitter_start_date = request.form.get(f'brand{i}_twitter_start_date')
            brand.twitter_end_date = request.form.get(f'brand{i}_twitter_end_date')
            brand.twitter_language = request.form.get(f'brand{i}_twitter_language')

            # Website fields
            brand.website_urls = request.form.get(f'brand{i}_website_urls')

            campaign.brands.append(brand)
            campaign.status = "Pending 🟠"
        
        db.session.add(campaign)
        db.session.commit()

        flash("Campaign started successfully! Please visit your campaigns page...", "success")
        return redirect(url_for('accounts.campaign'))

    return render_template('start_new_campaign.html', form=form)




@accounts.route('/your_campaigns')
@login_required
def your_campaigns():
    # Fetch campaigns associated with the logged in user
    campaigns = current_user.campaigns
    return render_template('your_campaigns.html', campaigns=campaigns)
