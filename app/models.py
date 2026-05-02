from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    phone         = db.Column(db.String(15), nullable=False)
    password      = db.Column(db.String(200), nullable=False)
    role          = db.Column(db.String(20), default='customer')
    address       = db.Column(db.String(300))
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    bookings      = db.relationship('Booking', backref='customer', lazy=True)
    messages      = db.relationship('ChatMessage', backref='user_ref', lazy=True)

class Service(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price       = db.Column(db.Float, nullable=False)
    duration    = db.Column(db.String(50))
    category    = db.Column(db.String(50))
    icon        = db.Column(db.String(100))
    is_active   = db.Column(db.Boolean, default=True)

class Mechanic(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    phone    = db.Column(db.String(15))
    specialty= db.Column(db.String(100))
    is_active= db.Column(db.Boolean, default=True)

class Booking(db.Model):
    id               = db.Column(db.Integer, primary_key=True)
    user_id          = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    service_id       = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    mechanic_id      = db.Column(db.Integer, db.ForeignKey('mechanic.id'), nullable=True)
    customer_name    = db.Column(db.String(100))
    customer_phone   = db.Column(db.String(15))
    car_brand        = db.Column(db.String(50))
    car_model        = db.Column(db.String(50))
    car_number       = db.Column(db.String(20))
    fuel_type        = db.Column(db.String(20))
    pickup_address   = db.Column(db.String(200))
    preferred_date   = db.Column(db.String(50))
    status           = db.Column(db.String(30), default='Pending')
    total_amount     = db.Column(db.Float)
    payment_status   = db.Column(db.String(20), default='Unpaid')
    payment_method   = db.Column(db.String(30))
    payment_ref      = db.Column(db.String(100))
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)
    service          = db.relationship('Service', backref='bookings')
    mechanic         = db.relationship('Mechanic', backref='bookings')


# ========== REVIEW MODEL ==========
class Review(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    rating     = db.Column(db.Integer, nullable=False)
    comment    = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ChatMessage(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message    = db.Column(db.Text, nullable=False)
    sender     = db.Column(db.String(20), nullable=False)  # customer or admin
    is_read    = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)