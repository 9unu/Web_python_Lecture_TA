import re
import pandas as pd

def video_info_extract(youtube, YouTube_video, start_idx, end_idx):
    
    YouTube_video = YouTube_video[['title', 'video_id', 'time','header']][start_idx:end_idx]
    headers=[]
    titles = []
    ids = []
    dates = []
    category_ids = []
    views = []
    likes = []
    dislikes = []
    comments = []
    hours = []
    mins = []
    secs = []
    watched_time = []
    descriptions = []
    thumbnails = []
    channel_titles = []
    tags = []
    dimensions = []
    definitions = []
    captions = []
    licensed_contents = []
    topic_ids = []
    relevant_topic_ids = []

    for i in range(len(YouTube_video)):
        request = youtube.videos().list(
            id=YouTube_video.iloc[i]['video_id'],
            part='snippet, contentDetails, statistics, topicDetails'
        )

        response = request.execute()

        if not response['items']:
            titles.append('-')
            ids.append('-')
            dates.append('-')
            category_ids.append('-')
            views.append('-')
            likes.append('-')
            dislikes.append('-')
            comments.append('-')
            hours.append('-')
            mins.append('-')
            secs.append('-')
            watched_time.append('-')
            headers.append('-')

            # 추가된 정보
            descriptions.append('-')
            thumbnails.append('-')
            channel_titles.append('-')
            tags.append('-')
            dimensions.append('-')
            definitions.append('-')
            captions.append('-')
            licensed_contents.append('-')
            topic_ids.append('-')
            relevant_topic_ids.append('-')
        else:
            item = response['items'][0]

            # 기존의 정보
            titles.append(item['snippet']['title'])
            ids.append(YouTube_video.iloc[i]['video_id'])
            dates.append(item['snippet']['publishedAt'].split('T')[0])
            category_ids.append(item['snippet']['categoryId'])

            statistics = item.get('statistics', {})
            views.append(statistics.get('viewCount', 0))
            likes.append(statistics.get('likeCount', 0))
            dislikes.append(statistics.get('dislikeCount', 0))
            comments.append(statistics.get('commentCount', 0))
            watched_time.append(YouTube_video.iloc[i]['time']) 
            headers.append(YouTube_video.iloc[i]['header'])
            descriptions.append(item['snippet']['description'])
            thumbnails.append(item['snippet']['thumbnails']['default']['url'])
            channel_titles.append(item['snippet']['channelTitle'])
            tags.append(", ".join(item['snippet'].get('tags', [])))
            dimensions.append(item['contentDetails']['dimension'])
            definitions.append(item['contentDetails']['definition'])
            captions.append(item['contentDetails']['caption'])
            licensed_contents.append(item['contentDetails']['licensedContent'])
            topic_ids.append(", ".join(item.get('topicDetails', {}).get('topicIds', [])))
            relevant_topic_ids.append(", ".join(item.get('topicDetails', {}).get('relevantTopicIds', [])))

            duration = re.findall(r'(\d+)', item['contentDetails']['duration'])
            if len(duration) == 3:
                hours.append(duration[0])
                mins.append(duration[1])
                secs.append(duration[2])
            elif len(duration) == 2:
                hours.append('0')
                mins.append(duration[0])
                secs.append(duration[1])
            else:
                hours.append('0')
                mins.append('0')
                secs.append(duration[0])

    detail_df = pd.DataFrame([
        headers,titles, ids, dates, category_ids, views, likes, comments, hours, mins, secs, watched_time,
        descriptions, thumbnails, channel_titles, tags, dimensions, definitions, captions, licensed_contents,
        topic_ids, relevant_topic_ids
    ]).T

    detail_df.columns = [
        'header','title', 'id', 'date', 'category_id', 'view', 'like', 'comment', 'hour', 'min', 'sec', 'watched_time',
        'description', 'thumbnail', 'channel_title', 'tags', 'dimension', 'definition', 'caption', 'licensed_content',
        'topic_ids', 'relevant_topic_ids'
    ]

    return detail_df