from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from db.service import get_workout_history
from bot.states.states import UserMenu
from bot.texts.text import text_user_menu as text_menu


async def create_user_keyboard(state) -> InlineKeyboardMarkup and str:
    current_state = await state.get_state()
    keyboard_builder = InlineKeyboardBuilder()
    match current_state:
        case UserMenu.main:
            text = text_menu["main"]
            keyboard_builder.add(
                InlineKeyboardButton(
                    text="Тренировка",
                    callback_data="get_training"
                )
            )
            keyboard_builder.add(
                InlineKeyboardButton(
                    text="Посмотреть историю тренировок",
                    callback_data="get_history"
                )
            )
            return keyboard_builder.adjust(1).as_markup(), text
        case _:
            keyboard_builder.add(InlineKeyboardButton(
                text="Ок",
                callback_data="user_back")
            )
            return keyboard_builder.adjust(1).as_markup(), text_menu["error"]


async def create_history_keyboard(
        session,
        telegram_id
) -> InlineKeyboardMarkup and str:
    workout_for_user = await get_workout_history(session, telegram_id)
    keyboard_builder = InlineKeyboardBuilder()
    text = text_menu["history_menu"]
    for workout in workout_for_user:
        keyboard_builder.add(
            InlineKeyboardButton(
                text=f"{workout.date.date()}",
                callback_data=f"userHistory_{workout.id}")
        )
    keyboard_builder.add(InlineKeyboardButton(
        text="Назад",
        callback_data="user_back")
    )
    return keyboard_builder.adjust(1).as_markup(), text
