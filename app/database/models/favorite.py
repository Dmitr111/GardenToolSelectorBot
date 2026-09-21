from typing import TYPE_CHECKING
from datetime import datetime
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .tool import Tool

class Favorite(Base):
    __tablename__ = 'favorites'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    tool_id: Mapped[int] = mapped_column(ForeignKey('tools.id', ondelete='CASCADE'))
    add_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped['User'] = relationship(back_populates='favorites')
    tool: Mapped['Tool'] = relationship(back_populates='favorites')

    __table_args__ = (
        UniqueConstraint('user_id', 'tool_id', name='uq_favorite_user_tool'),
    )