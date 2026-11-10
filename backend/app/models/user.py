import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base, uuid_pk

'''class User(Base)	Base se inherit karne par SQLAlchemy ko pata chalta hai ki ye ek table hai, aur woh ise apne register (metadata) mein daal leta hai
__tablename__ = "users"	Database mein table ka naam
Mapped[str]	Column ka Python type. Iske bina None likha ho, to column NOT NULL banta hai
Mapped[str | None]	(Is model mein nahi hai, aage aayega) NULL allowed hai
String(100)	Database type VARCHAR(100), yaani maximum 100 characters
unique=True	Ek email se do accounts nahi ban sakte. Ye rule database khud enforce karega
DateTime(timezone=True)	Time ke saath timezone bhi save hota hai. Tum India mein ho aur server kahin aur, to bhi time sahi rahega
server_default=func.now()	Row banate waqt time na diya jaaye, to PostgreSQL khud current time bhar dega'''

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = uuid_pk()
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
