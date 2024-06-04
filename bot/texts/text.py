from aiogram.utils.markdown import hcode, hbold

text_admin_menu = {
    "main": hbold("Главное меню"),
    "chose_user": hbold("Выберите пользоветеля"),
    "history_train_menu": hbold("Создание и редактирование тренировок для:\n"),
    "data_chose_menu": hbold("Выберите дату тренировки для:\n"),
    "data_create_form": hbold("Ведите дату в формате:\n")+hcode('2024-05-16'),
    "workout_create_form": hbold("Введите план тренировок"),
    "form_date_error": hbold("Неверный формат даты\n")+hcode('2024-05-16'),
    "edit_workout_ok": hbold("План тренировки изменен"),
    "error": hbold("Ошибка"),
    "search": hbold("Введите имя пользователя:"),
    "new_name": hbold("Имя изменено"),
    "name_menu": hbold("Введите новое имя для:\n"),
    "delete_user": hbold("Удалить пользователя?\n"),
    "delete_user_ok": hbold("Пользователь удален\n")
}


text_user_menu = {
    "main": hbold("Главное меню"),
    "error": hbold("Ошибка"),
    "not_training": hbold("Нет тренировки на сегодня"),
    "history_menu": hbold("История тренировок")
}


text_register_menu = {
    "user_menu": hbold("Главное меню"),
    "reg_start": hbold("Аккаунт не найден"),
    "code": hbold("Введите код:"),
    "error_code": hbold("Нет такого кода"),
    "name": hbold("Введите ФИО:"),
    "reg_end": hbold("Регистрация прошла успешно")
}
