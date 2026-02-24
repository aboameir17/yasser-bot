import asyncio, os, httpx, logging
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

# --- [ الإعدادات - مفاتيحك الملكية ] ---
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
OPENROUTER_KEY = "b33a34f2b0da469e854176cc78642ea5"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# --- [ محرك التلميح عبر OpenRouter ] ---
async def get_openrouter_hint(word):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://render.com", # ضروري لـ OpenRouter
    }
    
    # نستخدم الموديل المجاني الأقوى Gemini 2.0 Flash
    payload = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {
                "role": "user", 
                "content": f"أنت خبير ألغاز. أعطني لغزاً ذكياً وقصيراً عن كلمة ({word}) دون ذكرها. الرد سطر واحد فقط."
            }
        ]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload, timeout=25.0)
            res_data = response.json()
            
            if 'choices' in res_data:
                return res_data['choices'][0]['message']['content'].strip()
            else:
                logging.error(f"OpenRouter Error: {res_data}")
                return "⚠️ المحرك المجاني مشغول حالياً."
    except Exception as e:
        logging.error(f"Connection Error: {e}")
        return "⚠️ فشل الاتصال بالمحرك المنقذ."

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.answer("🚀 <b>مرحباً بك في جورب الذكاء!</b>\nالبوت يعمل الآن عبر محرك OpenRouter المجاني.")

@dp.message_handler()
async def handle_game(m: types.Message):
    word = m.text.strip()
    wait_msg = await m.answer(f"⏳ <b>المنقذ يفكر في:</b> ( {word} )...")
    
    hint = await get_openrouter_hint(word)
    
    res = (
        f"💎 <b>〔 تـلـمـيـح الـمـنـقـذ 〕</b>\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📜 <b>الوصف:</b>\n"
        f"« <i>{hint}</i> »\n\n"
        f"━━━━━━━━━━━━━━"
    )
    await wait_msg.delete()
    await m.answer(res)

# --- [ إعدادات الويب للبقاء حياً لـ Render ] ---
async def handle_ping(request): return web.Response(text="Bot is Active")

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    port = int(os.environ.get("PORT", 10000))
    loop.create_task(web.TCPSite(runner, '0.0.0.0', port).start())
    
    print("✅ البوت شغال بمفتاح المنقذ الجديد!")
    executor.start_polling(dp, skip_updates=True)
