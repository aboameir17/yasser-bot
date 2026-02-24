import asyncio, os, httpx, logging
import google.generativeai as genai
from aiogram import Bot, Dispatcher, types, executor
from aiohttp import web

# --- [ الإعدادات - مفاتيحك ] ---
API_TOKEN = "8587471594:AAEDUgePR4dToTkxeJkrhFL3sWo0nFUY1yU"
GROQ_API_KEY = "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"
GEMINI_API_KEY = "AIzaSyBB6hSieJutCAx1jdZSi_h6kUfERIVV1C4"

# إعداد Gemini مع تعطيل الفلاتر تماماً
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    safety_settings=[
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]
)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

# --- [ محرك جورب (Groq) ] ---
async def get_groq_hint(word):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [{"role": "user", "content": f"أعطني لغزاً ذكياً جداً عن كلمة ({word}) بدون ذكر اسمها."}],
        "temperature": 0.6
    }
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(url, json=payload, headers=headers, timeout=10.0)
            text = res.json()['choices'][0]['message']['content'].strip()
            return f"🐺 <b>〔 تـلـمـيـح جـورب - Groq 〕</b>\n━━━━━━━━━━━━━━\n📜 <i>{text}</i>"
    except: return "⚠️ محرك جورب (Groq) متوقف حالياً."

# --- [ محرك الاختبار (Gemini) - النسخة الموثوقة ] ---
async def get_gemini_hint(word):
    try:
        # استخدام asyncio.to_thread لمنع تعليق البوت
        response = await asyncio.to_thread(
            gemini_model.generate_content, 
            f"أعطني لغزاً غامضاً وذكياً جداً عن الكلمة التالية بدون ذكرها: {word}"
        )
        
        # التحقق من وجود رد صالح
        if response and response.candidates:
            text = response.text.strip()
            return f"💎 <b>〔 تـلـمـيـح اخـتـبـار - Gemini 〕</b>\n━━━━━━━━━━━━━━\n📜 <i>{text}</i>"
        else:
            return "⚠️ Gemini رفض توليد اللغز (قيود المحتوى)."
    except Exception as e:
        logging.error(f"Gemini Error: {e}")
        return "⚠️ محرك Gemini واجه خطأ في الاتصال."

# --- [ معالجة الرسائل ] ---

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    await m.answer("🚀 <b>نظام السباق المزدوج مفعل!</b>\nأرسل أي كلمة الآن وشاهد قوة الذكاء الاصطناعي.")

@dp.message_handler()
async def duel_mode(m: types.Message):
    word = m.text.strip()
    wait_msg = await m.answer(f"⏳ جاري تشغيل المحركات لـ (<b>{word}</b>)...")

    # تشغيل المحركين بالتوازي لضمان السرعة
    gemini_res, groq_res = await asyncio.gather(
        get_gemini_hint(word),
        get_groq_hint(word)
    )

    await wait_msg.delete()
    await m.answer(gemini_res)
    await m.answer(groq_res)

# --- [ إعدادات Render للبقاء حياً ] ---
async def handle_ping(request): return web.Response(text="Active")

if __name__ == '__main__':
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app); loop = asyncio.get_event_loop()
    loop.run_until_complete(runner.setup())
    port = int(os.environ.get("PORT", 10000))
    loop.create_task(web.TCPSite(runner, '0.0.0.0', port).start())
    executor.start_polling(dp, skip_updates=True)
