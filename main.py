import requests

def get_direct_hint(word):
    print(f"⏳ جاري طلب لغز عن ({word}) من المحرك المباشر...")
    
    # الرابط المستخرج من ملفك ChatGPT-3.5.py
    url = f"https://www.pyhanzo.com/ChatGPT3.5?prompt=أعطني لغز ذكي وقصير جداً عن {word} بدون ذكر الاسم"
    
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            return response.text.strip()
        else:
            return f"❌ خطأ في السيرفر: {response.status_code}"
    except Exception as e:
        return f"❌ فشل الاتصال: {e}"

# تجربة فورية
if __name__ == "__main__":
    كلمة_التجربة = "الكتاب" # غير الكلمة هنا للتجربة
    result = get_direct_hint(كلمة_التجربة)
    print("\n📝 اللغز الناتح:")
    print(f"« {result} »")
