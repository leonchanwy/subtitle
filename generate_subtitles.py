import re
import requests
import os
import shutil
from pydub import AudioSegment
import requests
import gdown



def download_video_from_google_drive(google_drive_video_link, output_file_name):
        gdown.download(google_drive_video_link, output_file_name, quiet=False)
        print(f"影片已成功下載並儲存為：{output_file_name}")


def compress_audio(input_file, target_size=21):
    target_size_bytes = target_size * 1000 * 1000
    audio = AudioSegment.from_file(input_file)

    output_file = f"compressed_{os.path.basename(input_file)}.mp3"
    
    # 計算目標比特率
    duration_seconds = len(audio) / 1000
    target_bitrate = int((target_size_bytes * 8) / duration_seconds)

    # 壓縮音訊並將其匯出為MP3
    audio.export(output_file, format="mp3", bitrate=f"{target_bitrate/1000}k")

    print(f"目標檔案大小：{target_size} MB")
    print(f"目標比特率：{target_bitrate/1000} kbps")
    print(f"壓縮後的檔案已儲存為：{output_file}")

    return output_file

def transcribe_audio(compressed_file, srt_file, language, prompt, api_key):
    
    with open(compressed_file, 'rb') as f:
        response = requests.post(
            'https://api.openai.com/v1/audio/transcriptions',
            headers={
                'Authorization': f'Bearer {api_key}'},
            data={
                'model': 'whisper-1',
                'language': language, #這裏可以改你想轉譯的文字'zh'是中文'ja'是日文、'en'是英文
                'prompt': prompt,
                'response_format': 'srt',
            },
            files={'file': (compressed_file, f, 'audio/mpeg')}
        )
        
    if response.status_code == 200:
        with open(srt_file, 'w', encoding='utf-8') as f:
            f.write(response.text)
    else:
        print(f"Error transcribing audio: {response.text}")
        raise Exception(f"Error transcribing audio: {response.text}")

        
if __name__ == "__main__":
    google_drive_video_link = "https://drive.google.com/file/d/1pkm5_UE4HhO6UUZHdCEkZnlNtzSNLAAU/view?usp=sharing"
    output_file_name = "video.mp4"
    srt_file = f"srt_{os.path.basename(output_file_name)}.srt"
    compressed_file = compress_audio(output_file_name)
    transcribe_audio(compressed_file, srt_file)
    print("字幕檔案已儲存為：", srt_file)

