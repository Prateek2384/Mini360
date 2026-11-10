import uuid

from sqlalchemy import MetaData, create_engine, func
from sqlalchemy.orm import DeclarativeBase, mapped_column, sessionmaker

from app.core.config import settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}
#Engine .env se url leta h and post gresql se connection banane ke liye tayaar krta h
'''.env se URL leta hai aur PostgreSQL se connection banane ke liye taiyaar rehta hai.
pool_pre_ping=True: Kisi purane connection ko use karne se pehle ek chhota sa check karta hai ki woh abhi bhi zinda hai ya nahi. Kyun: Aaj jaise container band ho gaya tha, waise hi agar DB restart ho jaaye, to purane connections toot jaate hain. Ye setting un toote connections ko pakad leti hai, warna ajeeb errors aate.'''

engine = create_engine(settings.database_url, pool_pre_ping=True)

'''Har API request ke liye ek naya Session isi se banega.
autoflush=False ka matlab: Changes database mein tabhi jaayenge jab hum khud bolenge. Isse samajhna aasaan rehta hai ki kab kya database mein gaya.'''
SessionLocal = sessionmaker(bind=engine, autoflush=False)


'''Step 3 mein har model class User(Base) jaisa likha jaayega. Isse SQLAlchemy ko pata rehta hai ki kaun-kaun si tables hain.
metadata ek “register” hai jisme saari tables ki list rehti hai. Alembic isi register ko padhkar migrations banayega.'''

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

'''primary_key=True	Ye column table ki primary key hai
default=uuid.uuid4	Jab Python (SQLAlchemy) row banata hai, to Python UUID generate karta hai
server_default=gen_random_uuid()	Jab koi seedha SQL se row daalta hai, jaise Step 6 ke tests mein, to PostgreSQL khud UUID bana deta hai'''
def uuid_pk():
    return mapped_column(
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
