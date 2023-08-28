import streamlit as st
import os
import base64

st.title("YouTube Audio Downloader")

# 輸入 YouTube 影片網址
url = st.text_input("Enter the YouTube video URL:")

if url:
    # 當按下按鈕時執行
    if st.button("Download Audio"):
        # 為輸出文件指定一个名称
        output_file = "downloaded_audio.mp3"
        
        # 使用 yt-dlp 下載音頻到指定的文件名
        command = f'yt-dlp -x --audio-format mp3 -o "{output_file}" "{url}"'
        os.system(command)
        
        # 讀取音頻文件並转换为 Base64
        with open(output_file, 'rb') as f:
            audio_data = f.read()
        b64 = base64.b64encode(audio_data).decode()
        
        # 提供下載链接
        href = f'<a href="data:audio/mpeg;base64,{b64}" download="{output_file}" target="_blank">點擊此處下載音頻檔案</a>'
        st.markdown(href, unsafe_allow_html=True)
