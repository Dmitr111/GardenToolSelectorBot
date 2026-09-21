from aiogram import Router
from .users import router as users_router
from .categories import router as categories_router
from .manufacturers import router as manufacturers_router
from .tools import router as tools_router
from .materials import router as materials_router
from .recommendation import router as recommendation_router
from .proficiency_levels import router as proficiency_levels_router
from .review import router as review_router

admin_router = Router()

admin_router.include_router(users_router)
admin_router.include_router(categories_router)
admin_router.include_router(manufacturers_router)
admin_router.include_router(tools_router)
admin_router.include_router(materials_router)
admin_router.include_router(recommendation_router)
admin_router.include_router(proficiency_levels_router)
admin_router.include_router(review_router)

__all__ = ['admin_router']