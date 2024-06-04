from aiogram.fsm.state import StatesGroup, State


class AdminMenu(StatesGroup):
    main = State()

    training_main = State()
    users_menu = State()
    training_users_menu = State()
    training_history_menu = State()
    training_history_form = State()
    user_search = State()
    edit_name_form = State()
    edit_name_ok = State()

    free_plan_menu = State()
    free_training_history_menu = State()
    free_training_history_form = State()


class TrainingForm(StatesGroup):
    form_menu = State()
    form_date = State()
    form_training = State()
    form_edit_training = State()

    form_free_menu = State()
    form_free_training = State()
    form_free_date = State()


class Register(StatesGroup):
    start = State()
    code = State()
    name = State()


class UserMenu(StatesGroup):
    main = State()
    history = State()
