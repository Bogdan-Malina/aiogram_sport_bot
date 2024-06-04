from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from aiogram.utils.markdown import hunderline
from sqlalchemy.ext.asyncio import AsyncSession

from db.service import get_workout_for_user, get_workout
from bot.states.states import UserMenu
from bot.keyboards.user_keyboard import (
    create_user_keyboard,
    create_history_keyboard
)
from bot.texts.text import text_user_menu as text_menu


router = Router()


@router.callback_query(F.data.startswith("user_menu"))
async def user_menu(callback: CallbackQuery, state: FSMContext):
    await state.set_state(UserMenu.main)
    keyboard, text = await create_user_keyboard(state=state)
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
    )


@router.callback_query(F.data.startswith("get_training"))
async def get_training(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    telegram_id = callback.from_user.id
    workout_for_user = await get_workout_for_user(session, telegram_id)
    if workout_for_user:
        text_message = (
            f"{hunderline(workout_for_user.date.date())}\n\n"
            f"{workout_for_user.description}"
        )
        await callback.message.answer(
            text_message
        )
    else:
        await callback.message.answer(
            text_menu["not_training"]
        )
    keyboard, text = await create_user_keyboard(state=state)
    await callback.message.delete()
    await callback.message.answer(
        text,
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("get_history"))
async def get_history(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    telegram_id = callback.from_user.id
    keyboard, text = await create_history_keyboard(session, telegram_id)
    await state.set_state(UserMenu.history)
    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("userHistory_"))
async def get_history_training(callback: CallbackQuery, session: AsyncSession):
    telegram_id = callback.from_user.id
    workout_id = int(callback.data.split("_")[-1])
    workout = await get_workout(session, workout_id)
    await callback.message.answer(
        f"{hunderline(workout.date.date())}\n\n{workout.description}"
    )
    keyboard, text = await create_history_keyboard(session, telegram_id)
    await callback.message.delete()
    await callback.message.answer(
        text,
        reply_markup=keyboard
    )


@router.callback_query(F.data.startswith("user_back"))
async def user_back(callback: CallbackQuery, state: FSMContext):
    menu = await state.get_state()
    match menu:
        case UserMenu.history:
            new_stare = UserMenu.main
        case _:
            new_stare = UserMenu.main
    await state.set_state(new_stare)
    menu_keyboard, text = await create_user_keyboard(state)
    await callback.message.edit_text(
        text,
        reply_markup=menu_keyboard
    )
