from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .proficiency_level import ProficiencyLevel
    from .category import Category

class Recommendation(Base):
    __tablename__ = 'recommendations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    proficiency_level_id: Mapped[int] = mapped_column(ForeignKey('proficiency_levels.id', ondelete='CASCADE'))
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))
    text: Mapped[str] = mapped_column(String(1024))

    proficiency_level: Mapped['ProficiencyLevel'] = relationship(back_populates='recommendations')
    category: Mapped['Category'] = relationship(back_populates='recommendations')