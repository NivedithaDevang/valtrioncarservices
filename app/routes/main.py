from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app.models import Service, Booking
from app import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    services = Service.query.all()
    categories = list(set([s.category for s in services]))
    return render_template('index.html', services=services, categories=categories)

@main.route('/services')
def services():
    all_services = Service.query.all()
    categories = list(set([s.category for s in all_services]))
    return render_template('services.html', services=all_services, categories=categories)

@main.route('/estimator')
def estimator():
    return render_template('estimator.html')

@main.route('/dashboard')
@login_required
def dashboard():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.created_at.desc()).all()
    return render_template('dashboard.html', bookings=bookings)

@main.route('/api/estimate', methods=['POST'])
def api_estimate():
    data = request.json
    brand = data.get('brand', '')
    age = int(data.get('age', 0))
    service_type = data.get('service', '')

    base_prices = {
        'Basic Car Wash': 499,
        'Premium Car Wash': 999,
        'Oil Change': 1299,
        'AC Service': 2499,
        'Brake Service': 1999,
        'Full Inspection': 799,
        'Battery Replacement': 3499,
        'Tyre Rotation': 599,
        'Engine Tune-Up': 3999,
        'Suspension Check': 1499,
        'Wheel Alignment': 899,
        'Periodic Service': 2999,
    }

    luxury_brands = ['BMW', 'Mercedes-Benz', 'Audi', 'Jaguar', 'Land Rover', 'Porsche', 'Volvo']
    premium_brands = ['Toyota', 'Honda', 'Hyundai', 'Kia', 'Jeep', 'Volkswagen', 'Skoda', 'MG']

    base = base_prices.get(service_type, 1500)

    if brand in luxury_brands:
        base *= 2.0
    elif brand in premium_brands:
        base *= 1.3

    if age > 10:
        base *= 1.4
    elif age > 5:
        base *= 1.2

    return jsonify({'estimate': round(base), 'service': service_type, 'brand': brand})

@main.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.json
    msg = data.get('message', '').lower()

    responses = {
        'oil': "Our Oil Change starts at Rs.1,299. We use OEM-grade engine oils. Book via our Services page!",
        'ac': "Our AC Service (gas refill + cleaning) is Rs.2,499 and takes 2-3 hours. Want to book?",
        'brake': "Brake Service including pads and fluid check is Rs.1,999. Safety first! Book now.",
        'wash': "We offer Basic Car Wash at Rs.499 and Premium Wash at Rs.999. Both include interior vacuum!",
        'battery': "Battery Replacement with installation is Rs.3,499. Quick 30-minute service!",
        'tyre': "Tyre Rotation is Rs.599. Wheel Alignment is Rs.899.",
        'price': "Our prices start from Rs.499 for car wash to Rs.3,999 for engine tune-up. All transparent, no hidden charges!",
        'book': "To book a service, click Book Now on any service card or go to our Services page!",
        'location': "We serve Bengaluru, Hyderabad, Chennai and Pune. Pickup and delivery included!",
        'pickup': "Yes! We offer complimentary pickup and doorstep delivery for all services.",
        'warranty': "All our services come with a 30-day service warranty assurance.",
        'time': "Service times vary: Car wash 1hr, Oil change 1-2hr, AC service 2-3hr.",
        'payment': "We accept online payments via Razorpay including UPI, cards, and net banking.",
        'hello': "Hello! Welcome to Valtrion! I am your car care assistant. How can I help you today?",
        'hi': "Hi there! Welcome to Valtrion! Ask me about our services, pricing, or bookings!",
        'help': "I can help you with service prices, booking info, our locations, and pickup and delivery. What do you need?",
        'inspection': "Our Full Car Inspection (30-point check) is just Rs.799 and takes 1.5 hours!",
        'engine': "Engine Tune-Up is Rs.3,999. Improves performance and fuel efficiency!",
        'periodic': "Periodic Service (comprehensive) is Rs.2,999. Includes all major checks!",
    }

    reply = "I am not sure about that. Try asking about services, prices, booking, locations, or pickup!"
    for key, response in responses.items():
        if key in msg:
            reply = response
            break

    return jsonify({'reply': reply})