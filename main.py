import telebot
import subprocess
import os

API_TOKEN = '8893223250:AAGTbssA6NQ1OlWbEADF__SZswA0zQ36xPU'

bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    pesan = (
        "👋 **Selamat datang di Bot AutoKlip Anda!**\n\n"
        "Kirim pesan dengan format berikut untuk memotong video:\n"
        "`LINK_YOUTUBE | START_DETIK | END_DETIK | TEKS_HOOK`\n\n"
        "📌 **Contoh Penggunaan:**\n"
        "`https://youtu.be/abc1234 | 10 | 40 | BANYAK ORANG ENGGAK TAHU HAL INI!`"
    )
    bot.reply_to(message, pesan, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def process_video(message):
    try:
        data = message.text.split('|')
        if len(data) < 3:
            bot.reply_to(message, "⚠️ Format salah!\nGunakan format: `LINK | START_DETIK | END_DETIK | TEKS_HOOK`", parse_mode='Markdown')
            return

        url = data[0].strip()
        start = data[1].strip()
        end = data[2].strip()
        hook_text = data[3].strip() if len(data) > 3 else ""

        bot.reply_to(message, "⏳ **Sedang memproses video...**\nMohon tunggu, video sedang dipotong, di-crop 9:16, dan ditempeli hook.", parse_mode='Markdown')

        cmd_url = f'yt-dlp -g -f "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best" "{url}"'
        stream_url = subprocess.check_output(cmd_url, shell=True).decode('utf-8').strip().split('\n')[0]

        output_file = "klip_hasil.mp4"

        if hook_text:
            vf_filter = f"crop=ih*(9/16):ih,drawtext=text='{hook_text}':enable='between(t,0,3)':fontcolor=yellow:fontsize=36:x=(w-text_w)/2:y=(h-text_h)/4:box=1:boxcolor=black@0.8"
        else:
            vf_filter = "crop=ih*(9/16):ih"

        cmd_ffmpeg = f'ffmpeg -y -ss {start} -to {end} -i "{stream_url}" -vf "{vf_filter}" -c:v libx264 -preset ultrafast -c:a aac {output_file}'
        subprocess.run(cmd_ffmpeg, shell=True, check=True)

        with open(output_file, 'rb') as video:
            bot.send_video(message.chat.id, video, caption="✅ **Klip Anda sudah siap!**")

        if os.path.exists(output_file):
            os.remove(output_file)

    except Exception as e:
        bot.reply_to(message, f"❌ Gagal memproses video.\nError: {str(e)}")

bot.polling()
