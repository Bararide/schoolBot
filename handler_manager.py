import asyncio

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

import database_manager as db

from translations import translate_text

async def set_document_to_students(id: int, group_id: int) -> int:
    student_id = db.get_group_document_from_teacher(group_id)[0]
    return student_id

async def set_document_to_teachers(group_id: int) -> int:
    teacher_id = db.get_group_document_from_student(group_id)[0]
    return teacher_id

async def create_lesson_view_menu(lang) -> []: # type: ignore
    levels = db.get_views()

    group_conversion = {
        3: "Групповое",
        2: "Парное",
        1: "Индивидуальное"
    }

    with db.conn:
        keyboard_buttons = []
        for i, level in enumerate(levels):
            group = group_conversion[level]
            if level == 3:
                keyboard_buttons.append([InlineKeyboardButton(text=translate_text(group, lang), callback_data=f"group_{i}")])
            elif level == 2:
                keyboard_buttons.append([InlineKeyboardButton(text=translate_text(group, lang), callback_data=f"pair_{i}")])
            elif level == 1:
                keyboard_buttons.append([InlineKeyboardButton(text=translate_text(group, lang), callback_data=f"individual_{i}")])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons, row_width=1)

async def create_del_teacher_menu(lang=2) -> InlineKeyboardMarkup:
    teachers = db.get_all_teachers()

    with db.conn:
        keyboard_buttons = []
        for teacher in teachers:
            keyboard_buttons.append([InlineKeyboardButton(text=teacher[0], callback_data=f"teacher_del_{teacher[1]}")])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons, row_width=1)

async def create_language_level_menu(group_level: int, lang) -> InlineKeyboardMarkup:
    groups = db.get_views_by_level(group_level)
    print(groups)

    level_conversion = {
        6: "C1",
        5: "C2",
        4: "B1",
        3: "B2",
        2: "A1",
        1: "A2",
        0: "Новичок"
    }

    with db.conn:
        keyboard_buttons = []
        for row in groups:
            views = row[1].split(', ')
            for view in views:
                level = level_conversion[int(view)]
                if int(view) == 1:
                    callback_data = "level_a2"
                elif int(view) == 2:
                    callback_data = "level_a1"
                elif int(view) == 3:
                    callback_data = "level_b2"
                elif int(view) == 4:
                    callback_data = "level_b1"
                elif int(view) == 5:
                    callback_data = "level_c2"
                elif int(view) == 6:
                    callback_data = "level_c1"
                else:
                    callback_data = "level_a0"

                keyboard_buttons.append([InlineKeyboardButton(text=translate_text(level, lang), callback_data=callback_data)])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons, row_width=2)
    

def create_groups_menu(id: int, index: int, type: int, lang) -> InlineKeyboardMarkup:
    if type == 1:
        groups = db.get_teacher_groups(id)
    else:
        groups = db.get_student_groups(id)

    group_conversion = {
        3: "Групповое",
        2: "Парное",
        1: "Индивидуальное"
    }

    level_conversion = {
        6: "C1",
        5: "C2",
        4: "B1",
        3: "B2",
        2: "A1",
        1: "A2",
        0: "Новичок"
    }

    with db.conn:
        keyboard_buttons = []
        for row in groups:
            if row[1] != None:
                group = group_conversion[row[1]]
                levels = ""

                views = row[2].split(", ")
                for i, view in enumerate(views):
                    digits = view.split(",")
                    for digit in digits:
                        digit_int = int(digit.strip())
                        levels += str(level_conversion[digit_int]) + " "

                    if index == 1:
                        keyboard_buttons.append([InlineKeyboardButton(text=translate_text(f"Занятие: {translate_text(group, lang)}, уровни: {translate_text(levels, lang)}", lang), callback_data=f"del_group_{row[-1]}")])
                    else:
                        keyboard_buttons.append([InlineKeyboardButton(text=translate_text(f"Занятие: {translate_text(group, lang)}, уровни: {translate_text(levels, lang)}", lang), callback_data=f"choose_group_{row[-1]}")])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons, row_width=1)
    
def create_group_id_menu(id: int, lang) -> InlineKeyboardMarkup:
    groups = db.get_groups_id(id)
    with db.conn:
        keyboard_buttons = []
        for row in groups:
            print(row[0])
            keyboard_buttons.append([InlineKeyboardButton(text=str(row[0]), callback_data=f"gr_id_{row[0]}")])

        return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons, row_width=1)