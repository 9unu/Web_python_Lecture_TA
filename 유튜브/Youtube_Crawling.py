from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
import numpy as np
import os
import time
from Yotube_info_extraction import video_info_extract  # 영상 정보 긁어오는 함수

def extract_vid_id(url):
    start_index = url.find("watch?v=")
    video_id = url[start_index + len("watch?v="):]
    return video_id

def Youtube_Crawling( json_path):
    DEVELOPER_KEY = "AIzaSyAQ8WczgeULi-om2ee2B023qXYdEBtIb6c"
    YOUTUBE_API_SERVICE_NAME = 'youtube'
    YOUTUBE_API_VERSION = 'v3'
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
    
    watched = pd.read_json(json_path, encoding='utf-8')
    watched['video_id'] = watched['titleUrl'].apply(extract_vid_id)
    
    # 이전에 저장된 데이터 불러오기
    prev_df_path = f"{json_path.replace('json', 'csv')}"
    if os.path.exists(prev_df_path):
        prev_df = pd.read_csv(prev_df_path)
        start_index = len(prev_df)  # 이전 데이터의 길이를 시작 인덱스로 설정
    else:
        prev_df = pd.DataFrame()
        start_index = 0

    total_df = prev_df

    k = 10
    try:
        while True:
            detail_df = video_info_extract(youtube, watched, start_index, start_index + k)
            if detail_df.empty:
                break
            total_df = pd.concat([total_df, detail_df], ignore_index=True)
            start_index += k
            if start_index > 6000:
                break
    except HttpError as err:
        print("api 한계에 도달했습니다.")
    finally:
        total_df.to_csv(f"{json_path.replace('json', 'csv')}", index=False)
        print("저장이 완료되었습니다.")

if __name__ == '__main__':
    json_path = input('시청기록 json 파일 상대 경로:')
    Youtube_Crawling(json_path)
