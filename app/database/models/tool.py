from typing import TYPE_CHECKING
from decimal import Decimal
from sqlalchemy import ForeignKey, String, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship, column_property
from sqlalchemy import select, func, cast
from .base import Base
from .review import Review

if TYPE_CHECKING:
    from .category import Category
    from .manufacturer import Manufacturer
    from .favorite import Favorite
    from .tool_material import ToolMaterial
    from .material import Material

class Tool(Base):
    __tablename__ = 'tools'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50))
    model: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str] = mapped_column(String(1024), nullable=True)
    category_id: Mapped[int] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'))
    manufacturer_id: Mapped[int] = mapped_column(ForeignKey('manufacturers.id', ondelete='CASCADE'))
    weight: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=True)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=True)
    image_url: Mapped[str] = mapped_column(String(2048), nullable=True)

    category: Mapped['Category'] = relationship(back_populates='tools')
    manufacturer: Mapped['Manufacturer'] = relationship(back_populates='tools')

    materials_link: Mapped[list['ToolMaterial']] = relationship(
        back_populates='tool',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    
    @property
    def materials(self) -> list['Material']:
        return [link.material for link in self.materials_link]

    avg_rating = column_property(
        select(
            cast(func.avg(Review.rating), Numeric(3, 2))
        ).where(
            Review.tool_id == id
        ).correlate_except(Review).scalar_subquery()
    )

    reviews: Mapped[list['Review']] = relationship(
        back_populates='tool',
        cascade='all, delete-orphan',
        passive_deletes=True
    )
    favorites: Mapped[list['Favorite']] = relationship(
        back_populates='tool',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint('category_id', 'manufacturer_id', name='uq_tool_name_manufacturer'),
    )