import os
import tempfile
import pydub
import streamlit as st
import time
from generate_subtitles import compress_audio, transcribe_audio
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

default_prompt = 'Eko去死...?我是Sandra和七分編!'

user_prompt = st.text_input(
    '請輸入 Prompt 以改進轉譯品質（使用預設值，直接點擊 Enter）：',
    default_prompt,
    help='提示可幫助改善轉譯。模型會匹配提示風格。'
)

default_api_key = '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'
user_api_key = st.text_input('請輸入您的 API 金鑰（使用預設值，直接點擊 Enter）：', default_api_key, type="password")

uploaded_file = st.file_uploader("請上傳 MP3 或 MP4 檔案：", type=["mp3", "mp4"])

if uploaded_file is not None:
    total_start_time = time.time()
    
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(uploaded_file.getvalue())
        temp_file_name = temp_file.name

    if os.path.splitext(temp_file_name)[1] == ".mp4":
        with st.spinner("壓縮音訊中..."):
            start_time = time.time()
            compressed_file = compress_audio(temp_file_name)
            elapsed_time = time.time() - start_time
            st.write(f"壓縮音訊所需時間：{elapsed_time:.2f} 秒")
    else:
        with st.spinner("壓縮音訊中..."):
            start_time = time.time()
            compressed_file = compress_audio(temp_file_name)
            elapsed_time = time.time() - start_time
            st.write(f"壓縮音訊所需時間：{elapsed_time:.2f} 秒")
    
    with st.spinner("生成字幕中..."):
        start_time = time.time()
        srt_file = f"srt_{os.path.basename(temp_file_name)}.srt"
        transcribe_audio(compressed_file, srt_file, language_options[selected_language], user_prompt, user_api_key)
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
