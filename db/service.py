import datetime
import math
import random
import string

from sqlalchemy import select, func

from sqlalchemy.ext.asyncio import AsyncSession

from db.models.models import User, Code, WorkoutPlan, FreeWorkoutPlan
from db.models.schemas import User as UserDC, WorkoutPlan as WorkoutPlanDC, FreeWorkoutPlan as FreeWorkoutPlanDC


async def get_user(
        session: AsyncSession,
        telegram_id: int,
        admin: bool = False
) -> bool or User:
    if admin:
        query = await session.execute(
            select(User)
            .filter(User.telegram_id == telegram_id, User.role == 1)
            .limit(1)
        )
    else:
        query = await session.execute(
            select(User)
            .filter(User.telegram_id == telegram_id)
            .limit(1)
        )
    res = query.scalars().first()
    if not res:
        return False
    return res


async def delete_user(
        session: AsyncSession,
        telegram_id: int,
):
    user = await get_user(session, telegram_id)
    await session.delete(user)
    await session.commit()


async def get_all_users(session: AsyncSession, page: int, search: str = ''):
    offset = page * 7
    search = "%{}%".format(search)
    query = await session.execute(
        select(User)
        .filter(User.name.like(search))
        .order_by(User.name)
        .limit(7)
        .offset(offset))
    query_count = await session.execute(
        select(func.count(User.telegram_id))
        .filter(User.name.like(search))
    )
    count_pages = 0
    res = query.scalars().all()
    count = query_count.scalars().first()
    if count != 0:
        count_pages = math.ceil(count / 7)
    return res, count_pages


async def create_user(session: AsyncSession, user: UserDC) -> User:
    query = await session.execute(
        select(Code)
        .filter(Code.code == user.code)
        .limit(1))
    code = query.scalars().first()
    user_db_instance = User(
        telegram_id=user.telegram_id,
        name=user.name,
        code=code,
    )
    session.add(user_db_instance)
    await session.commit()
    await session.refresh(user_db_instance)
    return user_db_instance


async def get_code(session: AsyncSession, code: str) -> bool:
    query = await session.execute(
        select(Code)
        .filter(Code.code == code, Code.user_id.is_(None))
        .limit(1))
    res = query.scalars().first()
    if not res:
        return False
    return True


async def create_code(session: AsyncSession) -> Code:
    while True:
        code = ''.join(
            random.choices(string.ascii_letters + string.digits, k=10)
        )
        query = await session.execute(
            select(Code)
            .filter(Code.code == code)
            .limit(1)
        )
        res = query.scalars().first()
        if not res:
            code_db_instance = Code(
                code=code,
            )
            session.add(code_db_instance)
            await session.commit()
            return code_db_instance


async def get_workout_user_plan(session: AsyncSession, telegram_id: int):
    data = datetime.date.today()
    query = await session.execute(
        select(WorkoutPlan)
        .filter(WorkoutPlan.user_id == telegram_id, WorkoutPlan.date >= data)
        .order_by(WorkoutPlan.date.desc())
        .limit(7)
    )
    res = query.scalars().all()
    return res


async def get_workout(session: AsyncSession, workout_id: int) -> WorkoutPlan:
    query = await session.execute(
        select(WorkoutPlan)
        .filter(WorkoutPlan.id == workout_id)
        .limit(1)
    )
    workout = query.scalars().first()
    return workout


async def get_workout_for_user(
        session: AsyncSession,
        telegram_id: int
) -> WorkoutPlan:
    date = datetime.date.today()
    query = await session.execute(
        select(WorkoutPlan)
        .filter(WorkoutPlan.user_id == telegram_id, WorkoutPlan.date == date)
        .limit(1)
    )
    res = query.scalars().first()
    return res


async def get_workout_history(session: AsyncSession, telegram_id: int):
    date = datetime.date.today()
    query = await session.execute(
        select(WorkoutPlan)
        .filter(WorkoutPlan.user_id == telegram_id, WorkoutPlan.date < date)
        .limit(7)
    )
    res = query.scalars().all()
    return res


async def create_workout_plan(
        session: AsyncSession,
        data: WorkoutPlanDC
) -> bool:
    query = await session.execute(
        select(WorkoutPlan)
        .filter(
            WorkoutPlan.user_id == data.user_id,
            WorkoutPlan.date == data.date
        )
        .limit(1)
    )
    workout = query.scalars().first()
    if workout:
        workout.description = data.description
        await session.commit()
        return True
    workout_db_instance = WorkoutPlan(
        description=data.description,
        user_id=data.user_id,
        date=data.date,
    )
    session.add(workout_db_instance)
    await session.commit()
    return True


async def create_free_workout_plan(
        session: AsyncSession,
        data: FreeWorkoutPlanDC
) -> bool:
    query = await session.execute(
        select(FreeWorkoutPlan)
        .filter(
            FreeWorkoutPlan.date == data.date
        )
        .limit(1)
    )
    workout = query.scalars().first()
    if workout:
        workout.description = data.description
        await session.commit()
        return True
    workout_db_instance = FreeWorkoutPlan(
        description=data.description,
        date=data.date,
    )
    session.add(workout_db_instance)
    await session.commit()
    return True


async def update_workout_plan(
        session: AsyncSession,
        workout_id: int,
        description: str
) -> bool:
    workout = await get_workout(session, workout_id)
    workout.description = description
    await session.commit()
    return True


async def edit_user_name(
        session: AsyncSession,
        user_id: int,
        new_name: str
) -> bool:
    user = await get_user(session, user_id)
    if user:
        user.name = new_name
        await session.commit()
        return True
    else:
        return False


async def get_workout_free_plan(
        session: AsyncSession,
):
    data = datetime.date.today()
    query = await session.execute(
        select(FreeWorkoutPlan)
        .filter(FreeWorkoutPlan.date >= data)
        .order_by(FreeWorkoutPlan.date.desc())
        .limit(7)
    )
    res = query.scalars().all()
    return res


async def get_free_workout(
        session: AsyncSession,
        workout_id: int
) -> FreeWorkoutPlan:
    query = await session.execute(
        select(FreeWorkoutPlan)
        .filter(FreeWorkoutPlan.id == workout_id)
        .limit(1)
    )
    workout = query.scalars().first()
    return workout


async def update_free_workout_plan(
        session: AsyncSession,
        workout_id: int,
        description: str
) -> bool:
    workout = await get_free_workout(session, workout_id)
    workout.description = description
    await session.commit()
    return True


async def get_free_workout_for_user(
        session: AsyncSession,
) -> FreeWorkoutPlan:
    date = datetime.date.today()
    query = await session.execute(
        select(FreeWorkoutPlan)
        .filter(FreeWorkoutPlan.date == date)
        .limit(1)
    )
    res = query.scalars().first()
    return res
