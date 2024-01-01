from flask import url_for
from flask_login.mixins import UserMixin
from flask import render_template
from werkzeug.security import (
        generate_password_hash,
        check_password_hash
    )
from accounts.extensions import database as db
from accounts.utils import (
        unique_uid,
        unique_security_token,
        send_mail
    )
from datetime import datetime, timedelta


class User(db.Model, UserMixin):
    campaigns = db.relationship('Campaign', backref='user', lazy=True)
    """
    A Base User model class.
    """

    __tablename__ = 'user'

    id = db.Column(db.String(38), primary_key=True, default=unique_uid, unique=True, nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    company_name = db.Column(db.String(128), nullable=False)
    sector = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(128), nullable=False)
    other_role = db.Column(db.String(128), nullable=False)

    active = db.Column(db.Boolean, default=False, nullable=False)
    security_token = db.Column(db.String(138), default=unique_security_token)
    is_send = db.Column(db.DateTime, default=datetime.now)
    change_email = db.Column(db.String(120), default="")

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    profile = db.relationship('Profile', backref='user', uselist=False, cascade='save-update, merge, delete')


    def send_confirmation(self):
        """
        A method for sending an email for account confirmation.
        """
        self.security_token = unique_security_token()
        self.is_send = datetime.now()
        db.session.commit()
        subject = "Verify Your Account."
        
        verification_link = "http://localhost:5000"+url_for('accounts.confirm_account', token=self.security_token)
        content = render_template(
            'email_confirm.html',
            username=self.username,
            verification_link=verification_link,
            img1='https://www.h-in-q.com/wp-content/uploads/2022/07/hinq.png',
            img2='https://www.h-in-q.com/wp-content/uploads/2022/07/qr.png',
        )

        return send_mail(subject, self.email, content)

    @classmethod
    def get_user_by_username(cls, username):
        return cls.query.filter_by(username=username).first()

    @classmethod
    def get_user_by_email(cls, email):
        return cls.query.filter_by(email=email).first()

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def save_profile(self):
        profile = Profile(user_id=self.id)
        profile.save()

    def save(self):
        db.session.add(self)
        db.session.commit()
        self.save_profile()
    
    def is_active(self):
        return self.active
    
    def is_token_expire(self):
        expiry_time = (
            self.is_send
            + timedelta(minutes=15)
        )
        current_time = datetime.now()
        return expiry_time <= current_time
        
    def __repr__(self):
        return '<User> {}'.format(self.email)


class Profile(db.Model):
    """
    A User profile model class.
    """

    __tablename__ = 'profile'

    id = db.Column(db.String(38), primary_key=True, default=unique_uid, unique=True, nullable=False)
    bio = db.Column(db.String(200), default='')
    avator = db.Column(db.String(250), default='')

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    user_id = db.Column(db.String(38), db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)

    def __repr__(self):
        return '<Profile> {}'.format(self.user.username)

    def save(self):
        db.session.add(self)
        db.session.commit()



class Campaign(db.Model):
    __tablename__ = 'campaign'
    
    campaign_id = db.Column(db.String(10), primary_key=True, default=unique_uid, unique=True, nullable=False)  # Hidden field (Token)
    campaign_name = db.Column(db.String(100), nullable=False)
    platforms = db.Column(db.Text, nullable=False)
    num_brands = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.String(38), db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    brands = db.relationship('Brand', backref='campaign', lazy=True)
    image_path = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(100), nullable=False)


class Brand(db.Model):
    __tablename__ = 'brand'
    
    id = db.Column(db.String(38), primary_key=True, default=unique_uid, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    # For Facebook
    facebook_urls = db.Column(db.Text, nullable=True)
    facebook_hashtags = db.Column(db.Text, nullable=True)
    facebook_groups = db.Column(db.Text, nullable=True)

    # For TikTok
    tiktok_urls = db.Column(db.Text, nullable=True)
    tiktok_hashtags = db.Column(db.Text, nullable=True)
    tiktok_keywords = db.Column(db.Text, nullable=True)

    # For YouTube
    youtube_urls = db.Column(db.Text, nullable=True)
    youtube_hashtags = db.Column(db.Text, nullable=True)
    youtube_searchterms = db.Column(db.Text, nullable=True)

    # For Twitter
    twitter_profiles = db.Column(db.Text, nullable=True)
    twitter_keywords = db.Column(db.Text, nullable=True)
    twitter_country = db.Column(db.String(50), nullable=True)
    twitter_start_date = db.Column(db.Date, nullable=True)
    twitter_end_date = db.Column(db.Date, nullable=True)
    twitter_language = db.Column(db.String(50), nullable=True)

    # For Website
    website_urls = db.Column(db.Text, nullable=True)
        
    camp_id = db.Column(db.String(10), db.ForeignKey('campaign.campaign_id', ondelete="CASCADE"), nullable=False)

