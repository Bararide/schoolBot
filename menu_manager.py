from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import database_manager as db

from translations import translate_text

STUDENT    = "student"
TEACHER    = "teacher"
GROUP      = "group"
INDIVIDUAL = "individual"
PAIR       = "pair"
YES        = "yes"
NO         = "no"
LEVEL      = "level"
LEVEL_C1   = "level_c1"
LEVEL_C2   = "level_c2"
LEVEL_B1   = "level_b1"
LEVEL_B2   = "level_b2"
LEVEL_A1   = "level_a1"
LEVEL_A2   = "level_a2"
LEVEL_A0   = "level_a0"

local_language_menu = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text="Russian"  , callback_data='lang_ru'),
    InlineKeyboardButton(text="English"  , callback_data='lang_en'),
    InlineKeyboardButton(text="Polish"   , callback_data='lang_pl'),
    InlineKeyboardButton(text="Ukrainian", callback_data='lang_uk')
]])

def get_choose_of_payload_menu(id, lang=2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=translate_text("Да", lang), callback_data=f"check_payload_yes_{id}"),
            InlineKeyboardButton(text=translate_text("Нет", lang), callback_data=f"check_payload_no_{id}")
        ]
    ])

def get_payload_menu(group_id, lang=2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=translate_text("Оплатить одно занятие"  , lang), callback_data=f"choose_payload_one_{group_id}"),
            InlineKeyboardButton(text=translate_text("Оплатить восемь занятий", lang), callback_data=f"choose_payload_all_{group_id}")
        ]
    ])

def get_type_menu(lang=2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=translate_text("Есть аккаунт", lang), callback_data=YES),
        InlineKeyboardButton(text=translate_text("Нет аккаунта", lang), callback_data=NO)
    ]])

def get_registration_menu(lang=2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=translate_text("Студент", lang)      , callback_data=STUDENT),
        InlineKeyboardButton(text=translate_text("Преподаватель", lang), callback_data=TEACHER)
    ]])

def get_lesson_view_menu(lang=2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=translate_text("Групповое", lang)     , callback_data=GROUP),
        ],
        [
        InlineKeyboardButton(text=translate_text("Парное", lang)        , callback_data=PAIR),
        ],
        [
        InlineKeyboardButton(text=translate_text("Индивидуальное", lang), callback_data=INDIVIDUAL),
        ]
    ])

def get_language_level_menu(lang=2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="С1", callback_data=LEVEL_C1),
            InlineKeyboardButton(text="С2", callback_data=LEVEL_C2)
        ],
        [
            InlineKeyboardButton(text="B1", callback_data=LEVEL_B1),
            InlineKeyboardButton(text="B2", callback_data=LEVEL_B2)
        ],
        [
            InlineKeyboardButton(text="A1", callback_data=LEVEL_A1),
            InlineKeyboardButton(text="A2", callback_data=LEVEL_A2)
        ],
        [
            InlineKeyboardButton(text=translate_text("Новичок", lang), callback_data=LEVEL_A0),
        ],
    ])

def get_check_payload_menu(choose: str, id: int, group_id: int, lang=2) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=translate_text("Оплатил(а)", lang), callback_data=f"pay_{choose}_{id}_{group_id}")
        ]
    ])

def get_student_account_menu(lang=2) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=translate_text("Мой аккаунт", lang))],
        [KeyboardButton(text=translate_text("Отправить домашнее задание", lang))],
        [KeyboardButton(text=translate_text("Удалить аккаунт", lang))]
    ])

def get_teacher_account_menu(lang=2) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=translate_text("Мой аккаунт", lang))],
        [KeyboardButton(text=translate_text("Отправить домашнее задание", lang))],
        [KeyboardButton(text=translate_text("Добавить группу", lang))],
        [KeyboardButton(text=translate_text("Удалить группу", lang))]
    ])

def get_admin_account_menu(lang=2) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(keyboard=[
        [KeyboardButton(text=translate_text("Мой аккаунт", lang))],
        [KeyboardButton(text=translate_text("Добавить карту", lang))],
        [KeyboardButton(text=translate_text("Установить цену на занятие", lang))],
        [KeyboardButton(text=translate_text("Удалить преподавателя", lang))]
    ])