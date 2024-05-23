import pandas as pd
import numpy as np

def split_youtube_csv(csv_path):
    data=pd.read_csv(csv_path)

    data=data.drop(columns=['topic_ids', 'relevant_topic_ids'])
    # '-' 값을 포함하는 행을 삭제
    cols_to_check = ['hour', 'min', 'sec','watched_time']
    for col in cols_to_check:
        data = data[data[col] != '-']
        
    # 데이터 타입 변환
    dtype_dict = {
        'hour': 'int64',
        'min': 'int64',
        'sec': 'int64',
    }

    for col, dtype in dtype_dict.items():
        data[col] = data[col].astype(dtype)

    data.loc[data['sec'] == 1, 'sec'] = 60   # 60초 영상이 1초로 크롤링됨

    categories = {'1': 'Film & Animation', '2': 'Autos & Vehicles', '10': 'Music', '15': 'Pets & Animals', '17': 'Sports', '18': 'Short Movies', '19': 'Travel & Events', '20': 'Gaming', '21': 'Videoblogging', '22': 'People & Blogs', '23': 'Comedy', '24': 'Entertainment', '25': 'News & Politics', '26': 'Howto & Style', '27': 'Education', '28': 'Science & Technology', '30': 'Movies', '31': 'Anime/Animation', '32': 'Action/Adventure', '33': 'Classics', '34': 'Comedy', '35': 'Documentary', '36': 'Drama', '37': 'Family', '38': 'Foreign', '39': 'Horror', '40': 'Sci-Fi/Fantasy', '41': 'Thriller', '42': 'Shorts', '43': 'Shows', '44': 'Trailers'}
    data['category_id'] = data['category_id'].astype(str)
    # 카테고리 id를 이름으로 변환
    data['category_id'] = data['category_id'].map(categories)


    from datetime import datetime, timedelta

    def format_time(time_str):
        if time_str is None:
            return None

        # 문자열을 파싱 -> datetime 객체로 변환
        dt = datetime.fromisoformat(time_str.replace("Z", "+00:00"))    
        korea_time = dt + timedelta(hours=9)
        
        return korea_time.strftime("%Y-%m-%d %H:%M:%S")

    # 'watched_time' 열의 모든 값을 한국 시간대로 변환하여 문자열로 수정
    data['watched_time'] = data['watched_time'].apply(format_time)


    """
    일반 영상, 쇼츠 영상, 음악 분류
    """
    # 쇼츠 영상과 일반 영상 분류
    Youtube_shorts = data[(data['min'] == 0) & (data['hour'] == 0)]
    Youtube_shorts.reset_index(drop=True, inplace=True)
    YouTube_video = data[data['header'] == 'YouTube']
    YouTube_video.reset_index(drop=True, inplace=True)
    YouTube_music=data[data['header'] == 'YouTube Music']
    YouTube_music.reset_index(drop=True, inplace=True)
    
    print(YouTube_music)


    """
    쇼츠 영상과 유튜브 음악은 시청 시각 차이로 시청 시간까지 계산
    """
    # datetime으로 변환해서 계산
    Youtube_shorts['watched_time'] = pd.to_datetime(Youtube_shorts['watched_time'], format="%Y-%m-%d %H:%M:%S")
    # 실제 시청 시간 계산 (이전 영상 시청 시각과의 차이)
    Youtube_shorts['watched_duration'] = abs(Youtube_shorts['watched_time'].diff(1).dt.total_seconds().fillna(0))

    # datetime으로 변환해서 계산
    YouTube_music['watched_time'] = pd.to_datetime(YouTube_music['watched_time'], format="%Y-%m-%d %H:%M:%S")
    # 실제 시청 시간 계산 (이전 영상 시청 시각과의 차이)
    YouTube_music['watched_duration'] = abs(YouTube_music['watched_time'].diff(1).dt.total_seconds().fillna(0))


    def outlier_upper_bound(data, threshold=1.5):
        q1, q3 = np.percentile(data, [25, 75])  # 1사분위수, 3사분위수 계산
        IQR = q3 - q1  # IQR 계산
        lower_bound = q1 - (threshold * IQR)  # Outlier 판단 Lower Bound 계산
        upper_bound = q3 + (threshold * IQR)  # Outlier 판단 Upper Bound 계산
        return upper_bound
    
    shorts_upper_bound = outlier_upper_bound(Youtube_shorts['watched_duration'])
    music_upper_bound = outlier_upper_bound(YouTube_music['watched_duration'])
    
    Youtube_shorts = Youtube_shorts[Youtube_shorts['watched_duration']<=shorts_upper_bound]
    Youtube_music = YouTube_music[YouTube_music['watched_duration']<=music_upper_bound]

    return YouTube_video, Youtube_shorts, YouTube_music

if __name__ == '__main__':
    YouTube_video, Youtube_shorts, YouTube_music=split_youtube_csv(input('크롤링한 csv 파일 상대 경로:'))
    
    YouTube_video.to_csv("YouTube_video.csv")
    Youtube_shorts.to_csv("YouTube_shorts.csv")
    YouTube_music.to_csv("YouTube_music.csv")