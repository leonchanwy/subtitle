import gdown

def download_video_from_google_drive(link, output_file_name):
        gdown.download(google_drive_video_link, output_file_name, quiet=False, fuzzy=True)
        print(f"影片已成功下載並儲存為：{output_file_name}")

# 將以下變數替換為Google雲端硬碟影片的共享連結
google_drive_video_link = "https://drive.google.com/file/d/1CqaqOCTnbR9YQ2aMtyO3wO3l2gEK_HFQ/view?usp=sharing"

# 將以下變數替換為您想要儲存影片的檔案名稱
output_file_name = "video.mp4"

download_video_from_google_drive(google_drive_video_link, output_file_name)
