from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required, current_user
from app import db, bcrypt
from app.models import Service, User, Booking
from datetime import date, timedelta
from urllib.parse import quote

main = Blueprint('main', __name__)

@main.route('/seed')
def seed():
    if Service.query.count() == 0:
        services = [
            Service(name="Basic Car Wash", description="Exterior body wash, wheel cleaning, window wipe and interior vacuum.", price=499, duration="1 hour", category="Cleaning", icon="fa-spray-can"),
            Service(name="Premium Car Wash", description="Full exterior wash, interior deep clean, dashboard polish and glass cleaning.", price=999, duration="1.5 hours", category="Cleaning", icon="fa-star"),
            Service(name="Ceramic Coating", description="Premium 9H ceramic coating for long-lasting paint protection and showroom shine.", price=8999, duration="4-6 hours", category="Cleaning", icon="fa-gem"),
            Service(name="Oil Change", description="Engine oil drain and refill with OEM-grade oil, oil filter replacement and inspection.", price=1299, duration="1-2 hours", category="Engine", icon="fa-oil-can"),
            Service(name="Engine Tune-Up", description="Spark plug replacement, air filter check, fuel injector cleaning and performance optimization.", price=3999, duration="3-4 hours", category="Engine", icon="fa-cog"),
            Service(name="Coolant Flush", description="Complete radiator coolant flush and refill with anti-corrosion coolant.", price=999, duration="1 hour", category="Engine", icon="fa-temperature-half"),
            Service(name="AC Service", description="AC gas top-up, evaporator and condenser cleaning, filter replacement and performance check.", price=2499, duration="2-3 hours", category="AC", icon="fa-snowflake"),
            Service(name="AC Deep Clean", description="Comprehensive disinfection of AC vents, coils and duct cleaning for fresh air.", price=1499, duration="1.5 hours", category="AC", icon="fa-wind"),
            Service(name="Brake Service", description="Brake pad inspection and replacement, brake fluid check and top-up, rotor inspection.", price=1999, duration="2 hours", category="Brakes", icon="fa-circle-stop"),
            Service(name="Tyre Rotation", description="4-wheel tyre rotation to ensure even wear and extended tyre life.", price=599, duration="45 minutes", category="Brakes", icon="fa-rotate"),
            Service(name="Wheel Alignment", description="Computerized 3D wheel alignment for better handling and tyre longevity.", price=899, duration="1 hour", category="Brakes", icon="fa-arrows-left-right"),
            Service(name="Battery Replacement", description="New OEM-grade battery installation with free battery health check.", price=3499, duration="30 minutes", category="Electrical", icon="fa-battery-full"),
            Service(name="Electrical Diagnosis", description="Advanced ECU scan, wiring check, sensor diagnostics and fault code clearing.", price=799, duration="1 hour", category="Electrical", icon="fa-bolt"),
            Service(name="Full Car Inspection", description="Comprehensive 30-point vehicle inspection covering engine, brakes, suspension and electrical.", price=799, duration="1.5 hours", category="Inspection", icon="fa-magnifying-glass"),
            Service(name="Basic Periodic Service", description="Oil change, filter check, brake inspection, tyre pressure and fluid top-up.", price=1999, duration="2-3 hours", category="Periodic", icon="fa-calendar-check"),
            Service(name="Standard Periodic Service", description="Comprehensive service including oil, all filters, brake fluid, coolant and belts check.", price=2999, duration="3-4 hours", category="Periodic", icon="fa-clipboard-list"),
            Service(name="Comprehensive Service", description="Full vehicle overhaul - all fluids, filters, plugs, belts, brakes and safety check.", price=5999, duration="5-6 hours", category="Periodic", icon="fa-shield-halved"),
            Service(name="Suspension Check", description="Shock absorber, strut, ball joint and bushing inspection for a smooth ride.", price=1499, duration="1.5 hours", category="Suspension", icon="fa-car"),
            Service(name="Prime Care", description="The Prime Care package provides essential maintenance with a premium touch. It is ideal for regular servicing to keep your vehicle running smoothly and efficiently.", price=2999, duration="Every 6 months or 5,000-7,500 km", category="Packages", icon="fa-medal"),
            Service(name="Elite Care", description="The Elite Care package offers an advanced level of servicing with additional checks and enhancements to improve vehicle performance and comfort. It is perfect for annual maintenance.", price=5999, duration="Every 12 months or 15,000 km", category="Packages", icon="fa-crown"),
            Service(name="Prestige Care", description="The Prestige Care package delivers a complete and thorough service designed to restore your vehicle's overall health and reliability. It is best suited for major servicing.", price=9999, duration="Every 18-24 months or 30,000 km", category="Packages", icon="fa-shield"),
            Service(name="Platinum Elite", description="The Platinum Elite package is the ultimate luxury experience, offering top-tier services and exclusive benefits for customers who want the very best for their vehicles.", price=14999, duration="Once every 2 years or as required for luxury detailing", category="Packages", icon="fa-gem"),
        ]
        db.session.bulk_save_objects(services)
        db.session.commit()
        return "Services seeded!"
    return "Services already exist."

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




def build_service_image(title, accent, subtitle):
    initials = ''.join(part[0] for part in title.split()[:2]).upper()
    svg = f'''
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 500" role="img" aria-label="{title}">
      <defs>
        <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="{accent}" stop-opacity="0.96" />
          <stop offset="100%" stop-color="#0f172a" stop-opacity="1" />
        </linearGradient>
        <radialGradient id="glow" cx="50%" cy="35%" r="70%">
          <stop offset="0%" stop-color="#ffffff" stop-opacity="0.28" />
          <stop offset="100%" stop-color="#ffffff" stop-opacity="0" />
        </radialGradient>
      </defs>
      <rect width="800" height="500" rx="36" fill="url(#bg)" />
      <circle cx="650" cy="110" r="140" fill="url(#glow)" />
      <circle cx="132" cy="388" r="168" fill="#ffffff" fill-opacity="0.08" />
      <circle cx="650" cy="388" r="110" fill="#ffffff" fill-opacity="0.08" />
      <text x="56" y="116" fill="#ffffff" font-size="54" font-weight="700" font-family="Arial, Helvetica, sans-serif">{title}</text>
      <text x="56" y="166" fill="#dbeafe" font-size="22" font-weight="400" font-family="Arial, Helvetica, sans-serif">{subtitle}</text>
      <rect x="56" y="214" width="218" height="8" rx="4" fill="#ffffff" fill-opacity="0.42" />
      <rect x="508" y="136" width="172" height="172" rx="36" fill="#ffffff" fill-opacity="0.16" />
      <text x="594" y="235" text-anchor="middle" fill="#ffffff" font-size="78" font-weight="700" font-family="Arial, Helvetica, sans-serif">{initials}</text>
      <text x="56" y="346" fill="#ffffff" font-size="24" font-weight="600" font-family="Arial, Helvetica, sans-serif">Custom car service</text>
      <text x="56" y="384" fill="#e2e8f0" font-size="18" font-weight="400" font-family="Arial, Helvetica, sans-serif">Tailored upgrades, expert fitment, and support</text>
    </svg>
    '''
    return 'data:image/svg+xml;charset=UTF-8,' + quote(svg)




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
    filtered_services = Service.query.filter(
        Service.category.isnot(None),
        Service.category != 'Packages'
    ).all()
    categories = list(set(service.category for service in filtered_services if service.category))
    return render_template('services.html', services=filtered_services, categories=categories)


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
    return render_template(
        'packages.html',
        packages=package_services,
        package_map=package_map,
        # ...existing code...
    )


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


