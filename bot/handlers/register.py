from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hunderline
from sqlalchemy.ext.asyncio import AsyncSession

from db.service import get_user, get_code, create_user, get_free_workout_for_user
from db.models.schemas import User as UserDC

from bot.handlers.user import UserMenu

from bot.keyboards.user_keyboard import create_user_keyboard
from bot.texts.text import text_register_menu as text_menu, text_user_menu
from bot.states.states import Register

router = Router()


@router.message(Command("start"))
async def start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    user = await get_user(session, message.from_user.id)
    keyboard = InlineKeyboardBuilder()
    if not user:
        await state.set_state(Register.start)
        keyboard.add(InlineKeyboardButton(
            text="Регистрация",
            callback_data="reg_code")
        )
        keyboard.add(InlineKeyboardButton(
            text="Получить общую тренировку",
            callback_data="get_not_auth")
        )
        await message.answer(
            text_menu["reg_start"],
            reply_markup=keyboard.adjust(1).as_markup()
        )
    else:
        await state.set_state(UserMenu.main)
        keyboard, text = await create_user_keyboard(state)
        await message.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("reg_code"), Register.start)
async def reg(callback: CallbackQuery, state: FSMContext):
    await state.update_data(
        menu=callback.message,
    )
    await state.set_state(Register.code)
    await callback.message.edit_text(text_menu["code"])


@router.message(Register.code)
async def form_code(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    code = await get_code(session, message.text)
    if not code:
        await message.answer(text_menu["error_code"])
    else:
        await state.update_data(code=message.text)
        await message.answer(text_menu["name"])
        await state.set_state(Register.name)


@router.message(Register.name)
async def form_name(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    name = message.text.upper()
    telegram_id = message.from_user.id
    data = await state.get_data()

    user = UserDC(
        telegram_id=telegram_id,
        name=name,
        code=data['code']
    )
    await create_user(session, user)

    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text="Ок", callback_data="user_menu"))
    await state.clear()
    await message.answer(
        text_menu["reg_end"],
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(F.data.startswith("get_not_auth"))
async def delete_user_handler(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    workout_for_user = await get_free_workout_for_user(session)
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
            text_user_menu["not_training"]
        )
    keyboard = InlineKeyboardBuilder()
    await state.set_state(Register.start)
    keyboard.add(InlineKeyboardButton(
        text="Регистрация",
        callback_data="reg_code")
    )
    keyboard.add(InlineKeyboardButton(
        text="Получить общую тренировку",
        callback_data="get_not_auth")
    )
    await callback.message.delete()
    await callback.message.answer(
        text_menu["reg_start"],
        reply_markup=keyboard.adjust(1).as_markup()
    )
