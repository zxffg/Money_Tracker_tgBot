from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery, ErrorEvent

import logging

from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from database import insert_in_db, delete_from_db, money_on_account, insert_in_transactions, get_category_id
from app.keybords import main_keyboard, delete_keyboard, popular_categories, type_operation_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Это Бот для учета доходов/расходов!', reply_markup=main_keyboard)

#! Проверка баланса
@router.message(F.text == 'Баланс счета')
async def check_money(message: Message):
    await message.reply(f"Сейчас на вашем счете: {money_on_account()} руб." )

#! Добавление записи
class AddTransaction(StatesGroup):
    # Для варианта А (выбор существующей)
    wait_category_id = State()
    wait_amount_old_cat = State() # состояние суммы для варианта А

    # Для варианта Б (создание новой)
    wait_category_name = State()
    wait_type = State()
    wait_amount_new_cat = State()

@router.message(F.text == 'Добавить запись')
async def insert_name(message: Message, state: FSMContext):
    input_kb = await popular_categories()
    await message.answer(text="Выберите уже существующую категорию, или добавьте новую", reply_markup=input_kb)
    await state.set_state(AddTransaction.wait_category_id)

#TODO: хендлеры на добавление записи
@router.callback_query(F.data.startswith("cat:"))
async def get_new_entry(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split(":")[1])
    await state.update_data(chosen_category_id=category_id)
    await state.set_state(AddTransaction.wait_amount_old_cat)
    await callback.answer()
    await callback.message.edit_text(text="Отлично! Укажите сумму в формате xxx.xx")

@router.message(AddTransaction.wait_amount_old_cat)
async def insert_entry_in_table(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(text="Укажите стоимость в цифрах")
        return
    clean_text = message.text.replace(',', '.')
    try:
        amount = float(clean_text)
        if amount <= 0:
            await message.answer(text="Сумма должна быть больше нуля (например 500 или 159.99).\nЕсли выбрана категория <Расход>, стоит указывать числа без '-'")
            return
    except ValueError:
        await message.answer(text="Указано недопустимое значение!")
        return
    await state.update_data(chosen_amount=amount)
    user_data = await state.get_data()
    category_id = user_data['chosen_category_id']
    amount = user_data['chosen_amount']

    insert_in_transactions(category_id, amount)

    await message.answer(text="Операция успешно добавлена!")
    await state.clear()


#TODO: хендлеры на добавление категории и записи
@router.callback_query(F.data.startswith("new:"))
async def insert_new_categoryANDentry(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Отлично! Ниже укажите название новой категории:")
    await state.set_state(AddTransaction.wait_category_name)
    await callback.answer()

@router.message(AddTransaction.wait_category_name)
async def get_name_category(message: Message, state: FSMContext):
    if not message.text:
        await message.answer("Указано недопустимое значение!")
        return
    category = message.text.strip()
    if len(category) > 50:
        await message.answer(text="Не более 50 символов!")
        return
    category.capitalize()
    await state.update_data(name_category=category)
    await state.set_state(AddTransaction.wait_type)
    await message.answer(text="Запомнил! Теперь выбери тип операции:", reply_markup=type_operation_keyboard)

@router.callback_query(F.data.startswith("too:"))
async def get_type_category(callback: CallbackQuery, state: FSMContext):
    type = str(callback.data.split(":")[1])
    await state.update_data(type_operation=type)
    await state.set_state(AddTransaction.wait_amount_new_cat)
    await callback.answer()
    await callback.message.edit_text(text="Записал! Теперь укажи сумму операции в формате xxx.xx")

@router.message(AddTransaction.wait_amount_new_cat)
async def get_amount(message: Message, state: FSMContext):
    if not message.text:
        await message.answer(text="Укажите стоимость в цифрах")
        return
    clean_text = message.text.replace(',', '.')
    try:
        amount = float(clean_text)
        if amount <= 0:
            await message.answer(text="Сумма должна быть больше нуля (например 500 или 159.99).\nЕсли выбрана категория <Расход>, стоит указывать числа без '-'")
            return
    except ValueError:
        await message.answer(text="Указано недопустимое значение!")
        return
    
    await state.update_data(new_amount=amount)
    user_data = await state.get_data()
    name_category = user_data["name_category"]
    type_operation = user_data["type_operation"]
    amount = user_data["new_amount"]

    insert_in_db(name_category, type_operation)
    insert_in_transactions(int(get_category_id(name_category, type_operation)), amount)

    await message.answer("Ваша запись успешно добавлена!")
    await state.clear()

#! Удаление записи через inline клавиатуру
@router.message(F.text == "Удалить запись")
async def show_delete_menu(message: Message):
    inline_kb = await delete_keyboard()
    await message.answer(text='Выберите одну из пяти последних записей, которую хотите удалить:', reply_markup=inline_kb)

@router.callback_query(F.data.startswith("del:"))
async def delete_entry(callback: CallbackQuery):
    entry_id = callback.data.split(":")[1]
    delete_from_db(entry_id)
    await callback.message.edit_text(text="Успешно", reply_markup=None)
    await callback.answer()


# ~ Глобальная обработка ошибок
@router.errors()
async def global_error_handler(event: ErrorEvent):
    logging.error("Critical error caused by %s", event.exception, exc_info=True)
    try:
        if event.update.message():
            await event.update.message.answer(text="Что-то пошло не так...\nПовторите попытку позже.")
        elif event.update.callback_query:
            await event.update.callback_query.answer()
            await event.update.callback_query.message.answer(text="Произошла непредвиденная ошибка...\nПовторите попытку позже.")
    except Exception as error:
        logging.critical(f"Не удалось отправить сообщение пользователю: {error}")