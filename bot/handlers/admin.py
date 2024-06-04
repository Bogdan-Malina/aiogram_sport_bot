import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    CallbackQuery
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.markdown import hlink, hcode, hbold, hitalic, hunderline
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboards.admin_keyboard import create_admin_keyboard
from bot.states.states import AdminMenu, TrainingForm
from bot.texts.text import text_admin_menu as text_menu

from db.service import (
    get_user,
    create_code,
    create_workout_plan,
    get_workout,
    update_workout_plan, edit_user_name, create_free_workout_plan, get_free_workout, update_free_workout_plan,
    delete_user
)
from db.models.schemas import WorkoutPlan as WorkoutPlanDC, FreeWorkoutPlan as FreeWorkoutPlanDC

router = Router()


@router.message(Command("admin"))
async def start_amin_menu(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    await state.clear()
    admin = await get_user(session, message.from_user.id, True)
    if admin:
        await state.update_data(
            admin=True
        )
        await state.set_state(AdminMenu.main)
        menu_keyboard, text = await create_admin_keyboard(session, state)
        await message.answer(
            text,
            reply_markup=menu_keyboard,
        )


@router.callback_query(F.data.startswith("generate_code"))
async def generate_code(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    code = await create_code(session)
    await callback.message.answer(
        hcode(f'{code.code}'),
    )
    await callback.message.delete()
    menu_keyboard, text = await create_admin_keyboard(session, state)
    await callback.message.answer(
        text,
        reply_markup=menu_keyboard,
    )


@router.callback_query(F.data.startswith("get_users"))
async def get_users(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(AdminMenu.users_menu)
    await state.update_data(
        user_page=0
    )
    menu_keyboard, text = await create_admin_keyboard(
        session,
        state
    )
    await callback.message.edit_text(
        text,
        reply_markup=menu_keyboard
    )


@router.callback_query(F.data.startswith("userPaginator_"))
async def paginator(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    page = callback.data.split("_")[-1]
    if data.get("user_page") is not None:
        if page == "next":
            if data["user_page"]+1 != data["max_user_page"]:
                await state.update_data(
                    user_page=data["user_page"] + 1
                )
                menu_keyboard, text = await create_admin_keyboard(
                    session,
                    state
                )
                await callback.message.edit_text(
                    text,
                    reply_markup=menu_keyboard
                )
            else:
                await callback.answer("Вы на последней странице")
        elif page == "back":
            if data["user_page"] != 0:
                await state.update_data(
                    user_page=data["user_page"] - 1
                )
                menu_keyboard, text = await create_admin_keyboard(
                    session,
                    state
                )
                await callback.message.edit_text(
                    text,
                    reply_markup=menu_keyboard
                )
            else:
                await callback.answer("Вы на первой странице")
        elif page == "info":
            await callback.answer(f'{data["user_page"]+1}')
    else:
        menu_keyboard = InlineKeyboardBuilder()
        menu_keyboard.add(InlineKeyboardButton(
            text="Ок",
            callback_data="back_admin")
        )
        await callback.message.edit_text(
            text_menu["error"],
            reply_markup=menu_keyboard.as_markup()
        )


@router.callback_query(F.data.startswith("historyPlan_"))
async def get_history_training(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(AdminMenu.training_users_menu)
    user_id = int(callback.data.split("_")[-1])
    user = await get_user(session, user_id)
    await state.update_data(
        user_id=user_id,
        user_name=user.name
    )
    menu_keyboard, text = await create_admin_keyboard(session, state)
    await callback.message.edit_text(
        text,
        reply_markup=menu_keyboard
    )


@router.callback_query(F.data.startswith("history_menu_"))
async def history_menu(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(AdminMenu.training_history_menu)
    data = int(callback.data.split("_")[-1])
    training = await get_workout(session, data)
    menu_keyboard = InlineKeyboardBuilder()
    menu_keyboard.add(InlineKeyboardButton(
        text="Редактировать",
        callback_data=f"history_edit_{training.id}")
    )
    menu_keyboard.add(InlineKeyboardButton(
        text="Отмена",
        callback_data="back_admin")
    )
    text = (f"{hunderline(training.date.date())}\n\n"
            f"{hitalic(training.description)}")
    await callback.message.edit_text(
        text,
        reply_markup=menu_keyboard.adjust(1).as_markup(),
    )


@router.callback_query(F.data.startswith("history_edit_"))
async def history_edit(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(AdminMenu.training_history_form)
    await state.update_data(
        menu=callback.message,
        training_id=int(callback.data.split("_")[-1])
    )
    menu_keyboard = InlineKeyboardBuilder()
    menu_keyboard.add(
        InlineKeyboardButton(text="Отмена", callback_data="back_admin")
    )
    await callback.message.edit_text(
        text_menu["workout_create_form"],
        reply_markup=menu_keyboard.adjust(1).as_markup(),
    )


@router.message(AdminMenu.training_history_form)
async def edit_workout(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    text = message.text
    menu_keyboard = InlineKeyboardBuilder()
    menu_keyboard.add(
        InlineKeyboardButton(text="Ок", callback_data="back_admin")
    )
    await update_workout_plan(session, data["training_id"], text)
    await data["menu"].delete()
    await state.set_state(AdminMenu.training_history_menu)
    await message.answer(
        text_menu["edit_workout_ok"],
        reply_markup=menu_keyboard.adjust(1).as_markup()
    )


@router.callback_query(F.data.startswith("createPlan_"))
async def create_plan(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(TrainingForm.form_menu)
    menu_keyboard, text = await create_admin_keyboard(session, state)
    await callback.message.edit_text(
        text,
        reply_markup=menu_keyboard
    )


@router.callback_query(F.data.startswith("selectDate_"))
async def select_date(callback: CallbackQuery, state: FSMContext):
    states = {
        "user": [TrainingForm.form_training, TrainingForm.form_date],
        "free": [TrainingForm.form_free_training, TrainingForm.form_free_date]
    }
    free_or_user = callback.data.split("_")[-2]
    command = callback.data.split("_")[-1]
    date = datetime.date.today()
    buttons = [
        [InlineKeyboardButton(text="Отмена", callback_data="back_admin")],
    ]
    menu_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await state.update_data(menu=callback.message)
    match command:
        case "today":
            text = (f'{text_menu["workout_create_form"]}'
                    f' {hbold("на")} {hcode(date)}')
            await state.update_data(date=date)
            await state.set_state(states.get(free_or_user)[0])
            await callback.message.edit_text(
                text,
                reply_markup=menu_keyboard
            )
        case "tomorrow":
            date += datetime.timedelta(days=1)
            text = (f'{text_menu["workout_create_form"]} '
                    f'{hbold("на")} {hcode(date)}')
            await state.update_data(date=date)
            await state.set_state(states.get(free_or_user)[0])
            await callback.message.edit_text(
                text,
                reply_markup=menu_keyboard
            )
        case "select":
            await callback.message.edit_text(
                text_menu["data_create_form"],
                reply_markup=menu_keyboard
            )
            await state.set_state(states.get(free_or_user)[1])


@router.callback_query(F.data.startswith("back_admin"))
async def back_key(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    menu = await state.get_state()
    data = await state.get_data()
    print(menu)
    if data.get("admin"):
        match menu:
            case AdminMenu.users_menu:
                new_state = AdminMenu.main
            case AdminMenu.training_users_menu:
                new_state = AdminMenu.users_menu
            case AdminMenu.training_history_menu:
                new_state = AdminMenu.training_users_menu
            case AdminMenu.edit_name_form:
                new_state = AdminMenu.training_users_menu
            case AdminMenu.edit_name_ok:
                new_state = AdminMenu.training_users_menu
            case TrainingForm.form_menu:
                new_state = AdminMenu.training_users_menu
            case TrainingForm.form_date:
                new_state = TrainingForm.form_menu
            case TrainingForm.form_free_menu:
                new_state = AdminMenu.free_plan_menu
            case TrainingForm.form_free_training:
                new_state = TrainingForm.form_free_menu
            case TrainingForm.form_free_date:
                new_state = TrainingForm.form_free_menu
            case TrainingForm.form_training:
                new_state = TrainingForm.form_menu
            case AdminMenu.free_training_history_menu:
                new_state = AdminMenu.free_plan_menu
            case AdminMenu.free_training_history_form:
                new_state = AdminMenu.free_plan_menu
            case AdminMenu.training_history_form:
                new_state = AdminMenu.training_users_menu
            case _:
                new_state = AdminMenu.main
        await state.set_state(new_state)
        menu_keyboard, text = await create_admin_keyboard(session, state)
        await callback.message.edit_text(
            text,
            reply_markup=menu_keyboard
        )
    else:
        admin = await get_user(session, callback.from_user.id, True)
        if admin:
            await state.update_data(
                admin=True
            )
            await state.set_state(AdminMenu.main)
            menu_keyboard, text = await create_admin_keyboard(session, state)
            await callback.message.edit_text(
                text,
                reply_markup=menu_keyboard
            )
        else:
            await callback.message.delete()


@router.message(TrainingForm.form_date)
async def edit_date(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["menu"].delete()

    date_str = message.text
    buttons = [
        [InlineKeyboardButton(text="Отмена", callback_data="back_admin")],
    ]
    menu_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        await state.update_data(date=date)
        await state.set_state(TrainingForm.form_training)
        new_msg = await message.answer(
            text_menu["workout_create_form"],
            reply_markup=menu_keyboard
        )
    except ValueError:
        buttons = [
            [InlineKeyboardButton(text="Отмена", callback_data="back_admin")]
        ]
        menu_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        new_msg = await message.answer(
            text_menu["form_date_error"],
            reply_markup=menu_keyboard
        )
    await state.update_data(menu=new_msg)


@router.message(TrainingForm.form_free_date)
async def edit_free_date(message: Message, state: FSMContext):
    data = await state.get_data()
    await data["menu"].delete()

    date_str = message.text
    buttons = [
        [InlineKeyboardButton(text="Отмена", callback_data="back_admin")],
    ]
    menu_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    try:
        date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        await state.update_data(date=date)
        await state.set_state(TrainingForm.form_free_training)
        new_msg = await message.answer(
            text_menu["workout_create_form"],
            reply_markup=menu_keyboard
        )
    except ValueError:
        buttons = [
            [InlineKeyboardButton(text="Отмена", callback_data="back_admin")]
        ]
        menu_keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        new_msg = await message.answer(
            text_menu["form_date_error"],
            reply_markup=menu_keyboard
        )
    await state.update_data(menu=new_msg)


@router.message(TrainingForm.form_training)
async def edit_training(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    await data["menu"].delete()

    description = message.text

    workout_plan = WorkoutPlanDC(
        description=description,
        user_id=data["user_id"],
        date=data["date"]
    )

    await create_workout_plan(session, workout_plan)
    url = hlink(data["user_name"], f'tg://user?id={data["user_id"]}')
    date = hcode(data["date"])
    text = (f'{hbold("Добавлен план тренировок для")} '
            f'{url} {hbold("на")} {date}:\n'
            f'{hitalic(description)}')
    await message.answer(
        text
    )

    await state.set_state(TrainingForm.form_menu)
    await get_user(session, data["user_id"])
    menu_keyboard, text = await create_admin_keyboard(session, state)
    await message.answer(
        text,
        reply_markup=menu_keyboard
    )


@router.message(TrainingForm.form_free_training)
async def edit_free_training(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    await data["menu"].delete()

    description = message.text

    workout_plan = FreeWorkoutPlanDC(
        description=description,
        date=data["date"]
    )

    await create_free_workout_plan(session, workout_plan)
    date = hcode(data["date"])
    text = (f'{hbold("Добавлен план тренировок для")} '
            f'Незарегистрированных пользователей {hbold("на")} {date}:\n'
            f'{hitalic(description)}')
    await message.answer(
        text
    )

    await state.set_state(TrainingForm.form_free_menu)
    menu_keyboard, text = await create_admin_keyboard(session, state)
    await message.answer(
        text,
        reply_markup=menu_keyboard
    )


@router.callback_query(F.data.startswith("search_user"))
async def search_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AdminMenu.user_search)
    await state.update_data(
        menu=callback.message,
        user_page=0
    )
    keyboard_search = InlineKeyboardBuilder()
    keyboard_search.add(
        InlineKeyboardButton(text="Отмена", callback_data="back_admin")
    )
    await callback.message.edit_text(
        text_menu["search"],
        reply_markup=keyboard_search.as_markup()
    )


@router.message(AdminMenu.user_search)
async def search_form(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    text = message.text.upper()
    data = await state.get_data()
    await state.set_state(AdminMenu.users_menu)
    await state.update_data(
        search_str=text
    )
    search_res, text = await create_admin_keyboard(session, state)
    await message.answer(
        text,
        reply_markup=search_res
    )
    await data["menu"].delete()


@router.callback_query(F.data.startswith("edit_name"))
async def edit_name(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(AdminMenu.edit_name_form)
    await state.update_data(
        menu=callback.message
    )
    data = await state.get_data()
    keyboard_edit = InlineKeyboardBuilder()
    keyboard_edit.add(
        InlineKeyboardButton(text="Отмена", callback_data="back_admin")
    )
    url = hlink(data["user_name"], f'tg://user?id={data["user_id"]}')
    await callback.message.edit_text(
        f"{text_menu["name_menu"]}{url}",
        reply_markup=keyboard_edit.as_markup()
    )


@router.callback_query(F.data.startswith("delete_user_menu"))
async def delete_user_menu(
        callback: CallbackQuery,
        state: FSMContext
):
    data = await state.get_data()
    keyboard_edit = InlineKeyboardBuilder()
    keyboard_edit.add(
        InlineKeyboardButton(text="Да", callback_data="delete_user")
    )
    keyboard_edit.add(
        InlineKeyboardButton(text="Отмена", callback_data="back_admin")
    )
    url = hlink(data["user_name"], f'tg://user?id={data["user_id"]}')
    await callback.message.edit_text(
        f"{text_menu["delete_user"]}{url}",
        reply_markup=keyboard_edit.adjust(2).as_markup()
    )


@router.callback_query(F.data.startswith("delete_user"))
async def delete_user_handler(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    await delete_user(session, data["user_id"])
    await state.update_data(
        user_id=False
    )
    keyboard_edit = InlineKeyboardBuilder()
    keyboard_edit.add(
        InlineKeyboardButton(text="Ок", callback_data="back_admin")
    )
    await callback.message.edit_text(
        f"{text_menu["delete_user_ok"]}",
        reply_markup=keyboard_edit.adjust(2).as_markup()
    )


@router.message(AdminMenu.edit_name_form)
async def edit_form(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    new_name = message.text.upper()
    data = await state.get_data()
    keyboard_back = InlineKeyboardBuilder()
    keyboard_back.add(
        InlineKeyboardButton(text="Ок", callback_data="back_admin")
    )
    await edit_user_name(session, data["user_id"], new_name)
    await state.update_data(
        user_name=new_name
    )
    await state.set_state(AdminMenu.edit_name_ok)
    await message.answer(
        text_menu["new_name"],
        reply_markup=keyboard_back.as_markup()
    )
    await data["menu"].delete()


@router.callback_query(F.data.startswith("freePlanMenu"))
async def free_plan_menu(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(AdminMenu.free_plan_menu)
    await state.update_data(
        menu=callback.message
    )
    keyboard_free_plan, text = await create_admin_keyboard(session, state)
    await callback.message.edit_text(
        text,
        reply_markup=keyboard_free_plan
    )


@router.callback_query(F.data.startswith("createFreePlan_"))
async def create_free_plan(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(TrainingForm.form_free_menu)
    menu_keyboard, text = await create_admin_keyboard(session, state)
    await callback.message.edit_text(
        text,
        reply_markup=menu_keyboard
    )


@router.callback_query(F.data.startswith("free_history_menu_"))
async def history_free_menu(
        callback: CallbackQuery,
        state: FSMContext,
        session: AsyncSession
):
    await state.set_state(AdminMenu.free_training_history_menu)
    data = int(callback.data.split("_")[-1])
    training = await get_free_workout(session, data)
    menu_keyboard = InlineKeyboardBuilder()
    menu_keyboard.add(InlineKeyboardButton(
        text="Редактировать",
        callback_data=f"free_history_edit_{training.id}")
    )
    menu_keyboard.add(InlineKeyboardButton(
        text="Отмена",
        callback_data="back_admin")
    )
    text = (f"{hunderline(training.date.date())}\n\n"
            f"{hitalic(training.description)}")
    await callback.message.edit_text(
        text,
        reply_markup=menu_keyboard.adjust(1).as_markup(),
    )


@router.callback_query(F.data.startswith("free_history_edit_"))
async def history_free_edit(
        callback: CallbackQuery,
        state: FSMContext
):
    await state.set_state(AdminMenu.free_training_history_form)
    await state.update_data(
        menu=callback.message,
        training_id=int(callback.data.split("_")[-1])
    )
    menu_keyboard = InlineKeyboardBuilder()
    menu_keyboard.add(
        InlineKeyboardButton(text="Отмена", callback_data="back_admin")
    )
    await callback.message.edit_text(
        text_menu["workout_create_form"],
        reply_markup=menu_keyboard.adjust(1).as_markup(),
    )


@router.message(AdminMenu.free_training_history_form)
async def edit_free_workout(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    data = await state.get_data()
    text = message.text
    menu_keyboard = InlineKeyboardBuilder()
    menu_keyboard.add(
        InlineKeyboardButton(text="Ок", callback_data="back_admin")
    )
    await update_free_workout_plan(session, data["training_id"], text)
    await data["menu"].delete()
    await state.set_state(AdminMenu.free_training_history_menu)
    await message.answer(
        text_menu["edit_workout_ok"],
        reply_markup=menu_keyboard.adjust(1).as_markup()
    )
