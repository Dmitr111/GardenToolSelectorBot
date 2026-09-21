from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from .models import *
from .repositories import *
from ..config import CONNECTIONSTRING, ADMIN_IDS

engine = create_async_engine(url=CONNECTIONSTRING)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        plr = ProficiencyLevelRepository(session)
        proficiency_levels = await plr.get_all()

        if not proficiency_levels:
            levels = [
                ProficiencyLevel(name="Новичок", description="Начинающий пользователь"),
                ProficiencyLevel(name="Любитель", description="Опытный пользователь"),
                ProficiencyLevel(name="Профессионал", description="Профессиональный пользователь")
            ]

            session.add_all(levels)
            await session.commit()
        
        mr = ManufacturerRepository(session)
        materials = await mr.get_all()

        if not materials:
            array = [
                Material("Сталь"),
                Material("Алюминий"),
                Material("Титан"),
                Material("Дерево"),
                Material("Пластик"),
                Material("Углеродное волокно"),
                Material("Резина"),
                Material("Латунь"),
                Material("Медь"),
                Material("Нержавеющая сталь"),
            ]

            session.add_all(array)
            await session.commit()

        ur = UserRepository(session)
        for admin_id in ADMIN_IDS:
            admin = await ur.get_by_telegram_id(admin_id)

            if not admin:
                admin = User(username=None, telegram_id=admin_id, proficiency_level_id=1, is_admin=True)
                session.add(admin)
            elif not admin.is_admin:
                admin.is_admin = True

        await session.commit()


async def get_session() -> async_sessionmaker:
    return async_session