import os
import tempfile
from pydub import AudioSegment
import gdown
import streamlit as st
import time
from generate_subtitles import compress_audio, transcribe_audio, translate_audio
import base64
from io import BytesIO


st.set_page_config(page_title='影片字幕生成', layout='centered')

st.title('影片字幕生成')
st.warning('⚠️ 注意：本應用僅供 AmazingTalker 員工使用。')




language_options = {
    '中文': 'zh',
    '英文': 'en',
    '日文': 'ja',
    '韓文': 'ko',
    '德語': 'de',
    '法語': 'fr',
    '阿非利堪斯語': 'af',
    '阿拉伯語': 'ar',
    '亞美尼亞語': 'hy',
    '亞塞拜然語': 'az',
    '白俄羅斯語': 'be',
    '波士尼亞語': 'bs',
    '保加利亞語': 'bg',
    '加泰隆尼亞語': 'ca',
    '克羅埃西亞語': 'hr',
    '捷克語': 'cs',
    '丹麥語': 'da',
    '荷蘭語': 'nl',
    '愛沙尼亞語': 'et',
    '芬蘭語': 'fi',
    '加利西亞語': 'gl',
    '希臘語': 'el',
    '希伯來語': 'he',
    '印地語': 'hi',
    '匈牙利語': 'hu',
    '冰島語': 'is',
    '印度尼西亞語': 'id',
    '義大利語': 'it',
    '卡納達語': 'kn',
    '哈薩克語': 'kk',
    '拉脫維亞語': 'lv',
    '立陶宛語': 'lt',
    '馬其頓語': 'mk',
    '馬來語': 'ms',
    '馬拉地語': 'mr',
    '毛利語': 'mi',
    '尼泊爾語': 'ne',
    '挪威語': 'no',
    '波斯語': 'fa',
    '波蘭語': 'pl',
    '葡萄牙語': 'pt',
    '羅馬尼亞語': 'ro',
    '俄語': 'ru',
    '塞爾維亞語': 'sr',
    '斯洛伐克語': 'sk',
    '斯洛維尼亞語': 'sl',
    '西班牙語': 'es',
    '斯瓦希里語': 'sw',
    '瑞典語': 'sv',
    '他加祿語': 'tl',
    '坦米爾語': 'ta',
    '泰語': 'th',
    '土耳其語': 'tr',
    '烏克蘭語': 'uk',
    '烏都語': 'ur',
    '越南語': 'vi',
    '威爾斯語': 'cy'
}

selected_language = st.selectbox('請選擇轉譯語言：', options=list(language_options.keys()))

translate_to_english = st.checkbox("翻譯成英文")

default_prompt = 'Eko去死...?我是Sandra和七分編!'

user_prompt = st.text_input(
    '請輸入 Prompt 以改進轉譯品質（如果轉譯語言不是中文，要刪去預設內容）：',
    default_prompt,
    help='提示可幫助改善轉譯。模型會匹配提示風格。sk-XoMbaSlipXt1g01SjTvjT3B-lbkFJd13PWYDy44b2OFXKSz91'
)

temperature = st.number_input('請輸入 Temperature：', value=0.6)

user_api_key = st.text_input('請輸入您的 Open AI API 金鑰：', type="password")

# 用於下載音頻的 YouTube 網址
youtube_url = st.text_input("輸入 YouTube 影片網址:")

# 用於下載音頻的 Google Drive 連結
gdrive_url = st.text_input("或輸入 Google Drive 連結:")

# 或者直接上傳音頻檔案
uploaded_file = st.file_uploader("或請上傳 MP3 或 MP4 檔案：", type=["mp3", "mp4"])


if youtube_url:
    output_file = "downloaded_audio.mp3"
    command = f'yt-dlp -x --audio-format mp3 -o "{output_file}" "{youtube_url}"'
    os.system(command)
    uploaded_file = BytesIO(open(output_file, "rb").read())

elif gdrive_url:
    output_file = "gdrive_file"
    gdown.download(gdrive_url, output_file, quiet=False, fuzzy=True)
    uploaded_file = BytesIO(open(output_file, "rb").read())


if uploaded_file is not None:
    total_start_time = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_name = temp_file.name

    with st.spinner("壓縮音訊中..."):
        start_time = time.time()
        compressed_file = compress_audio(temp_file_name)
        elapsed_time = time.time() - start_time
        st.write(f"壓縮音訊所需時間：{elapsed_time:.2f} 秒")
    
    if translate_to_english:
        with st.spinner("生成字幕並翻譯成英文中..."):
            start_time = time.time()
            srt_file = f"srt_{os.path.basename(temp_file_name)}_translated.srt"
            translate_audio(compressed_file, srt_file, user_prompt, user_api_key, temperature)
            elapsed_time = time.time() - start_time
            st.write(f"生成字幕並翻譯成英文所需時間：{elapsed_time:.2f} 秒")
    else:
        with st.spinner("生成字幕中..."):
            start_time = time.time()
            srt_file = f"srt_{os.path.basename(temp_file_name)}.srt"
            transcribe_audio(compressed_file, srt_file, language_options[selected_language], user_prompt, user_api_key, temperature)
            elapsed_time = time.time() - start_time
            st.write(f"生成字幕所需時間：{elapsed_time:.2f} 秒")
    
    total_elapsed_time = time.time() - total_start_time
    st.write(f"總共所需時間：{total_elapsed_time:.2f} 秒")

    st.success("字幕檔案已生成！")
        
    # Convert the SRT file into a downloadable format
    with open(srt_file, 'r', encoding='utf-8') as f:
        srt_data = f.read()
    srt_bytes = srt_data.encode('utf-8')
    b64 = base64.b64encode(srt_bytes).decode()
    
    href = f'<a href="data:file/srt;base64,{b64}" download="{srt_file}" target="_blank">點擊此處下載字幕檔案</a>'
    st.markdown(href, unsafe_allow_html=True)
    
    st.markdown("以下是一些實用連結：")
    st.markdown("- [合併兩個字幕](https://subtitletools.com/merge-subtitles-online)")
    st.markdown("- [把雙行字幕變成英文大小50、中文大小75](https://colab.research.google.com/drive/16I1BLSC_LR6EFZOWGXBSJwIjJ4LfTq9s?usp=sharing)")
    st.markdown("- [生成內容摘要SRT](https://colab.research.google.com/drive/1VgfPTfmbU2kjJ7nMXkmNMWcVbvOyqX0N?usp=sharing)")
