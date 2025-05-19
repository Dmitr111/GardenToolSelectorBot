from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base 

if TYPE_CHECKING:
    from .favorite import Favorite
    from .review import Review
    from .proficiency_level import ProficiencyLevel

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    proficiency_level_id: Mapped[int] = mapped_column(ForeignKey('proficiency_levels.id', ondelete='CASCADE'))
    is_admin: Mapped[bool] = mapped_column(default=False)
    registration_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    proficiency_level: Mapped['ProficiencyLevel'] = relationship(back_populates='users')
    favorites: Mapped[list['Favorite']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    reviews: Mapped[list['Review']] = relationship(
        back_populates='user',
        cascade='all, delete-orphan',
        passive_deletes=True
    )