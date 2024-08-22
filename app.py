import streamlit as st
import os
import tempfile
from pydub import AudioSegment
import gdown
import time
import datetime
from generate_subtitles import compress_audio, transcribe_audio, translate_audio
import base64
from io import BytesIO
import re
from openai import OpenAI
import configparser
import chardet
import xml.etree.ElementTree as ET
from datetime import timedelta


# 設置頁面配置
st.set_page_config(page_title='剪接神器', layout='centered')

# 定義功能模塊


def ai_subtitle_generator():
    st.title('影片字幕生成')

    language_options = {
        '中文': 'zh', '英文': 'en', '日文': 'ja', '韓文': 'ko', '德語': 'de', '法語': 'fr',
        '阿非利堪斯語': 'af', '阿拉伯語': 'ar', '亞美尼亞語': 'hy', '亞塞拜然語': 'az',
        '白俄羅斯語': 'be', '波士尼亞語': 'bs', '保加利亞語': 'bg', '加泰隆尼亞語': 'ca',
        '克羅埃西亞語': 'hr', '捷克語': 'cs', '丹麥語': 'da', '荷蘭語': 'nl', '愛沙尼亞語': 'et',
        '芬蘭語': 'fi', '加利西亞語': 'gl', '希臘語': 'el', '希伯來語': 'he', '印地語': 'hi',
        '匈牙利語': 'hu', '冰島語': 'is', '印度尼西亞語': 'id', '義大利語': 'it', '卡納達語': 'kn',
        '哈薩克語': 'kk', '拉脫維亞語': 'lv', '立陶宛語': 'lt', '馬其頓語': 'mk', '馬來語': 'ms',
        '馬拉地語': 'mr', '毛利語': 'mi', '尼泊爾語': 'ne', '挪威語': 'no', '波斯語': 'fa',
        '波蘭語': 'pl', '葡萄牙語': 'pt', '羅馬尼亞語': 'ro', '俄語': 'ru', '塞爾維亞語': 'sr',
        '斯洛伐克語': 'sk', '斯洛維尼亞語': 'sl', '西班牙語': 'es', '斯瓦希里語': 'sw',
        '瑞典語': 'sv', '他加祿語': 'tl', '坦米爾語': 'ta', '泰語': 'th', '土耳其語': 'tr',
        '烏克蘭語': 'uk', '烏都語': 'ur', '越南語': 'vi', '威爾斯語': 'cy'
    }

    selected_language = st.selectbox(
        '請選擇轉譯語言：', options=list(language_options.keys()))
    translate_to_english = st.checkbox("翻譯成英文")
    default_prompt = '繁體！'
    user_prompt = st.text_input('請輸入 Prompt 以改進轉譯品質（如果轉譯語言不是中文，要刪去預設內容）：',
                                default_prompt,
                                help='提示可幫助改善轉譯。模型會匹配提示風格。')
    temperature = st.number_input('請輸入 Temperature：', value=0.6)
    user_api_key = st.text_input('請輸入您的 Open AI API 金鑰：', type="password")

    gdrive_url = st.text_input("或輸入 Google Drive 連結:")
    uploaded_file = st.file_uploader("或請上傳 MP3 或 MP4 檔案：", type=["mp3", "mp4"])

    if gdrive_url:
        output_file = "gdrive_file"
        gdown.download(gdrive_url, output_file, quiet=False, fuzzy=True)
        with open(output_file, "rb") as f:
            uploaded_file = BytesIO(f.read())

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
                translate_audio(compressed_file, srt_file,
                                user_prompt, user_api_key, temperature)
                elapsed_time = time.time() - start_time
                st.write(f"生成字幕並翻譯成英文所需時間：{elapsed_time:.2f} 秒")
        else:
            with st.spinner("生成字幕中..."):
                start_time = time.time()
                srt_file = f"srt_{os.path.basename(temp_file_name)}.srt"
                transcribe_audio(
                    compressed_file, srt_file, language_options[selected_language], user_prompt, user_api_key, temperature)
                elapsed_time = time.time() - start_time
                st.write(f"生成字幕所需時間：{elapsed_time:.2f} 秒")

        total_elapsed_time = time.time() - total_start_time
        st.write(f"總共所需時間：{total_elapsed_time:.2f} 秒")

        st.success("字幕檔案已生成！")

        with open(srt_file, 'r', encoding='utf-8') as f:
            srt_data = f.read()
        srt_bytes = srt_data.encode('utf-8')
        b64 = base64.b64encode(srt_bytes).decode()

        href = f'<a href="data:file/srt;base64,{b64}" download="{srt_file}" target="_blank">點擊此處下載字幕檔案</a>'
        st.markdown(href, unsafe_allow_html=True)

        st.markdown("以下是一些實用連結：")
        st.markdown(
            "- [合併兩個字幕](https://subtitletools.com/merge-subtitles-online)")
        st.markdown(
            "- [把雙行字幕變成英文大小50、中文大小75](https://colab.research.google.com/drive/16I1BLSC_LR6EFZOWGXBSJwIjJ4LfTq9s?usp=sharing)")
        st.markdown(
            "- [生成內容摘要SRT](https://colab.research.google.com/drive/1VgfPTfmbU2kjJ7nMXkmNMWcVbvOyqX0N?usp=sharing)")


def subtitle_time_sync():
    st.title("字幕時間同步器")

    class XMLParser:
        @staticmethod
        def parse_xml(xml_path):
            tree = ET.parse(xml_path)
            root = tree.getroot()
            frame_rate = XMLParser._detect_frame_rate(root)
            cut_points = XMLParser._get_cut_points(root)
            return frame_rate, cut_points

        @staticmethod
        def _detect_frame_rate(root):
            rate_elements = root.findall(".//rate")
            for rate_element in rate_elements:
                timebase = rate_element.find("timebase")
                ntsc = rate_element.find("ntsc")
                if timebase is not None and timebase.text:
                    try:
                        frame_rate = float(timebase.text)
                        if ntsc is not None and ntsc.text.lower() == "true":
                            frame_rate = frame_rate * 1000 / 1001
                        return frame_rate
                    except ValueError:
                        continue
            return 30.0

        @staticmethod
        def _get_cut_points(root):
            video_tracks = root.findall(
                ".//video/track") + root.findall(".//video")
            cut_points = []
            for track in video_tracks:
                clipitems = track.findall(
                    ".//clipitem") + track.findall("clipitem")
                for clipitem in clipitems:
                    start_element = clipitem.find("start")
                    end_element = clipitem.find("end")
                    if start_element is not None and start_element.text and start_element.text != "0":
                        cut_points.append(int(start_element.text))
                    if end_element is not None and end_element.text and end_element.text != "-1":
                        cut_points.append(int(end_element.text))
            return cut_points

    class SRTParser:
        @staticmethod
        def parse_srt(srt_path):
            with open(srt_path, "r", encoding="utf-8") as file:
                content = file.read()
            pattern = re.compile(
                r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.*?)(?=\n\n|\Z)", re.DOTALL)
            return [(SRTParser._srt_time_to_timedelta(start), SRTParser._srt_time_to_timedelta(end), text.strip())
                    for start, end, text in pattern.findall(content)]

        @staticmethod
        def _srt_time_to_timedelta(srt_time_str):
            hours, minutes, seconds = srt_time_str.split(':')
            seconds, milliseconds = seconds.split(',')
            return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds), milliseconds=int(milliseconds))

    class SubtitleAdjuster:
        def __init__(self, frame_rate, cut_points, max_difference_seconds):
            self.frame_rate = frame_rate
            self.cut_points = [self._frame_to_timedelta(
                frame) for frame in cut_points]
            self.max_difference_seconds = max_difference_seconds

        def _frame_to_timedelta(self, frame):
            return timedelta(seconds=frame / self.frame_rate)

        def adjust_subtitles(self, srt_data):
            adjusted_srt_data = []
            for start_time, end_time, text in srt_data:
                new_start_time = self._get_closest_cut_time(
                    start_time) or start_time
                new_end_time = self._get_closest_cut_time(end_time) or end_time
                adjusted_srt_data.append((new_start_time, new_end_time, text))
            return adjusted_srt_data

        def _get_closest_cut_time(self, time):
            min_difference = timedelta(hours=9999)
            closest_cut_time = None
            for cut_time in self.cut_points:
                difference = abs(cut_time - time)
                if difference < min_difference:
                    min_difference = difference
                    closest_cut_time = cut_time
            return closest_cut_time if min_difference <= timedelta(seconds=self.max_difference_seconds) else None

    class SRTWriter:
        @staticmethod
        def write_srt(srt_data):
            srt_string = ""
            for i, (start_time, end_time, text) in enumerate(srt_data, start=1):
                srt_string += f"{i}\n"
                srt_string += f"{SRTWriter._timedelta_to_srt_time(start_time)} --> {SRTWriter._timedelta_to_srt_time(end_time)}\n"
                srt_string += f"{text}\n\n"
            return srt_string.rstrip()

        @staticmethod
        def _timedelta_to_srt_time(timedelta_obj):
            total_seconds = int(timedelta_obj.total_seconds())
            hours, remainder = divmod(total_seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = timedelta_obj.microseconds // 1000
            return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

    def process_files(xml_path, srt_path, max_difference_seconds):
        frame_rate, cut_points = XMLParser.parse_xml(xml_path)
        srt_data = SRTParser.parse_srt(srt_path)

        adjuster = SubtitleAdjuster(
            frame_rate, cut_points, max_difference_seconds)
        adjusted_srt_data = adjuster.adjust_subtitles(srt_data)

        return SRTWriter.write_srt(adjusted_srt_data), frame_rate

    xml_file = st.file_uploader("上傳影片剪輯 XML 文件", type="xml")
    srt_file = st.file_uploader("上傳需要同步的 SRT 字幕文件", type="srt")

    if xml_file and srt_file:
        max_difference_seconds = st.slider("最大允許的時間差 (秒)", 0.1, 2.0, 0.5, 0.1)

        if st.button("開始同步"):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".xml") as tmp_xml:
                tmp_xml.write(xml_file.getvalue())
                tmp_xml_path = tmp_xml.name

            with tempfile.NamedTemporaryFile(delete=False, suffix=".srt") as tmp_srt:
                tmp_srt.write(srt_file.getvalue())
                tmp_srt_path = tmp_srt.name

            try:
                adjusted_content, detected_frame_rate = process_files(
                    tmp_xml_path, tmp_srt_path, max_difference_seconds)
                st.success(f"字幕時間同步完成！檢測到的幀率：{detected_frame_rate:.2f}")
                st.download_button(
                    label="下載同步後的 SRT 字幕文件",
                    data=adjusted_content,
                    file_name="同步後的字幕.srt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"處理過程中出現錯誤：{str(e)}")
            finally:
                os.unlink(tmp_xml_path)
                os.unlink(tmp_srt_path)


def bilingual_subtitle_resizer():
    st.title('雙語字幕大小調整器')

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


def bilingual_srt_translator():
    st.title("雙語字幕翻譯器")

    def load_config():
        config = configparser.ConfigParser()
        config_file = 'settings.cfg'

        if os.path.exists(config_file):
            with open(config_file, 'rb') as f:
                content = f.read()
                encoding = chardet.detect(content)['encoding']
            config.read(config_file, encoding=encoding)
        else:
            config['option'] = {'openai-apikey': '', 'target-language': ''}
            with open(config_file, 'w') as f:
                config.write(f)

        return config

    @st.cache_resource
    def get_openai_client(api_key):
        return OpenAI(api_key=api_key)

    def split_text(text):
        blocks = re.split(r'(\n\s*\n)', text)
        short_text_list = []
        short_text = ""
        for block in blocks:
            if len(short_text + block) <= 1024:
                short_text += block
            else:
                short_text_list.append(short_text)
                short_text = block
        short_text_list.append(short_text)
        return short_text_list

    def is_translation_valid(original_text, translated_text):
        original_blocks = original_text.strip().split('\n\n')
        translated_blocks = translated_text.strip().split('\n\n')

        if len(original_blocks) != len(translated_blocks):
            return False

        for orig_block, trans_block in zip(original_blocks, translated_blocks):
            orig_lines = orig_block.split('\n')
            trans_lines = trans_block.split('\n')

            if len(trans_lines) != 4:
                return False

            if orig_lines[0] != trans_lines[0] or orig_lines[1] != trans_lines[1]:
                return False

        return True

    def translate_text(text, client, first_language, second_language, custom_prompt):
        max_retries = 3
        for _ in range(max_retries):
            try:
                completion = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": f"""
    Translate the following SRT subtitle block to {first_language} and {second_language}.
    Follow this exact format for each subtitle:

    [subtitle number]
    [timestamp]
    [{first_language} translation]
    [{second_language} translation]

    Maintain the original subtitle numbering and timing. {custom_prompt}
    Do not include any introductory or explanatory text in your response.
    """},
                        {"role": "user", "content": text},
                        {"role": "user", "content": "translate:"}
                    ]
                )
                translated_text = completion.choices[0].message.content

                filtered_lines = []
                current_block = []
                for line in translated_text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith("Sure,") and not line.startswith("以下是"):
                        current_block.append(line)
                        if len(current_block) == 4:
                            filtered_lines.extend(current_block)
                            filtered_lines.append('')
                            current_block = []

                filtered_text = '\n'.join(filtered_lines).strip()

                if is_translation_valid(text, filtered_text):
                    return filtered_text
            except Exception as e:
                st.error(f"翻譯錯誤：{e}")
        return text

    def validate_srt(srt_content):
        lines = srt_content.strip().split('\n')
        errors = []
        subtitle_count = 0
        line_number = 0

        while line_number < len(lines):
            subtitle_count += 1

            if line_number >= len(lines) or not lines[line_number].strip().isdigit():
                errors.append(
                    f"錯誤：第 {line_number + 1} 行，預期為字幕編號 {subtitle_count}")
                break

            line_number += 1
            if line_number >= len(lines) or not re.match(r'\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', lines[line_number]):
                errors.append(f"錯誤：第 {line_number + 1} 行，時間戳格式不正確")
                break

            line_number += 1
            if line_number >= len(lines) or not lines[line_number].strip():
                errors.append(f"錯誤：第 {line_number + 1} 行，第一語言字幕缺失")
                break

            line_number += 1
            if line_number >= len(lines) or not lines[line_number].strip():
                errors.append(f"錯誤：第 {line_number + 1} 行，第二語言字幕缺失")
                break

            line_number += 1
            if line_number < len(lines) and lines[line_number].strip():
                errors.append(f"錯誤：第 {line_number + 1} 行，預期為空行")
                break

            line_number += 1

        if not errors:
            return True, f"SRT 文件格式正確。共有 {subtitle_count} 個字幕。"
        else:
            return False, "\n".join(errors)

    def process_srt_file(file, client, first_language, second_language, custom_prompt):
        start_time = time.time()
        content = file.getvalue().decode("utf-8")
        short_text_list = split_text(content)

        translated_text = ""
        progress_bar = st.progress(0)
        for i, short_text in enumerate(short_text_list):
            translated_short_text = translate_text(
                short_text, client, first_language, second_language, custom_prompt)
            translated_text += f"{translated_short_text}\n\n"
            progress_bar.progress((i + 1) / len(short_text_list))

        end_time = time.time()
        processing_time = end_time - start_time
        return translated_text, processing_time

    config = load_config()
    default_api_key = config.get('option', 'openai-apikey', fallback='')

    api_key = st.text_input(
        "OpenAI API Key", value=default_api_key, type="password")
    first_language = st.text_input("第一語言", value="traditional chinese")
    second_language = st.text_input("第二語言", value="malay")
    custom_prompt = st.text_area(
        "自定義翻譯提示",
        "第一個語言是台灣式口語加上髒話、第二個語言要極度口語"
    )

    client = get_openai_client(api_key)

    uploaded_file = st.file_uploader("選擇一個 SRT 文件", type="srt")

    if uploaded_file is not None:
        if st.button("翻譯"):
            if not first_language or not second_language:
                st.error("請在翻譯之前輸入兩種語言。")
            else:
                with st.spinner("正在翻譯..."):
                    translated_srt, processing_time = process_srt_file(
                        uploaded_file, client, first_language, second_language, custom_prompt)

                    is_valid, validation_message = validate_srt(translated_srt)
                    if is_valid:
                        st.success("翻譯完成！SRT 格式驗證通過。")
                        st.info(validation_message)
                    else:
                        st.warning("翻譯完成，但 SRT 格式可能有問題。")
                        st.error(validation_message)

                    st.subheader("翻譯預覽")
                    st.text_area(
                        "", value=translated_srt[:1000] + "...", height=300)

                    st.download_button(
                        label="下載雙語 SRT",
                        data=translated_srt,
                        file_name="dual_language.srt",
                        mime="text/plain"
                    )

                    st.markdown(f"<p style='font-size: 10px; text-align: right;'>總處理時間：{processing_time:.2f} 秒</p>", unsafe_allow_html=True)


def main():
    st.sidebar.title("剪接神器")

    # 使用 sidebar.radio 來讓使用者選擇頁面
    page = st.sidebar.radio("選擇功能",
                            ("AI 生成字幕", "雙語字幕翻譯器", "雙語字幕大小調整器", "字幕時間同步器"),
                            captions=["把聲音轉譯成字幕","翻譯 SRT 文件","調整雙語字幕大小","同步字幕與分鏡點的時間"])

    # 根據選擇的頁面來顯示內容
    if page == "AI 生成字幕":
        ai_subtitle_generator()
    elif page == "字幕時間同步器":
        subtitle_time_sync()
    elif page == "雙語字幕大小調整器":
        bilingual_subtitle_resizer()
    elif page == "雙語字幕翻譯器":
        bilingual_srt_translator()


if __name__ == "__main__":
    main()
