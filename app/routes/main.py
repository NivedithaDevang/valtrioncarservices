from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db
from app.models import Service, Booking
from datetime import date, timedelta

main = Blueprint('main', __name__)

PACKAGE_DEFINITIONS = [
    {
        'name': 'Prime Care',
        'tagline': 'Essential Elegance for Every Drive',
        'description': 'The Prime Care package provides essential maintenance with a premium touch. It is ideal for regular servicing to keep your vehicle running smoothly and efficiently.',
        'price': 2999,
        'duration': 'Every 6 months or 5,000-7,500 km',
        'icon': 'fa-medal'
    },
    {
        'name': 'Elite Care',
        'tagline': 'Enhanced Performance, Elevated Comfort',
        'description': 'The Elite Care package offers an advanced level of servicing with additional checks and enhancements to improve vehicle performance and comfort. It is perfect for annual maintenance.',
        'price': 5999,
        'duration': 'Every 12 months or 15,000 km',
        'icon': 'fa-crown'
    },
    {
        'name': 'Prestige Care',
        'tagline': 'Comprehensive Care for Lasting Excellence',
        'description': 'The Prestige Care package delivers a complete and thorough service designed to restore your vehicle\'s overall health and reliability. It is best suited for major servicing.',
        'price': 9999,
        'duration': 'Every 18-24 months or 30,000 km',
        'icon': 'fa-shield'
    },
    {
        'name': 'Platinum Elite',
        'tagline': 'Because Your Car Deserves Royal Treatment',
        'description': 'The Platinum Elite package is the ultimate luxury experience, offering top-tier services and exclusive benefits for customers who want the very best for their vehicles.',
        'price': 14999,
        'duration': 'Once every 2 years or as required for luxury detailing',
        'icon': 'fa-gem'
    }
]


def ensure_packages_exist():
    legacy_renames = {
        'Signature Care': 'Prime Care',
        'Prestige Care': 'Elite Care',
        'Imperial Care': 'Prestige Care',
        'Royal Majesty': 'Platinum Elite'
    }
    changed = False

    for old_name, new_name in legacy_renames.items():
        existing = Service.query.filter_by(name=old_name, category='Packages').first()
        target_exists = Service.query.filter_by(name=new_name, category='Packages').first()
        if existing and not target_exists:
            existing.name = new_name
            changed = True

    existing_names = {service.name for service in Service.query.filter_by(category='Packages').all()}
    for package in PACKAGE_DEFINITIONS:
        if package['name'] not in existing_names:
            db.session.add(Service(
                name=package['name'],
                description=package['description'],
                price=package['price'],
                duration=package['duration'],
                category='Packages',
                icon=package['icon']
            ))
            changed = True

    if changed:
        db.session.commit()


@main.route('/')
def index():
    ensure_packages_exist()
    services = Service.query.all()
    categories = list(set(service.category for service in services if service.category))
    return render_template('index.html', services=services, categories=categories)


@main.route('/services')
def services():
    ensure_packages_exist()
    all_services = Service.query.filter(Service.category != 'Packages').all()
    categories = list(set(service.category for service in all_services if service.category))
    return render_template('services.html', services=all_services, categories=categories)


@main.route('/packages')
def packages():
    ensure_packages_exist()
    package_services = Service.query.filter_by(category='Packages').order_by(Service.price.asc()).all()
    package_map = {
        'Prime Care': {
            'tagline': 'Essential Elegance for Every Drive',
            'inclusions': [
                'Engine oil replacement',
                'Oil filter replacement',
                'Fluid top-ups (coolant, brake fluid, windshield washer)',
                'Battery health check',
                'Tyre pressure and condition check',
                'Basic brake inspection',
                '20-30 point vehicle inspection',
                'Exterior car wash',
                'Interior vacuum cleaning'
            ],
            'addons': ['Pick-up and drop service', 'Windshield washer refill', 'Car perfume']
        },
        'Elite Care': {
            'tagline': 'Enhanced Performance, Elevated Comfort',
            'inclusions': [
                'All services included in Prime Care',
                'Air filter cleaning or replacement',
                'Cabin (AC) filter cleaning or replacement',
                'Wheel alignment and balancing',
                'Brake pad cleaning and adjustment',
                'Battery terminal cleaning',
                'AC performance check',
                'Dashboard and interior polishing',
                'Tyre and alloy polishing'
            ],
            'addons': ['Engine bay cleaning', 'Minor scratch removal', 'Interior sanitization/fumigation']
        },
        'Prestige Care': {
            'tagline': 'Comprehensive Care for Lasting Excellence',
            'inclusions': [
                'All services included in Elite Care',
                'Spark plug replacement (for petrol vehicles)',
                'Fuel filter replacement',
                'Brake fluid replacement',
                'Coolant replacement',
                'Transmission fluid inspection/top-up',
                'Full AC servicing',
                'Engine diagnostics using OBD scanner',
                'Engine bay degreasing and dressing',
                'Complete interior detailing (seats, carpets, roof)',
                'Exterior waxing and paint protection'
            ],
            'addons': ['Headlight restoration', 'Underbody anti-rust coating', 'Paint protection treatments']
        },
        'Platinum Elite': {
            'tagline': 'Because Your Car Deserves Royal Treatment',
            'inclusions': [
                'All services included in Prestige Care',
                'Ceramic or Teflon coating',
                'Paint correction and swirl removal',
                'Leather seat conditioning',
                'Steam or ozone interior sanitization',
                'Underbody anti-rust treatment',
                'Premium car spa detailing',
                'Complimentary pick-up and drop service',
                'Priority/express servicing',
                'Dedicated service advisor',
                'Free follow-up inspection within 1 month',
                'Complimentary premium gift hamper (optional)'
            ],
            'addons': []
        }
    }
    return render_template('packages.html', packages=package_services, package_map=package_map)


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
    data = request.json or {}
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
    data = request.json or {}
    msg = (data.get('message', '') or '').lower()

    responses = {
        'package': 'We have four packages: Prime Care, Elite Care, Prestige Care, and Platinum Elite.',
        'prime': 'Prime Care is Rs.2,999.',
        'elite': 'Elite Care is Rs.5,999.',
        'prestige': 'Prestige Care is Rs.9,999.',
        'platinum': 'Platinum Elite is Rs.14,999.',
        'oil': 'Oil Change starts at Rs.1,299.',
        'ac': 'AC Service is Rs.2,499.',
        'brake': 'Brake Service is Rs.1,999.',
        'wash': 'Basic Car Wash starts at Rs.499 and Premium Wash starts at Rs.999.',
        'battery': 'Battery Replacement is Rs.3,499.',
        'tyre': 'Tyre Rotation is Rs.599 and Wheel Alignment is Rs.899.',
        'price': 'Our services start from Rs.499.',
        'book': 'You can book from the Services or Packages page.',
        'location': 'We serve Bengaluru, Hyderabad, Chennai, and Pune.',
        'pickup': 'Yes, pickup and delivery are included.',
        'warranty': 'We provide a 30-day service warranty.',
        'time': 'Service time depends on the selected service or package.',
        'payment': 'We accept online payments and COD where available.',
        'hello': 'Hello, how can I help you?',
        'hi': 'Hi, how can I help?',
        'help': 'I can help with pricing, booking, locations, pickup, and payment.',
        'inspection': 'Full Car Inspection is Rs.799.',
        'engine': 'Engine Tune-Up is Rs.3,999.',
        'periodic': 'Periodic Service starts at Rs.2,999.',
    }

    reply = 'I am not sure about that. Try asking about services, prices, booking, locations, or pickup.'
    for key, response in responses.items():
        if key in msg:
            reply = response
            break

    return jsonify({'reply': reply})