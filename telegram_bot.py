import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from dotenv import load_dotenv

from logic import RedisClient


load_dotenv()

URL = 'https://cbr.ru/scripts/XML_daily.asp'

bot_token = os.getenv('BOT_API')
bot = Bot(bot_token)
dp = Dispatcher()


@dp.message(Command('exchange'))
async def exchange(message: Message, command: CommandObject):
    if not command.args or len(command.args.split()) != 3:
        text = (
            'Вы ввели значения после /exchange неправильно.' +
            'Пример правильного ввода данных:\n"/exchange USD RUB 10".'
        )
        await message.answer(text)
        return
    currency_from, currency_to, amount = command.args.split()
    try:
        amount = float(amount)
        if amount <= 0:
            await message.answer(
                'Количество должно быть положительным числом.'
            )
            return
    except ValueError:
        await message.answer('Количество должно быть числом.')
        return
    if not await client.is_not_empty():
        await client.insert_currencies(URL)
    if currency_from == 'RUB':
        rate = await client.get_currency(currency_to)
        currency = currency_to
        function = client.buy_foreign_currency
    elif currency_to == 'RUB':
        rate = await client.get_currency(currency_from)
        currency = currency_from
        function = client.sell_foreign_currency
    else:
        await message.answer('Хотя бы одна валюта должна быть рублём.')
        return
    if not rate:
        await message.answer(f'{currency} такой валюты не существует.')
        return
    result = function(rate, float(amount))
    text = (
        f'За продажу {amount} {currency_from} ' +
        f'вы получите {result} {currency_to}'
    )
    await message.answer(text)


@dp.message(Command('rate'))
async def rate(message: Message):
    if not await client.is_not_empty():
        await client.insert_currencies(URL)
    text = await client.gather_all_info()
    await message.answer(text)


@dp.message()
async def unknown_command(message: Message):
    await message.answer(
        'Неизвестная команда, используйте "/rate" или "/exchange".'
    )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    client = RedisClient()
    asyncio.run(main())
