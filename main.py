import telebot
import yt_dlp
import os
import time
from keep_alive import keep_alive

# --- ضع التوكن هنا ---
TOKEN = "8555506230:AAFn0u92SPovcETmaNeIn_MU0Ixscbr1cbA" 
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً! أرسل رابط الفيديو وسأحاول تنزيله لك (الجودة المتوسطة لضمان السرعة).")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    chat_id = message.chat.id
    msg = bot.reply_to(message, "⏳ جارٍ الاتصال بالسيرفر... لحظة.")

    # إعدادات خاصة للسيرفرات الضعيفة (Render Free)
    ydl_opts = {
        'format': 'best[ext=mp4]/best', # ابحث عن صيغة MP4 جاهزة ولا تدمج شيئاً
        'outtmpl': 'video.%(ext)s',     # اسم موحد للملف
        'quiet': True,
        'noplaylist': True,
        'geo_bypass': True,
    }

    try:
        # 1. التنزيل
        bot.edit_message_text("⬇️ جارٍ التحميل داخل السيرفر...", chat_id, msg.message_id)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # 2. الرفع لتليجرام
        bot.edit_message_text("⬆️ جارٍ الرفع لك...", chat_id, msg.message_id)
        
        # التأكد من اسم الملف (قد يكون mp4 أو mkv)
        file_name = 'video.mp4'
        if not os.path.exists(file_name):
             file_name = 'video.mkv' # احتياط
        
        if os.path.exists(file_name):
            with open(file_name, 'rb') as video:
                bot.send_video(chat_id, video, caption="تم التنزيل بواسطة بوتك الخاص ✅")
            
            # 3. التنظيف (مهم جداً)
            os.remove(file_name)
            bot.delete_message(chat_id, msg.message_id)
        else:
            bot.edit_message_text("❌ فشل العثور على الملف بعد التنزيل.", chat_id, msg.message_id)

    except Exception as e:
        error_text = str(e)
        # تصفية رسالة الخطأ لتكون مقروءة
        if "Too Many Requests" in error_text:
            bot.reply_to(message, "⚠️ السيرفر مشغول جداً، حاول بعد قليل.")
        else:
            bot.reply_to(message, f"❌ حدث خطأ: {error_text[:100]}") # نعرض أول 100 حرف فقط
    
    finally:
        # تنظيف إجباري في كل الحالات
        if os.path.exists('video.mp4'): os.remove('video.mp4')
        if os.path.exists('video.mkv'): os.remove('video.mkv')

# تشغيل السيرفر أولاً
keep_alive()
# تشغيل البوت
bot.infinity_polling(timeout=10, long_polling_timeout=5)
  
