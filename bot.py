import os
import json
import youtube_dl
import telepotpro
from random import randint
from multiprocessing import Process
from youtubesearchpython import SearchVideos
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

TOKEN = os.environ.get("TOKEN")
bot = telepotpro.Bot(TOKEN)

class Music:
    def __init__(self, user_input, msg):
        self.chat = Chat
        self.user_input = user_input[6:]

    def search_music(self, user_input):
        search = SearchVideos(user_input, offset = 1, mode = "json", max_results = 1)
        
        return json.loads(search.result())

        pass

    def get_link(self, result):
        return result['search_result'][0]['link']

        pass

    def get_title(self, result):
        return result['search_result'][0]['title']

        pass

    def get_duration(self, result):
        result = result['search_result'][0]['duration'].split(':')
        min_duration = int(result[0])
        split_count = len(result)
        
        return min_duration, split_count

        pass

    def download_music(self, file_name, link):
        ydl_opts = {
            'outtmpl': './'+file_name,
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '256',
            }],
            'prefer_ffmpeg': True
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=True)

        pass

class Chat:
    def __init__(self, msg):
        self.chat_id = msg['chat']['id']
        self.user_input = msg['text']
        self.user_input = self.user_input.replace('@EmiliaMusicDownloader_Bot', '')
        self.user_name = msg['from']['first_name']
        self.message_id = msg['message_id']

        self.messages = {
            'start':'✨ Hi👋 '+ self.user_name +'!\n\n'
                    '📩 Kirimkan ke saya perintah:\n\n'
                    '"*/music* _judul lagu_"  or\n'
                    '"*/music* _nama artis - judul lagu_"\n\n'
                    'untuk mengunduh musik. 🎶',
            
            'spotify_input_error':"‼️ *upps! Maaf bot ini tidak mendukung link spotify, namun bisa mendukung perjuanganmu😁!*\n"
                    'Try: "*/music* _judul lagu_"\n'
                    'or: "*/music* _nama artis - judul lagu_"',

            'invalid_command':'‼️ *upps! Perintah tidak ditemukan, karena menemukannya tak semudah seperti kau menyakiti hati nya😌!*\n'
                    'Try: "*/music* _judul lagu_"\n'
                    'or: "*/music* _nama artis - judul lagu_"',

            'too_long':'‼️ *upps! Video terlalu panjang untuk dikonversi!*\n'
                    'Unduh video dengan durasi 30 menit atau kurang.'


        }

        self.check_input(self.user_input, msg)

        pass

    def send_message(self, content):
        return bot.sendMessage(self.chat_id, content, reply_to_message_id=self.message_id, parse_mode='Markdown')

        pass

    def delete_message(self, message):
        chat_id = message['chat']['id']
        message_id = message['message_id']
        bot.deleteMessage((chat_id, message_id))

        pass

    def send_audio(self, file_name):
        bot.sendAudio(self.chat_id,audio=open(file_name,'rb'), reply_to_message_id=self.message_id)

        pass

    def process_request(self, user_input):
        result = Music.search_music(self, user_input[6:])
        min_duration, split_count = Music.get_duration(self, result)

        if int(min_duration) < 30 and split_count < 3:
            file_name = Music.get_title(self, result) +' - @EmiliaMusicDownloader_Bot '+str(randint(0,999999))+'.mp3'
            file_name = file_name.replace('"', '')

            self.send_message(['🎵 '+ Music.get_title(self, result) +'\n'+'🔗 '+Music.get_link(self, result)])
            downloading_message = self.send_message('⬇️ Mengunduh😴... \n_(mungkin ini membutuhkan beberapa waktu, seperti menunggu jodoh🙂.)_')

            Music.download_music(self, file_name, Music.get_link(self, result))

            try:
                self.send_audio(file_name)
                self.delete_message(downloading_message)
                self.send_message('✅ Berhasil mendapatkannya😉!')
                print ("\nSuccess!\n")
            except:
                print("\nError")

            os.remove(file_name)
        pass

    def check_input(self, user_input, msg):
        if user_input.startswith('/start'):
            self.send_message(self.messages['start'])

        elif user_input.startswith('/music') and user_input[6:]!='':
            if 'open.spotify.com' in user_input[6:]:
            	self.send_message(self.messages['spotify_input_error'])

            else:
                self.process_request(user_input)

        else:
            #Invalid command
            self.send_message(self.messages['invalid_command'])

        pass 

def start_new_chat(msg):
    Process(target=Chat, args=(msg,)).start()
    

bot.message_loop(start_new_chat, run_forever=True)
