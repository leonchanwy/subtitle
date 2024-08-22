import streamlit as st
import io
import re


def escape_html(unsafe):
    return (unsafe
            .replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
            .replace("'", "&#039;"))


def format_time(time):
    return time.replace(',', '.')


def srt_to_ttml(srt_content, font_size_1, font_size_2):
    srt_lines = srt_content.strip().split('\n\n')
    ttml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<tt xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <head>
    <styling>
      <style xml:id="style1" tts:fontSize="{font_size_1}px" tts:fontFamily="Noto Sans CJK TC" tts:fontWeight="bold" tts:textShadow="2px 2px 2px black" tts:textAlign="center" tts:displayAlign="after"/>
      <style xml:id="style2" tts:fontSize="{font_size_2}px" tts:fontFamily="Noto Sans CJK TC" tts:fontWeight="bold" tts:textShadow="2px 2px 2px black" tts:textAlign="center" tts:displayAlign="after"/>
    </styling>
  </head>
  <body>
    <div>'''

    for srt_line in srt_lines:
        lines = srt_line.split('\n')
        index = lines[0]
        start_time, end_time = map(format_time, lines[1].split(' --> '))

        num_lines = len(lines[2:])
        for i, line in enumerate(lines[2:]):
            escaped_line = escape_html(line)
            if num_lines == 1:
                style_id = "style1"
            else:
                if i == 0 and line.startswith("-"):
                    style_id = "style1"
                else:
                    style_id = "style1" if i == 0 else "style2"

            ttml_content += f'''
      <p xml:id="caption{index}_{i+1}" begin="{start_time}" end="{end_time}" style="{style_id}">{escaped_line}</p>'''

    ttml_content += '''
    </div>
  </body>
</tt>'''

    return ttml_content


st.title('雙語字幕大小調整工具')

with st.expander("點擊展開查看詳細說明"):
    st.markdown("""
    ### 應用簡介
    這個工具專為處理雙行字幕而設計，支持自定義字幕大小，提升字幕的靈活性和觀看體驗：

    1. **自定義字體大小**：為第一行和第二行分別設置字體大小。
    2. **智能布局**：
       - 單行字幕：使用第一行的字體大小。
       - 雙行字幕：第一行使用較大字體，第二行使用較小字體。
       - 對話格式：當檢測到以破折號（-）開頭的對話時，兩行都使用第一行的字體大小。

    ### 主要功能
    - 將 SRT 格式字幕轉換為 TTML 格式
    - 允許自定義設置每行字幕的大小
    - 自動調整字幕大小，優化雙行字幕的顯示效果
    - 保留原始時間軸和文本內容
    - 生成符合標準的 TTML 文件，兼容各種播放器和平台

    ### 使用步驟
    1. 設置希望的字體大小。
    2. 上傳 SRT 格式字幕文件。
    3. 點擊 "轉換文件" 按鈕。
    4. 預覽轉換後的 TTML 內容。
    5. 下載生成的 XML 文件。

    ### 注意事項
    - 確保 SRT 文件格式正確，以獲得最佳轉換效果。
    - 字體大小設置影響所有字幕，請根據需求和播放設備調整。
    - 轉換後的 TTML 文件使用 UTF-8 編碼，確保與大多數現代系統兼容。
    - 如遇問題，請檢查原始 SRT 文件的格式是否符合標準。
    """)

col1, col2 = st.columns(2)
with col1:
    font_size_1 = st.number_input(
        "第一行字體大小（像素）", min_value=1, max_value=100, value=71)
with col2:
    font_size_2 = st.number_input(
        "第二行字體大小（像素）", min_value=1, max_value=100, value=45)

uploaded_file = st.file_uploader("選擇一個 SRT 文件", type="srt")

if uploaded_file is not None:
    srt_content = uploaded_file.getvalue().decode("utf-8")

    if st.button('轉換文件'):
        ttml_content = srt_to_ttml(srt_content, font_size_1, font_size_2)
        st.text_area("TTML 輸出", ttml_content, height=300)

        st.download_button(
            label="下載 XML",
            data=ttml_content,
            file_name="output.xml",
            mime="application/xml"
        )
