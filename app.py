import os
import tempfile
import pydub
import streamlit as st
import time
from generate_subtitles import compress_audio, transcribe_audio
import base64
from io import BytesIO
import tempfile
from pathlib import Path



st.set_page_config(page_title='影片字幕生成', layout='wide')

st.title('影片字幕生成')

uploaded_file = st.file_uploader("請上傳 MP3 或 MP4 檔案：", type=["mp3", "mp4"])

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

    with st.spinner("生成字幕中..."):
        start_time = time.time()
        srt_file = transcribe_audio(compressed_file)
        elapsed_time = time.time() - start_time
        st.write(f"生成字幕所需時間：{elapsed_time:.2f} 秒")

    if srt_file is not None:
        total_elapsed_time = time.time() - total_start_time
        st.write(f"總共所需時間：{total_elapsed_time:.2f} 秒")

        st.success("字幕檔案已生成！")

        # Convert the SRT file into a downloadable format
        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_data = f.read()
        srt_bytes = srt_data.encode('utf-8')
        b64 = base64.b64encode(srt_bytes).decode()

        href = f'<a href="data:file/srt;base64,{b64}" download="{Path(srt_file).name}" target="_blank">點擊此處下載字幕檔案</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.error("無法生成字幕檔案。")

