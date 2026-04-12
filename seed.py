from app import create_app, db, bcrypt
from app.models import Service, User

app = create_app()
with app.app_context():
    db.create_all()

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
            Service(name="Signature Care", description="The Signature Care package provides essential maintenance with a premium touch. It is ideal for regular servicing to keep your vehicle running smoothly and efficiently.", price=2999, duration="Every 6 months or 5,000-7,500 km", category="Packages", icon="fa-medal"),
            Service(name="Prestige Care", description="The Prestige Care package offers an advanced level of servicing with additional checks and enhancements to improve vehicle performance and comfort. It is perfect for annual maintenance.", price=5999, duration="Every 12 months or 15,000 km", category="Packages", icon="fa-crown"),
            Service(name="Imperial Care", description="The Imperial Care package delivers a complete and thorough service designed to restore your vehicle's overall health and reliability. It is best suited for major servicing.", price=9999, duration="Every 18-24 months or 30,000 km", category="Packages", icon="fa-shield"),
            Service(name="Royal Majesty", description="The Royal Majesty package is the ultimate luxury experience, offering top-tier services and exclusive benefits for customers who want the very best for their vehicles.", price=14999, duration="Once every 2 years or as required for luxury detailing", category="Packages", icon="fa-gem"),
        ]
        db.session.bulk_save_objects(services)
        print("Added " + str(len(services)) + " services!")

    if not User.query.filter_by(email='admin@valtrion.com').first():
        admin = User(
            name='Valtrion Admin',
            email='admin@valtrion.com',
            phone='9876543210',
            password=bcrypt.generate_password_hash('admin123').decode('utf-8'),
            role='admin'
        )
        db.session.add(admin)
        print("Admin created!")
        print("Email: admin@valtrion.com")
        print("Password: admin123")

    db.session.commit()
    print("Database seeded successfully!")
    print("")
    print("Run: python run.py")
    print("Visit: http://127.0.0.1:5000")
    print("Admin: http://127.0.0.1:5000/admin/")