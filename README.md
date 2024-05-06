# AT字幕神器（aka 影音轉譯字幕與下載工具）

這是一個多功能的影音轉譯字幕與下載工具，使用 Streamlit 框架開發，主要功能包括：

1. AI 生成字幕：將影片或音訊轉譯成多種語言的字幕，並可選擇翻譯成英文。
2. YouTube to MP3：從 YouTube 影片下載音訊並轉換為 MP3 格式。
3. YouTube to MP4：從 YouTube 影片下載影片並轉換為 MP4 格式。

## 開啓方法 1 : 網頁

1. 點擊以下連結：https://subtitle.streamlit.app/
2. 享受！

備註：這個方法不穩定性很高。

## 開啓方法 2 : Google Colab

1. 點擊以下連結：[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/drive/1rdTyl0cKwCT0-PJl1fknjUsfR8yWasbe)
2. 按播放按鍵執行，等待約半分鐘。
3. 上一步會產生一個 URL 和格式為 XXX.XXX.XXX.XXX 的 IP 位置（通常在倒數第三行）。
4. 複製 IP 位置並登入 URL。
5. 輸入剛複製的 IP 位置並 Submit。
6. 享受！


## 開啓方法 3 : Local

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
5. 享受！

## 使用方法

### AI 生成字幕

1. 選擇轉譯語言。
2. 選擇是否翻譯成英文。
3. 輸入 Prompt 以改進轉譯品質（可選）。
4. 輸入 Temperature 值（可選）。
5. 輸入您的 OpenAI API 金鑰。
6. 輸入以下任一內容。
* YouTube 影片網址
* Google Drive 連結
* 直接上傳 MP3 或 MP4 檔案
8. 等待應用程式生成字幕檔案，然後下載。

### YouTube to MP3

1. 輸入 YouTube 影片網址。
2. 點擊「Download Audio」按鈕。
3. 等待應用程式下載並轉換音訊，然後下載 MP3 檔案。

### YouTube to MP4

1. 輸入 YouTube 影片網址。
2. 點擊「Download Video」按鈕。
3. 等待應用程式下載並轉換影片，然後下載 MP4 檔案。

## 注意事項

1. 使用 AI 生成字幕功能需要有效的 OpenAI API 金鑰。
2. 請確保您有權下載和使用 YouTube 影片及音訊。

## 貢獻
1. 歡迎提交 Pull Request 和 Issue 以改進這個專案。

## 授權
1. 本專案採用 MIT 授權。
