from typing import TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .tool import Tool
    from .recommendation import Recommendation

class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(90), unique=True)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)

    tools: Mapped[list['Tool']] = relationship(
        back_populates='category', 
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    recommendations: Mapped[list['Recommendation']] = relationship(
        back_populates='category',
        cascade='all, delete-orphan',
        passive_deletes=True
    )