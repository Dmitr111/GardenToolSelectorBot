from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .tool import Tool

class Manufacturer(Base):
    __tablename__ = 'manufacturers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(90), unique=True)
    country: Mapped[str] = mapped_column(String(56), nullable=True)
    website: Mapped[str] = mapped_column(String(255), nullable=True)

    tools: Mapped[list['Tool']] = relationship(
        back_populates='manufacturer',
        cascade='all, delete-orphan',
        passive_deletes=True
    )