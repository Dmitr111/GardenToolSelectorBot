from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

if TYPE_CHECKING:
    from .tool import Tool
    from .material import Material

class ToolMaterial(Base):
    __tablename__ = 'tool_materials'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tool_id: Mapped[int] = mapped_column(ForeignKey('tools.id', ondelete='CASCADE'))
    material_id: Mapped[int] = mapped_column(ForeignKey('materials.id', ondelete='CASCADE'))

    tool: Mapped['Tool'] = relationship(back_populates='materials_link')
    material: Mapped['Material'] = relationship(back_populates='tools_link')

    __table_args__ = (
        UniqueConstraint('tool_id', 'material_id', name='uq_tool_material'),
    )