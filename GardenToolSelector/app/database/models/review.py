from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, Integer, Text, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .tool import Tool

class Review(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    tool_id: Mapped[int] = mapped_column(ForeignKey('tools.id', ondelete='CASCADE'))
    text: Mapped[str] = mapped_column(Text)
    rating: Mapped[int] = mapped_column(Integer)
    review_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped['User'] = relationship(back_populates='reviews')
    tool: Mapped['Tool'] = relationship(back_populates='reviews')

    __table_args__ = (
        UniqueConstraint('user_id', 'tool_id', name='uq_review_user_tool'),
        CheckConstraint('rating >= 1 AND rating <= 5', name='ck_review_rating_range'),
    )