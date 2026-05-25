from aiogram.types import (CallbackQuery, ReplyKeyboardMarkup, 
                           KeyboardButton, InlineKeyboardMarkup, 
                           InlineKeyboardButton)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import last_five_entrys, ten_popular_categories

#! Реализация реплай кнопок и приветсвие при /start
main_keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Баланс счета'), KeyboardButton(text="Статистика расходов")],
    [KeyboardButton(text='Добавить запись'), KeyboardButton(text='Удалить запись')],
    [KeyboardButton(text='/start')]], resize_keyboard=True, input_field_placeholder="Выберите кнопку в меню.")

#! Inline для выбора type пр добавлении записи
async def popular_categories():
    keyboard = InlineKeyboardBuilder()
    data = ten_popular_categories()
    for row in data:
        button_text = f"{row[1]}, {row[2]} количество записей: {row[3]}"
        callback_value = f"cat:{row[0]}"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=callback_value))
    keyboard.add(InlineKeyboardButton(text="Добавить новую категорию", callback_data="new:cat"))
    keyboard.adjust(1)
    return keyboard.as_markup()

#! Inline для удаления
async def delete_keyboard():
    keyboard = InlineKeyboardBuilder()
    data = last_five_entrys()
    for row in data:
        button_text = f"{row[2]}, {row[4]} {row[3]}руб. время {row[5]}"
        callback_value = f"del:{row[0]}"
        keyboard.add(InlineKeyboardButton(text=button_text, callback_data=callback_value))
    keyboard.adjust(1)
    return keyboard.as_markup()

#! Inline клавиатура для выбора типа операции "too:"
type_operation_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Доход", callback_data="too:Доход")], [InlineKeyboardButton(text="Расход", callback_data="too:Расход")]])

#! Inline клавиатура для выбора типа статистики
choice_statistic_keyboard = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="Сегодня", callback_data="stt:today")], [InlineKeyboardButton(text="Последние 7 дней", callback_data="stt:last7days")], [InlineKeyboardButton(text="Последние 30 дней", callback_data="stt:last30days")]])