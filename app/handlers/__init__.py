from aiogram import Router
from .commands import router as commands_router
from .comparison import router as comparison_router
from .favorites import router as favorites_router
from .reviews import router as reviews_router
from .search import router as search_router
from .selection import router as selection_router
from .admin import admin_router
from .filters import router as filters_router
from .proficiency import router as update_proficiency_router

main_router = Router()

main_router.include_router(comparison_router)
main_router.include_router(favorites_router)
main_router.include_router(reviews_router)
main_router.include_router(search_router)
main_router.include_router(selection_router)
main_router.include_router(admin_router)
main_router.include_router(filters_router)
main_router.include_router(update_proficiency_router)
main_router.include_router(commands_router)

__all__ = ['main_router']