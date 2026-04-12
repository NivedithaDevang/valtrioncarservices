from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, make_response
from flask_login import login_required, current_user
from app import db
from app.models import Booking, Service, User, Mechanic, ChatMessage
from datetime import datetime, date, timedelta
from functools import wraps

admin = Blueprint('admin', __name__)

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated

# ========== DASHBOARD ==========
@admin.route('/')
@login_required
@admin_required
def dashboard():
    today = date.today()
    bookings_today  = Booking.query.filter(db.func.date(Booking.created_at) == today).count()
    revenue_today   = db.session.query(db.func.sum(Booking.total_amount)).filter(
        db.func.date(Booking.created_at) == today, Booking.payment_status == 'Paid').scalar() or 0
    total_revenue   = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.payment_status == 'Paid').scalar() or 0
    pending_jobs    = Booking.query.filter_by(status='Pending').count()
    new_customers   = User.query.filter(
        db.func.date(User.created_at) == today, User.role == 'customer').count()
    total_bookings  = Booking.query.count()
    confirmed       = Booking.query.filter_by(status='Confirmed').count()
    completed       = Booking.query.filter_by(status='Completed').count()
    cancelled       = Booking.query.filter_by(status='Cancelled').count()
    # Last 7 days chart data
    labels, counts, revenues = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        labels.append(d.strftime('%d %b'))
        counts.append(Booking.query.filter(db.func.date(Booking.created_at) == d).count())
        rev = db.session.query(db.func.sum(Booking.total_amount)).filter(
            db.func.date(Booking.created_at) == d, Booking.payment_status == 'Paid').scalar() or 0
        revenues.append(float(rev))
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(8).all()
    unread_msgs = ChatMessage.query.filter_by(sender='customer', is_read=False).count()
    return render_template('admin/dashboard.html',
        bookings_today=bookings_today, revenue_today=revenue_today,
        total_revenue=total_revenue, pending_jobs=pending_jobs,
        new_customers=new_customers, total_bookings=total_bookings,
        confirmed=confirmed, completed=completed, cancelled=cancelled,
        labels=labels, counts=counts, revenues=revenues,
        recent_bookings=recent_bookings, unread_msgs=unread_msgs)

# ========== BOOKINGS ==========
@admin.route('/bookings')
@login_required
@admin_required
def bookings():
    status_filter = request.args.get('status', '')
    date_filter   = request.args.get('date', '')
    q = Booking.query
    if status_filter:
        q = q.filter_by(status=status_filter)
    if date_filter:
        try:
            fd = datetime.strptime(date_filter, '%Y-%m-%d').date()
            q = q.filter(db.func.date(Booking.created_at) == fd)
        except: pass
    all_bookings = q.order_by(Booking.created_at.desc()).all()
    mechanics    = Mechanic.query.filter_by(is_active=True).all()
    return render_template('admin/bookings.html', bookings=all_bookings,
        mechanics=mechanics, status_filter=status_filter, date_filter=date_filter)

@admin.route('/booking/update-status', methods=['POST'])
@login_required
@admin_required
def update_booking_status():
    data = request.json
    b = Booking.query.get_or_404(data['booking_id'])
    b.status = data['status']
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/booking/assign-mechanic', methods=['POST'])
@login_required
@admin_required
def assign_mechanic():
    data = request.json or {}
    b = Booking.query.get_or_404(data.get('booking_id'))
    mechanic_id = data.get('mechanic_id')

    if mechanic_id in ('', None):
        b.mechanic_id = None
        db.session.commit()
        return jsonify({'success': True})

    try:
        mechanic_id = int(mechanic_id)
    except (TypeError, ValueError):
        return jsonify({'success': False, 'error': 'Invalid mechanic selected.'}), 400

    mechanic = Mechanic.query.get(mechanic_id)
    if not mechanic or not mechanic.is_active:
        return jsonify({'success': False, 'error': 'Mechanic not found or inactive.'}), 404

    b.mechanic_id = mechanic_id
    db.session.commit()
    return jsonify({'success': True})

# ========== CUSTOMERS ==========
@admin.route('/customers')
@login_required
@admin_required
def customers():
    all_customers = User.query.filter_by(role='customer').order_by(User.created_at.desc()).all()
    return render_template('admin/customers.html', customers=all_customers)

@admin.route('/customer/<int:user_id>')
@login_required
@admin_required
def customer_detail(user_id):
    user     = User.query.get_or_404(user_id)
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.created_at.desc()).all()
    return render_template('admin/customer_detail.html', user=user, bookings=bookings)

# ========== SERVICES ==========
@admin.route('/services')
@login_required
@admin_required
def services():
    all_services = Service.query.all()
    return render_template('admin/services.html', services=all_services)

@admin.route('/service/add', methods=['POST'])
@login_required
@admin_required
def add_service():
    data = request.json
    s = Service(name=data['name'], description=data.get('description',''),
                price=float(data['price']), duration=data.get('duration',''),
                category=data.get('category',''), icon=data.get('icon','fa-wrench'))
    db.session.add(s); db.session.commit()
    return jsonify({'success': True, 'id': s.id})

@admin.route('/service/edit', methods=['POST'])
@login_required
@admin_required
def edit_service():
    data = request.json
    s = Service.query.get_or_404(data['id'])
    s.name = data.get('name', s.name)
    s.description = data.get('description', s.description)
    s.price = float(data.get('price', s.price))
    s.duration = data.get('duration', s.duration)
    s.category = data.get('category', s.category)
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/service/delete/<int:sid>', methods=['POST'])
@login_required
@admin_required
def delete_service(sid):
    s = Service.query.get_or_404(sid)
    db.session.delete(s); db.session.commit()
    return jsonify({'success': True})

# ========== PAYMENTS ==========
@admin.route('/payments')
@login_required
@admin_required
def payments():
    method_filter = request.args.get('method', '')
    q = Booking.query.filter(Booking.payment_status != 'Unpaid')
    if method_filter:
        q = q.filter_by(payment_method=method_filter)
    all_payments = q.order_by(Booking.created_at.desc()).all()
    total_upi = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.payment_method != 'COD', Booking.payment_status == 'Paid').scalar() or 0
    total_cod = db.session.query(db.func.sum(Booking.total_amount)).filter(
        Booking.payment_method == 'COD').scalar() or 0
    return render_template('admin/payments.html', payments=all_payments,
        total_upi=total_upi, total_cod=total_cod, method_filter=method_filter)

@admin.route('/invoice/<int:booking_id>')
@login_required
@admin_required
def admin_invoice(booking_id):
    return redirect(url_for('booking.download_invoice', booking_id=booking_id))

# ========== CHAT ==========
@admin.route('/chat')
@login_required
@admin_required
def chat():
    customers = User.query.filter_by(role='customer').all()
    unread_by_user = {}
    for c in customers:
        unread_by_user[c.id] = ChatMessage.query.filter_by(user_id=c.id, sender='customer', is_read=False).count()
    return render_template('admin/chat.html', customers=customers, unread_by_user=unread_by_user)

@admin.route('/chat/messages/<int:user_id>')
@login_required
@admin_required
def get_messages(user_id):
    msgs = ChatMessage.query.filter_by(user_id=user_id).order_by(ChatMessage.created_at.asc()).all()
    ChatMessage.query.filter_by(user_id=user_id, sender='customer', is_read=False).update({'is_read': True})
    db.session.commit()
    return jsonify([{'sender': m.sender, 'message': m.message, 'time': m.created_at.strftime('%I:%M %p')} for m in msgs])

# ========== MECHANICS ==========
@admin.route('/mechanics')
@login_required
@admin_required
def mechanics():
    all_mechanics = Mechanic.query.all()
    return render_template('admin/mechanics.html', mechanics=all_mechanics)

@admin.route('/mechanic/add', methods=['POST'])
@login_required
@admin_required
def add_mechanic():
    data = request.json or {}
    name = (data.get('name') or '').strip()
    if not name:
        return jsonify({'success': False, 'error': 'Mechanic name is required.'}), 400
    m = Mechanic(name=name, phone=(data.get('phone') or '').strip(), specialty=(data.get('specialty') or '').strip())
    db.session.add(m); db.session.commit()
    return jsonify({'success': True, 'id': m.id})

@admin.route('/mechanic/delete/<int:mid>', methods=['POST'])
@login_required
@admin_required
def delete_mechanic(mid):
    m = Mechanic.query.get_or_404(mid)
    db.session.delete(m); db.session.commit()
    return jsonify({'success': True})