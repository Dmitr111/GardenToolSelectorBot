from typing import TYPE_CHECKING
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .tool_material import ToolMaterial
    from .tool import Tool

class Material(Base):
    __tablename__ = 'materials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    tools_link: Mapped[list['ToolMaterial']] = relationship(
        back_populates='material',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    
    @property
    def tools(self) -> list['Tool']:
        return [link.tool for link in self.tools_link]