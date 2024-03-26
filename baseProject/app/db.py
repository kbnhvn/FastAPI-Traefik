import databases
import ormar
import sqlalchemy

from .config import settings

database = databases.Database(settings.db_url)
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    metadata = metadata
    database = database


class User(ormar.Model):
    class Meta(BaseMeta):
        tablename = "users"

    id: int = ormar.Integer(primary_key=True)
    lastName: str = ormar.String(max_length=32, unique=False, nullable=False)
    firstName: str = ormar.String(max_length=32, unique=False, nullable=False)
    password: str = ormar.String(max_length=128, unique=False, nullable=False)
    email: str = ormar.String(max_length=128, unique=True, nullable=False)
    city: str = ormar.String(max_length=64, unique=False, nullable=True)
    active: bool = ormar.Boolean(default=True, nullable=False)
    # Role user ou admin
    role: str = ormar.String(max_length=20, default="user", nullable=False)


engine = sqlalchemy.create_engine(settings.db_url)
metadata.create_all(engine)
