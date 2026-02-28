import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/soscubamap",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = False
    REMEMBER_COOKIE_SECURE = False
    WTF_CSRF_ENABLED = True
    APP_NAME = "#SOSCuba Map"
    DEFAULT_LANGUAGE = "es"
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    GOOGLE_MAPS_MAP_ID = os.getenv("GOOGLE_MAPS_MAP_ID", "")
    POSTS_REQUIRE_MODERATION = True
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@soscuba.local")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
