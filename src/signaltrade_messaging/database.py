from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from signaltrade_messaging.config import settings

options = ({"pool_pre_ping": True, "pool_size": 2, "max_overflow": 1, "pool_timeout": 5}
           if not settings.database_url.startswith("sqlite") else {})
engine = create_engine(settings.database_url, **options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()
