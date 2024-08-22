# subtitle_time_sync.py

import streamlit as st
import xml.etree.ElementTree as ET
import datetime
import re
from datetime import timedelta
import os
import tempfile

# 常量定義
DEFAULT_MAX_DIFFERENCE = 0.5
DEFAULT_FRAME_RATE = 30.0


class XMLParser:
    @staticmethod
    def parse_xml(xml_path):
        """解析XML文件，提取幀率和剪輯點"""
        tree = ET.parse(xml_path)
        root = tree.getroot()

        frame_rate = XMLParser._detect_frame_rate(root)
        cut_points = XMLParser._get_cut_points(root)

        return frame_rate, cut_points

    @staticmethod
    def _detect_frame_rate(root):
        """從XML中檢測幀率"""
        rate_elements = root.findall(".//rate")
        for rate_element in rate_elements:
            timebase = rate_element.find("timebase")
            ntsc = rate_element.find("ntsc")

            if timebase is not None and timebase.text:
                try:
                    frame_rate = float(timebase.text)
                    if ntsc is not None and ntsc.text.lower() == "true":
                        frame_rate = frame_rate * 1000 / 1001  # NTSC調整
                    return frame_rate
                except ValueError:
                    continue

        return DEFAULT_FRAME_RATE

    @staticmethod
    def _get_cut_points(root):
        """從XML中提取剪輯點"""
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
        """解析SRT文件，返回字幕數據"""
        with open(srt_path, "r", encoding="utf-8") as file:
            content = file.read()
        pattern = re.compile(
            r"(\d+:\d+:\d+,\d+) --> (\d+:\d+:\d+,\d+)\n(.*?)(?=\n\n|\Z)", re.DOTALL)
        return [(SRTParser._srt_time_to_timedelta(start), SRTParser._srt_time_to_timedelta(end), text.strip())
                for start, end, text in pattern.findall(content)]

    @staticmethod
    def _srt_time_to_timedelta(srt_time_str):
        """將SRT時間格式轉換為timedelta對象"""
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
        """將幀數轉換為timedelta對象"""
        return timedelta(seconds=frame / self.frame_rate)

    def adjust_subtitles(self, srt_data):
        """調整字幕時間"""
        adjusted_srt_data = []
        for start_time, end_time, text in srt_data:
            new_start_time = self._get_closest_cut_time(
                start_time) or start_time
            new_end_time = self._get_closest_cut_time(end_time) or end_time
            adjusted_srt_data.append((new_start_time, new_end_time, text))
        return adjusted_srt_data

    def _get_closest_cut_time(self, time):
        """獲取最接近的剪輯時間點"""
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
        """將調整後的字幕數據寫入SRT格式字符串"""
        srt_string = ""
        for i, (start_time, end_time, text) in enumerate(srt_data, start=1):
            srt_string += f"{i}\n"
            srt_string += f"{SRTWriter._timedelta_to_srt_time(start_time)} --> {
                SRTWriter._timedelta_to_srt_time(end_time)}\n"
            srt_string += f"{text}\n\n"
        return srt_string.rstrip()

    @staticmethod
    def _timedelta_to_srt_time(timedelta_obj):
        """將timedelta對象轉換為SRT時間格式"""
        total_seconds = int(timedelta_obj.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        milliseconds = timedelta_obj.microseconds // 1000
        return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def process_files(xml_path, srt_path, max_difference_seconds):
    """處理XML和SRT文件"""
    frame_rate, cut_points = XMLParser.parse_xml(xml_path)
    srt_data = SRTParser.parse_srt(srt_path)

    adjuster = SubtitleAdjuster(frame_rate, cut_points, max_difference_seconds)
    adjusted_srt_data = adjuster.adjust_subtitles(srt_data)

    return SRTWriter.write_srt(adjusted_srt_data), frame_rate


def main():
    st.title("字幕時間同步器")

    st.write("這個工具可以幫助您將 SRT 格式的字幕文件與影片的實際剪輯時間點同步。")

    with st.expander("點擊展開查看詳細說明"):
        st.markdown("""
        ### 應用簡介
        這個工具專為處理影片字幕時間同步而設計，能夠根據影片剪輯信息自動調整字幕時間，提升字幕的準確性和觀看體驗：

        1. **自動時間校正**：根據影片剪輯點自動調整字幕時間。
        2. **智能同步**：
           - 識別影片剪輯點，確保字幕與影片內容同步。
           - 自動處理時間差異，提高字幕顯示的精確度。
           - 支持各種常見的影片剪輯軟件導出的 XML 格式。

        ### 主要功能
        - 讀取影片剪輯軟件導出的 XML 文件，獲取影片剪輯信息
        - 自動調整 SRT 格式字幕的時間軸，使其與影片剪輯點同步
        - 允許自定義最大時間差，靈活處理不同場景
        - 保留原始字幕文本內容，只調整時間信息
        - 生成新的 SRT 文件，可直接用於視頻播放

        ### 使用步驟
        1. 上傳影片剪輯軟件導出的 XML 文件（包含影片剪輯信息）。
        2. 上傳需要校正的 SRT 字幕文件。
        3. 調整允許的最大時間差（可選）。
        4. 點擊「開始同步」按鈕。
        5. 下載同步後的 SRT 字幕文件。

        ### 注意事項
        - 確保上傳的 XML 文件包含正確的影片剪輯信息。
        - SRT 文件應為標準格式，以獲得最佳同步效果。
        - 最大時間差設置影響同步的靈敏度，請根據實際需求調整。
        - 如遇問題，請檢查原始文件格式是否符合要求。
        - 同步後的 SRT 文件使用 UTF-8 編碼，確保與大多數現代系統兼容。
        """)

    xml_file = st.file_uploader("上傳影片剪輯 XML 文件", type="xml")
    srt_file = st.file_uploader("上傳需要同步的 SRT 字幕文件", type="srt")

    if xml_file and srt_file:
        max_difference_seconds = st.slider(
            "最大允許的時間差 (秒)", 0.1, 2.0, DEFAULT_MAX_DIFFERENCE, 0.1)

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
                # 清理臨時文件
                os.unlink(tmp_xml_path)
                os.unlink(tmp_srt_path)


if __name__ == "__main__":
    main()
