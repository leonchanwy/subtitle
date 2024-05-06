# 影音轉譯與下載工具

這是一個多功能的影音轉譯與下載工具，使用 Streamlit 框架開發，主要功能包括：

1. AI 生成字幕：將影片或音訊轉譯成多種語言的字幕，並可選擇翻譯成英文。
2. YouTube to MP3：從 YouTube 影片下載音訊並轉換為 MP3 格式。
3. YouTube to MP4：從 YouTube 影片下載影片並轉換為 MP4 格式。

## 安裝與使用

1. 克隆此儲存庫到本地端：
  ```bash
  git clone https://github.com/leonchanwy/subtitle.git
  ```
2. 進入專案目錄並安裝所需的套件：
  ```bash
cd subtitle
  ```
  ```bash
pip install -r requirements.txt
  ``` 

3. 執行應用程式：
  ```bash
streamlit run app.py
  ```
4. 在瀏覽器中開啟 Streamlit 應用程式。

## AI 生成字幕

選擇轉譯語言。
選擇是否翻譯成英文。
輸入 Prompt 以改進轉譯品質（可選）。
輸入 Temperature 值（可選）。
輸入您的 OpenAI API 金鑰。
輸入 YouTube 影片網址、Google Drive 連結或直接上傳 MP3 或 MP4 檔案。
等待應用程式生成字幕檔案，然後下載。

## YouTube to MP3

輸入 YouTube 影片網址。
點擊「Download Audio」按鈕。
等待應用程式下載並轉換音訊，然後下載 MP3 檔案。

## YouTube to MP4

輸入 YouTube 影片網址。
點擊「Download Video」按鈕。
等待應用程式下載並轉換影片，然後下載 MP4 檔案。

## 注意事項

使用 AI 生成字幕功能需要有效的 OpenAI API 金鑰。
請確保您有權下載和使用 YouTube 影片及音訊。
應用程式僅供個人使用，不得用於商業用途。

## 貢獻
歡迎提交 Pull Request 和 Issue 以改進這個專案。

## 授權
本專案採用 MIT 授權。
