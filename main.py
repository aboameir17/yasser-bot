import asyncio
import httpx
import os
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

# --- [ الإعدادات المباشرة ] ---
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
GROQ_API_KEY = "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"

bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# --- [ محرك التلميح الذكي - المطور ضد التصفير ] ---
async def generate_smart_hint(word):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": "أنت خبير ألغاز. مهمتك إعطاء وصف ذكي وغامض للكلمة دون ذكرها. رد باللغة العربية فقط وبشكل مختصر."},
            {"role": "user", "content": f"أعطني لغزاً عن: {word}"}
        ],
        "temperature": 0.7,
        "max_tokens": 100
    }

    try:
        async with httpx.AsyncClient() as client:
            # زدنا الوقت لـ 20 ثانية عشان يلحق يجاوب وما يصفر
            response = await client.post(url, headers=headers, json=payload, timeout=20.0)
            
            if response.status_code == 200:
                result = response.json()
                hint_text = result['choices'][0]['message']['content'].strip()
                if hint_text:
                    return hint_text
                else:
                    return "لم أستطع إيجاد وصف، حاول مرة أخرى!"
            else:
                return f"خطأ في السيرفر: {response.status_code}"
    except Exception as e:
        return f"عذراً، حدث خطأ في الاتصال: {str(e)}"

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.answer("🚀 <b>جورب الذكاء متصل الآن!</b>\nأرسل أي كلمة (مثلاً: سيارة) وسأعطيك تلميحاً مليان.")

@dp.message_handler()
async def hint_handler(m: types.Message):
    word = m.text.strip()
    # رسالة الانتظار
    msg = await m.answer(f"⏳ <b>ذكاء Groq يحلل كلمة:</b> ( {word} )...")
    
    hint = await generate_smart_hint(word)
    
    # القالب الملكي المزخرف
    res = (
        f"💎 <b>〔 تـلـمـيـح ذكـي نـادر 〕</b>\n"
        f"━━━━━━━━━━━━━━\n\n"
        f"📜 <b>الوصف:</b>\n"
        f"« <i>{hint}</i> »\n\n"
        f"━━━━━━━━━━━━━━\n"
        f"<b>💡 هل عرفت الإجابة؟</b>"
    )
    
    await msg.delete()
    await m.answer(res)

# --- [ نظام البقاء حياً لـ Render ] ---
async def web_peer(request): return web.Response(text="Bot Active")

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/', web_peer)
    runner = web.AppRunner(app)
    loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    port = int(os.environ.get("PORT", 10000))
    loop.create_task(web.TCPSite(runner, '0.0.0.0', port).start())
    
    print("✅ البوت انطلق والتلميح لن يصفر!")
    executor.start_polling(dp, skip_updates=True)
