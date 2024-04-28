from aiogram import Bot, Dispatcher
from aiogram import Router

bot_token = '6705614973:AAG5j5irkaSSjbAw-jwxrf2HXaZvVGtt_qA'
bot = Bot(token=bot_token)
router = Router()
dp = Dispatcher()
dp.include_router(router)