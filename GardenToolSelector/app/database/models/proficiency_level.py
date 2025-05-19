from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .recommendation import Recommendation
    from .user import User

class ProficiencyLevel(Base):
    __tablename__ = 'proficiency_levels'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(512), nullable=True)

    users: Mapped[list['User']] = relationship(back_populates='proficiency_level')
    recommendations: Mapped[list['Recommendation']] = relationship(
        back_populates='proficiency_level',
        cascade='all, delete-orphan',
        passive_deletes=True
    )