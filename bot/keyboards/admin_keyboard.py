from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.markdown import hlink
from bot.states.states import AdminMenu, TrainingForm
from bot.texts.text import text_admin_menu as text_menu

from db.service import (
    get_all_users,
    get_workout_user_plan, get_workout_free_plan,
)


async def create_admin_keyboard(
        session: AsyncSession,
        state
) -> InlineKeyboardMarkup and str:
    current_state = await state.get_state()
    data = await state.get_data()
    keyboard_builder = InlineKeyboardBuilder()
    match current_state:
        case AdminMenu.main:
            text = text_menu["main"]
            keyboard_builder.add(InlineKeyboardButton(
                text="Сгенерировать код",
                callback_data="generate_code")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Поиск",
                callback_data="search_user")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Написать план тренировок",
                callback_data="get_users")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Написать общий план тренировок",
                callback_data="freePlanMenu")
            )
            return keyboard_builder.adjust(1).as_markup(), text
        case AdminMenu.users_menu:
            text = text_menu["chose_user"]
            search = ''
            page = 0
            if data.get("search_str"):
                search = data.get("search_str")
                await state.update_data(
                    search_str=''
                )
            if data.get("user_page"):
                page = data.get("user_page")
            users, max_pages = await get_all_users(session, page, search)
            await state.update_data(
                max_user_page=max_pages
            )
            row = []
            for user in users:
                keyboard_builder.add(
                    InlineKeyboardButton(
                        text=f"{user.name}",
                        callback_data=f"historyPlan_{user.telegram_id}")
                )
                row.append(1)
            if max_pages > 1:
                row.append(3)
                keyboard_builder.add(InlineKeyboardButton(
                    text="<<",
                    callback_data="userPaginator_back")
                )
                keyboard_builder.add(InlineKeyboardButton(
                    text=f"{page+1}/{max_pages}",
                    callback_data="userPaginator_info")
                )
                keyboard_builder.add(InlineKeyboardButton(
                    text=">>",
                    callback_data="userPaginator_next")
                )
            row.append(1)
            keyboard_builder.add(InlineKeyboardButton(
                text="Назад",
                callback_data="back_admin")
            )
            return keyboard_builder.adjust(*row).as_markup(), text
        case AdminMenu.training_users_menu:
            url = hlink(data["user_name"], f'tg://user?id={data["user_id"]}')
            text = f'{text_menu["history_train_menu"]}{url}'
            workout_plans = await get_workout_user_plan(
                session,
                data["user_id"]
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Написать новый план",
                callback_data="createPlan_")
            )
            for workout_plan in workout_plans:
                keyboard_builder.add(
                    InlineKeyboardButton(
                        text=f"{workout_plan.date.date()}",
                        callback_data=f"history_menu_{workout_plan.id}")
                )
            keyboard_builder.add(
                InlineKeyboardButton(text="Изменить имя пользователя", callback_data="edit_name")
            )
            keyboard_builder.add(
                InlineKeyboardButton(text="Удалить пользователя", callback_data="delete_user_menu")
            )
            keyboard_builder.add(
                InlineKeyboardButton(text="Назад", callback_data="back_admin")
            )
            return keyboard_builder.adjust(1).as_markup(), text
        case TrainingForm.form_menu:
            url = hlink(data["user_name"], f'tg://user?id={data["user_id"]}')
            text = f'{text_menu["data_chose_menu"]}{url}'
            keyboard_builder.add(InlineKeyboardButton(
                text="На сегодня",
                callback_data="selectDate_user_today")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="На завтра",
                callback_data="selectDate_user_tomorrow")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Своя дата",
                callback_data="selectDate_user_select")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Назад",
                callback_data="back_admin")
            )
            return keyboard_builder.adjust(1).as_markup(), text
        case TrainingForm.form_free_menu:
            text = f'{text_menu["data_chose_menu"]}Незарегистрированных пользователей'
            keyboard_builder.add(InlineKeyboardButton(
                text="На сегодня",
                callback_data="selectDate_free_today")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="На завтра",
                callback_data="selectDate_free_tomorrow")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Своя дата",
                callback_data="selectDate_free_select")
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Назад",
                callback_data="back_admin")
            )
            return keyboard_builder.adjust(1).as_markup(), text
        case AdminMenu.free_plan_menu:
            text = f'{text_menu["history_train_menu"]}Незарегистрированных пользователей'
            workout_plans = await get_workout_free_plan(
                session,
            )
            keyboard_builder.add(InlineKeyboardButton(
                text="Написать новый план",
                callback_data="createFreePlan_")
            )
            for workout_plan in workout_plans:
                keyboard_builder.add(
                    InlineKeyboardButton(
                        text=f"{workout_plan.date.date()}",
                        callback_data=f"free_history_menu_{workout_plan.id}")
                )
            keyboard_builder.add(
                InlineKeyboardButton(text="Назад", callback_data="back_admin")
            )
            return keyboard_builder.adjust(1).as_markup(), text
        case _:
            text = f'{text_menu["error"]}'
            keyboard_builder.add(InlineKeyboardButton(
                text="Ок",
                callback_data="back_admin")
            )
            return keyboard_builder.adjust(1).as_markup(), text
