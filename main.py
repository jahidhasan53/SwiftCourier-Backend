# Ensure passlib works with bcrypt 4.1.0+ and 5.0.0
try:
    import bcrypt
    if not hasattr(bcrypt, "__about__"):
        class _About:
            __version__ = getattr(bcrypt, "__version__", "4.0.1")
        bcrypt.__about__ = _About()
except Exception:
    pass

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, sessionLocal
import models
from router import auth, users, parcels, agents, admin

# Create all tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="SwiftCourier API")

# CORS — must have allow_credentials=False when allow_origins=["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(parcels.router, prefix="/api/v1", tags=["Parcels"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["Agents"])
app.include_router(admin.router, prefix="/api/v1", tags=["Admin"])


@app.get("/health")
def health():
    return {"status": "ok"}


@app.on_event("startup")
def seed_defaults():
    """Seed default admin user and platform settings on first run."""
    from passlib.context import CryptContext
    bcrypt_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
    db = sessionLocal()
    try:
        # Seed admin
        if not db.query(models.User).filter(models.User.email == "admin@swiftcourier.com").first():
            db.add(models.User(
                full_name="Admin",
                email="admin@swiftcourier.com",
                phone="01700000000",
                hashed_password=bcrypt_ctx.hash("Admin12345"),
                role="admin",
                is_verified=True,
            ))

        # Seed default settings
        defaults = [
            ("delivery_charge", "60", "Base delivery charge in BDT"),
            ("cod_charge_percent", "1", "COD charge percentage"),
            ("platform_name", "SwiftCourier", "Platform name"),
        ]
        for key, value, desc in defaults:
            if not db.query(models.PlatformSetting).filter(models.PlatformSetting.setting_key == key).first():
                db.add(models.PlatformSetting(setting_key=key, setting_value=value, description=desc))

        db.commit()
    finally:
        db.close()
