from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here for Alembic to automatically detect all tables
import app.models.user  # noqa: F401
import app.models.word  # noqa: F401
import app.models.room  # noqa: F401
