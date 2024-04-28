from menu_manager import (
    local_language_menu,
    STUDENT,
    TEACHER,
    GROUP,
    INDIVIDUAL,
    PAIR,
    YES,
    NO,
    LEVEL
)

import menu_manager as mm

import re

from config import router, bot
from state_manager import Form
from translations import translate_text

from aiogram import types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext

from aiogram.types import CallbackQuery, Message

from datetime import datetime

import database_manager as db
import handler_manager as dm

# Обработчик команды /start
@router.message(CommandStart())
async def handle_start(message: types.Message, state: FSMContext):
    await state.set_state(Form.type)
    if db.check_student(id=message.from_user.id) == True:
        await state.set_state(Form.student)
        await message.answer(
            translate_text("С возвращением в школу Express Polish", db.get_lang(message.from_user.id)),
            reply_markup=mm.get_student_account_menu(db.get_lang(message.from_user.id))
        )
    elif db.check_teacher(id=message.from_user.id) == True:
        await state.set_state(Form.teacher)
        await message.answer(
            translate_text("С возвращением в школу Express Polish", db.get_lang(message.from_user.id)),
            reply_markup=mm.get_teacher_account_menu(db.get_lang(message.from_user.id))
        )
    else:
        await message.reply(
            "Welcome to the Polish language school.\nDo you have an account?",
            reply_markup=mm.get_type_menu(db.get_lang(message.from_user.id))
        )
        
@router.message(Command('student'))
async def handle_start(message: types.Message, state: FSMContext):
    await message.reply(
            "Welcome to the Polish language school.\nDo you have an account?",
            reply_markup=mm.get_type_menu(db.get_lang(message.from_user.id))
        )
    
@router.message(Command('teacher'))
async def handle_start(message: types.Message, state: FSMContext):
    await message.reply(
            "Welcome to the Polish language school.\nDo you have an account?",
            reply_markup=mm.get_type_menu(db.get_lang(message.from_user.id))
        )
    
@router.message(Command('admin'))
async def handle_start(message: types.Message, state: FSMContext):
    if db.check_admin(id=message.from_user.id) == True:
        await message.answer(
            "Welcome to the Express Polish",
            reply_markup=mm.get_admin_account_menu(db.get_lang(message.from_user.id))
        )
    else:
        await message.answer(
            translate_text("Введите код администратора.", db.get_lang(message.from_user.id))
        )
        await state.set_state(Form.admin_password)

@router.message(Form.admin_password)
async def get_admin_password(message: Message, state: FSMContext):
    if message.text == "AdminExpressPolish":
        await message.answer(translate_text("Код принят.\nВведите фамилию и имя.", db.get_lang(message.from_user.id)))
        await state.set_state(Form.admin_fullname)
    else:
        await message.answer(
            translate_text("Код не принят.\nПопробуйте ещё раз.", db.get_lang(message.from_user.id)),
            reply_markup=mm.get_registration_menu(db.get_lang(message.from_user.id))
        )

@router.message(Form.admin_fullname)
async def set_admin_fullname(message: Message, state: FSMContext) -> None:
    await state.set_state()

    db.add_admin(id = message.from_user.id, fullname = message.text)

    await message.answer(
        translate_text("Благодарим за регистрацию. Вот ваш аккаутн", db.get_lang(message.from_user.id)),
        reply_markup=mm.get_admin_account_menu(db.get_lang(message.from_user.id))
    )

@router.callback_query(F.data == YES)
async def check_account(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(has_account="yes")
    await callback.message.edit_text(
        
        reply_markup=mm.get_registration_menu(db.get_lang(callback.from_user.id))
    )

@router.callback_query(F.data == NO)
async def check_account(callback: CallbackQuery, state: FSMContext) -> None:
    await state.update_data(has_account="no")
    await callback.message.edit_text(
        "Choose who you are.",
        reply_markup=mm.get_registration_menu(db.get_lang(callback.from_user.id))
    )

@router.callback_query(F.data == TEACHER)
async def check_teacher(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    has_account = user_data.get('has_account')
    await state.update_data(type = "teacher")

    if has_account == "yes":
        await callback.message.edit_text(
            translate_text("С возвращением в школу Express Polish", db.get_lang(callback.from_user.id)),
            reply_markup=mm.get_teacher_account_menu(db.get_lang(callback.from_user.id))
        )
    elif has_account == "no":
        await state.set_state(Form.teacher_password)
        await callback.message.edit_text(
            f"{callback.from_user.username}, enter the teacher access code."
        )

@router.message(Form.teacher_password)
async def get_teacher_password(message: Message, state: FSMContext):
    if message.text == "TeacherExpressPolish":
        await message.answer(
            "Success.\nChoose language.",
            reply_markup=local_language_menu
        )
        await state.update_data(type = "teacher")
        db.add_teacher(message.from_user.id)
    else:
        await message.answer(
            translate_text("Код не принят.\nПопробуйте ещё раз.", db.get_lang(message.from_user.id)),
            reply_markup=mm.get_registration_menu(db.get_lang(message.from_user.id))
        )


@router.callback_query(F.data == STUDENT)
async def check_student(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    has_account = user_data.get('has_account')
    await state.update_data(type = "student")

    db.add_student(callback.from_user.id)

    if has_account == "yes":
        await callback.message.edit_text(
            translate_text("С возвращением в школу Express Polish", db.get_lang(callback.from_user.id)),
            reply_markup=mm.get_student_account_menu(db.get_lang(callback.from_user.id))
        )
    elif has_account == "no":
        await callback.message.edit_text(
            f"{callback.from_user.username}, choose language.",
            reply_markup=mm.local_language_menu
        )

@router.callback_query(F.data.startswith('lang'))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    type = user_data.get('type')
    lang = callback.data[5:]

    db.add_user_lang(callback.from_user.id, lang)

    await callback.message.answer(
        translate_text("Вы выбрали язык. Введите фамилию и имя.", db.get_lang(callback.from_user.id)),
    )

    if type == "student":
        await state.set_state(Form.student_fullname)
    elif type == "teacher":
        await state.set_state(Form.teacher_fullname)

@router.message(Form.teacher_fullname)
async def add_teacher(message: Message, state: FSMContext):
    await state.set_state(Form.teacher)

    db.add_teacher_fullname(id = message.from_user.id, fullname = message.text)

    await message.answer(
        translate_text("Вы зарегестрировались в Express Polish.", db.get_lang(message.from_user.id)),
        reply_markup=mm.get_teacher_account_menu(db.get_lang(message.from_user.id))
    )

@router.message(Form.student_fullname)
async def add_student(message: Message, state: FSMContext):
    await state.set_state(Form.lesson_view)

    db.add_student_fullname(id = message.from_user.id, fullname = message.text)

    await message.answer(
        translate_text("Введите вид занятия.", db.get_lang(message.from_user.id)),
        reply_markup=await dm.create_lesson_view_menu(db.get_lang(message.from_user.id))
    )

@router.message(Form.add_group)
async def add_group(message: Message, state: FSMContext):
    words = message.text.split(", ")
    if len(words) > 0:
        level_conversion = {
            "c1": 6,
            "c2": 5,
            "b1": 4,
            "b2": 3,
            "a1": 2,
            "a2": 1,
            "a0": 0
        }
        levels = []
        await message.answer(
            translate_text("Уровни получены успешно.\nВыберите вид группы.", db.get_lang(message.from_user.id)),
            reply_markup=mm.get_lesson_view_menu(db.get_lang(message.from_user.id))
        )
        for word in words:
            level = level_conversion.get(word.lower())
            await state.update_data(type = "teacher")

            if level is not None:
                levels.append(level)
            else:
                await message.answer(
                    translate_text("Неверный формат ввода, попробуйте ещё раз.", db.get_lang(message.from_user.id))
                )
                return
            
        db.add_levels_in_group(message.from_user.id, levels)
    else:
        await message.answer(
            translate_text("Неверный формат ввода, попробуйте ещё раз.", db.get_lang(message.from_user.id))
        )

@router.callback_query((F.data.startswith(GROUP)) | (F.data.startswith(INDIVIDUAL)) | (F.data.startswith(PAIR)))
async def add_lesson_view(callback: CallbackQuery, state: FSMContext):

    user_data = await state.get_data()
    has_account = user_data.get('type')

    group_conversion = {
        "group": 3,
        "pair": 2,
        "individual": 1
    }

    if has_account == 'teacher':
        select_group = callback.data
        group = group_conversion.get(select_group)

        await state.update_data(group_level = group)
        
        await state.set_state(Form.teacher)
        db.add_group_level(callback.from_user.id, group)
        await callback.message.answer(
            translate_text("Группа успешно добавлена.", db.get_lang(callback.from_user.id)),
            reply_markup=mm.get_teacher_account_menu(db.get_lang(callback.from_user.id))
        )
    else:
        select_group, _ = callback.data.split('_')
        group = group_conversion.get(select_group)

        await state.update_data(group_level = group)

        if group is not None:
            db.add_student_group_view(callback.from_user.id, group)
            await callback.message.answer(
                translate_text("Выберите ваш уровень языка.", db.get_lang(callback.from_user.id)),
                reply_markup=await dm.create_language_level_menu(group, db.get_lang(callback.from_user.id))
            )
        else:
            await callback.message.answer(
                translate_text("Неверный ответ. Попробуйте ещё раз.", db.get_lang(callback.from_user.id)),
                reply_markup=await dm.create_lesson_view_menu(db.get_lang(callback.from_user.id))
            )

@router.callback_query(F.data.startswith(LEVEL))
async def add_lesson_view(callback: CallbackQuery, state: FSMContext):
    level_conversion = {
        "c1": 6,
        "c2": 5,
        "b1": 4,
        "b2": 3,
        "a1": 2,
        "a2": 1,
        "a0": 0
    }

    selected_level = callback.data[len("LEVEL_"):]
    level = level_conversion.get(selected_level)

    if level is not None:
        user_data = await state.get_data()
        group_view = user_data.get('group_level')

        db.add_student_level(callback.from_user.id, group_view, level)
        await state.set_state(Form.student)
        await callback.message.answer(
            translate_text("Выберите номер группы", db.get_lang(callback.from_user.id)),
            reply_markup=dm.create_group_id_menu(callback.from_user.id, db.get_lang(callback.from_user.id))
        )
    else:
        await callback.message.answer(
            translate_text("Неверный ответ. Попробуйте ещё раз.", db.get_lang(callback.from_user.id)),
            reply_markup=mm.get_language_level_menu(db.get_lang(callback.from_user.id))
        )

@router.callback_query(F.data.startswith("gr_id_"))
async def choose_group(callback: CallbackQuery, state: FSMContext):
    _, _, id = callback.data.split('_')
    db.add_student_group(callback.from_user.id, id)

    await callback.message.answer(
        translate_text("Благодарим за регистрацию. Вот ваш аккаутн:", db.get_lang(callback.from_user.id)),
        reply_markup=mm.get_student_account_menu(callback.from_user.id)
    )

@router.callback_query(lambda c: c.data.startswith('del_group_'))
async def delete_group(callback: CallbackQuery, state: FSMContext):
    _, _, index = callback.data.split('_')
    try:
        db.delete_group(index)
        await callback.message.answer(
            translate_text("Группа успешно удалина", db.get_lang(callback.from_user.id))
        )
    except Exception as e:
        await callback.message.answer(
            translate_text("По какой-то причине группа не была найдена, если она осталась, то обратитесь к админу.", db.get_lang(callback.from_user.id))
        )

@router.callback_query(lambda c: c.data.startswith('choose_group_'))
async def set_homework(callback: CallbackQuery, state: FSMContext):
    _, _, index = callback.data.split('_')
    if db.get_payload_check(callback.from_user.id, index) is not True:
        await state.update_data(type=index)
        await callback.message.answer(
            translate_text("Отправьте документ, который необходимо отправить.", db.get_lang(callback.from_user.id))
        )
    else:
        await callback.message.answer(
            translate_text("Вы ещё не оплатили курс. Хотите перейти к оплате?", db.get_lang(callback.message.from_user.id)),
            reply_markup=mm.get_choose_of_payload_menu(index, db.get_lang(callback.message.from_user.id))
        )


@router.message((F.text.lower() == 'добавить группу') | (F.text.lower() == 'add a group') | (F.text.lower() == 'dodaj grupę') | (F.text.lower() == 'додати групу'))
async def add_group(message: Message, state: FSMContext):
    await message.answer(
        translate_text("Введите уровни языка, которые могут находится в группе.", db.get_lang(message.from_user.id))
    )

    await state.set_state(Form.add_group)

@router.message((F.text.lower() == 'удалить группу') | (F.text.lower() == 'delete group') | (F.text.lower() == 'usuń grupę') | (F.text.lower() == 'видалити групу'))
async def delete_group(message: Message, state: FSMContext):
    await message.answer(
        translate_text("Выберите группу для удаления.", db.get_lang(message.from_user.id)),
        reply_markup=dm.create_groups_menu(message.from_user.id, 1, 1, db.get_lang(message.from_user.id))
    )

@router.message((F.text.lower() == "удалить аккаунт") | (F.text.lower() == 'delete account') | (F.text.lower() == 'usuń konto') | (F.text.lower() == 'видалити обліковий запис'))
async def delete_account(message: Message, state: FSMContext):
    await message.answer(
        translate_text("Ваш аккаунт удалён, напишите команду /start для создания аккаунта.", db.get_lang(message.from_user.id))
    )
    db.delete_account(message.from_user.id)

@router.message((F.text.lower() == 'мой аккаунт') | (F.text.lower() == 'my account') | (F.text.lower() == 'moje konto') | (F.text.lower() == 'мій обліковий запис'), Form.teacher)
async def view_account(message: Message, state: FSMContext):
    await message.reply(f"{translate_text('Вот ваш аккаунт.', db.get_lang(message.from_user.id))}\n{db.get_teacher_account(message.from_user.id, db.get_lang(message.from_user.id))}")

@router.message((F.text.lower() == 'мой аккаунт') | (F.text.lower() == 'my account') | (F.text.lower() == 'moje konto') | (F.text.lower() == 'мій обліковий запис'), Form.student)
async def view_account(message: Message, state: FSMContext):
    await message.reply(f"{translate_text('Вот ваш аккаунт.', db.get_lang(message.from_user.id))}\n{db.get_student_account(message.from_user.id, db.get_lang(message.from_user.id))}")

@router.message((F.text.lower() == 'мой аккаунт') | (F.text.lower() == 'my account') | (F.text.lower() == 'moje konto') | (F.text.lower() == 'мій обліковий запис'))
async def view_account(message: Message, state: FSMContext):
    await message.reply(f"{translate_text('Вот ваш аккаунт.', db.get_lang(message.from_user.id))}\n{db.get_admin_account(message.from_user.id, db.get_lang(message.from_user.id))}")

@router.message((F.text.lower() == "отправить домашнее задание") | (F.text.lower() == 'submit homework') | (F.text.lower() == 'prześlij zadanie domowe') | (F.text.lower() == 'Надіслати домашнє завдання'), Form.teacher)
async def set_homework(message: Message, state: FSMContext):
    await message.answer(
        translate_text("Выберите группу для отправки", db.get_lang(message.from_user.id)),
        reply_markup=dm.create_groups_menu(message.from_user.id, 2, 1, db.get_lang(message.from_user.id))
    )

@router.message(Form.set_price)
async def set_price(message: Message, state: FSMContext):
    price = message.text.strip()
    digits_pattern = r'^\d+$'

    await state.set_state()
    
    if re.match(digits_pattern, price):
        db.add_price(message.from_user.id, price)
        await message.answer("Цена успешно добавлена",
                                reply_markup=mm.get_admin_account_menu(db.get_lang(message.from_user.id))
                            )
    else:
        await return_to_menu(message)

@router.message((F.text.lower() == 'установить цену на занятие') | (F.text.lower() == 'set the price for classes') | (F.text.lower() == 'ustal cenę za zajęcia') | (F.text.lower() == 'додати картку для оплати'))
async def set_price(message: Message, state: FSMContext):
    await message.answer("Введите цену одного занятия в долларах")
    await state.set_state(Form.set_price)

@router.message((F.text.lower() == 'добавить карту') | (F.text.lower() == 'add a card') | (F.text.lower() == 'dodaj kartę do płatności') | (F.text.lower() == 'додати картку для оплати'))
async def add_admin_card(message: Message, state: FSMContext):
    await message.answer("Введите номер карточки")
    await state.set_state(Form.admin_card)

@router.message((F.text.lower() == 'удалить преподавателя') | (F.text.lower() == 'remove teacher') | (F.text.lower() == 'usuń nauczyciela') | (F.text.lower() == 'видалити викладача'))
async def del_teacher(message: Message, state: FSMContext):
    menu = await dm.create_del_teacher_menu(db.get_lang(message.from_user.id))
    await message.answer("Выберите преподавателя", reply_markup=menu)

async def return_to_menu(message: Message):
    await message.answer(
            "Номер карточки некорректен. Пожалуйста, попробуйте снова.",
            reply_markup=mm.get_admin_account_menu(db.get_lang(message.from_user.id))
        )

@router.message(Form.admin_card)
async def check_card(message: Message, state: FSMContext):
    card_number_pattern = r'^\d{16}$'
    card_number = message.text.strip()

    await state.set_state()

    if re.match(card_number_pattern, card_number):
        db.add_admin_card(message.from_user.id, card_number)
        await message.answer("Номер карточки успешно добавлен!",
                                reply_markup=mm.get_admin_account_menu(db.get_lang(message.from_user.id))
                            )
    else:
        await return_to_menu(message)

@router.message(F.document, Form.teacher)
async def set_homework(message: Message, state: FSMContext):
    if message.document:
        data = await state.get_data()
        index = data.get('type')
        await message.answer(translate_text("Документ успешно отправлен.", db.get_lang(message.from_user.id)))
        ids = await dm.set_document_to_students(message.from_user.id, index)
        for id in ids:
            await bot.send_document(chat_id=id, document=message.document.file_id)
    else:
        await message.answer(translate_text("Пожалуйста, прикрепите документ.", db.get_lang(message.from_user.id)))

@router.message((F.text.lower() == 'отправить домашнее задание') | (F.text.lower() == 'submit homework') | (F.text.lower() == 'prześlij zadanie domowe') | (F.text.lower() == 'Надіслати домашнє завдання'), Form.student)
async def set_homework(message: Message, state: FSMContext):
    await message.answer(
        translate_text("Выберите группу для отправки", db.get_lang(message.from_user.id)),
        reply_markup=dm.create_groups_menu(message.from_user.id, 2, 2, db.get_lang(message.from_user.id))
    )

@router.message(F.text | F.document | F.photo, Form.student)
async def set_homework(message: Message, state: FSMContext):
    data = await state.get_data()
    index = data.get('type')

    if message.document:
        await message.reply(translate_text("Документ успешно отправлен.", db.get_lang(message.from_user.id)))
        id = await dm.set_document_to_teachers(index)
        await bot.send_document(chat_id=id, document=message.document.file_id)
    elif message.photo:
        await message.reply(translate_text("Фото успешно отправлено.", db.get_lang(message.from_user.id)))
        id = await dm.set_document_to_teachers(index)
        photo_id = message.photo[-1].file_id
        await bot.send_photo(chat_id=id, photo=photo_id)
    elif message.text:
        await message.reply(translate_text("Текст успешно отправлен.", db.get_lang(message.from_user.id)))
        id = await dm.set_document_to_teachers(index)
        await bot.send_message(chat_id=id, text=message.text)
    else:
        await message.reply(translate_text("Пожалуйста, прикрепите документ, фото или введите текст.", db.get_lang(message.from_user.id)))

@router.callback_query(F.data.startswith("teacher_del"))
async def teacher_del(callback: CallbackQuery, state: FSMContext):
    _, _, id = callback.data.split("_")
    if db.delete_teacher(id) == True:
        await callback.message.answer(translate_text("Преподаватель был удалён", db.get_lang(callback.from_user.id)))
    else:
        await callback.message.answer(translate_text("В группах этого преподавателя есть студенты", db.get_lang(callback.from_user.id)))

@router.callback_query(F.data.startswith("check_payload"))
async def payload_check_query(callback: CallbackQuery, state: FSMContext):
    _, _, choose, group_id = callback.data.split('_')

    if choose == 'yes':
        await callback.message.answer(
            translate_text("Какой вариант оплаты вас устраивает?", db.get_lang(callback.from_user.id)),
            reply_markup=mm.get_payload_menu(group_id, db.get_lang(callback.from_user.id))
        )
    elif choose == 'no':
        await callback.message.answer(
            translate_text("Хорошо", db.get_lang(callback.from_user.id)),
            reply_markup=mm.get_student_account_menu(db.get_lang(callback.from_user.id))
        )
    else:
        await callback.message.answer(
            translate_text("Неверный ответ. Попробуйте ещё раз.", db.get_lang(callback.from_user.id)),
            reply_markup=mm.get_student_account_menu(db.get_lang(callback.from_user.id))
        )

@router.callback_query(F.data.startswith('confirm'))
async def confirm_user(callback: CallbackQuery, state: FSMContext):
    _, id, choose, group_id = callback.data.split("_")
    db.add_pay_user(id, group_id, choose)

@router.callback_query(F.data.startswith("pay"))
async def check_payload(callback: CallbackQuery, state: FSMContext):
    _, choose, id, group_id = callback.data.split("_")

    confirm_button = []

    if choose == "one":
        message_text = f'{translate_text("Пользователь оплатил одно занятие, подтверждаете оплату?", db.get_lang(id))}\n{translate_text("Фамилия и имя пользователя: ", db.get_lang(id))} {db.get_user_name(callback.from_user.id)}\n{datetime.now()}'
    elif choose == "all":
        message_text = f'{translate_text("Пользователь оплатил восемь занятий, подтверждаете оплату?", db.get_lang(id))}\n{translate_text("Фамилия и имя пользователя: ", db.get_lang(id))} {db.get_user_name(callback.from_user.id)}\n{datetime.now()}'

    confirm_button.append({
        'text': 'Подтвердить',
        'callback_data': f'confirm_{id}_{choose}_{group_id}'
    })

    inline_keyboard = {
        'inline_keyboard': [confirm_button],
        'row_width': 1
    }

    await bot.send_message(chat_id=id, text=message_text, reply_markup=inline_keyboard)

@router.callback_query(F.data.startswith("choose_payload"))
async def pay_payload_query(callback: CallbackQuery, state: FSMContext):
    _, _, choose, group_id = callback.data.split("_")

    id, card_number, price = db.get_card_number()

    lang = db.get_lang(callback.from_user.id)
    text1 = translate_text("Цена одного занятия составляет", lang)
    text2 = translate_text("Для оплаты необходимо перевести деньги по данному номеру карты", lang)
    text3 = translate_text("Цена восьми занятий составляет", lang)

    if choose == "one":
        await callback.message.answer(
            f"{text1} {price}$\n{text2} {card_number}",
            reply_markup=mm.get_check_payload_menu("one", id, group_id, lang=db.get_lang(callback.from_user.id))
        )
    elif choose == "all":
        await callback.message.answer(
            f"{text1} {price * 8}$\n{text3} {card_number}",
            reply_markup=mm.get_check_payload_menu("all", id, group_id, lang=db.get_lang(callback.from_user.id))
        )

    callback.message.answer(
        "Okey",
        reply_markup=mm.get_student_account_menu(db.get_lang(callback.from_user.id))
    )