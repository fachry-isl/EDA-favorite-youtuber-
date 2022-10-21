def get_channel_stats(youtube, channel_ids):
    
    """
    Get channel stats
    
    Params:
    ------
    youtube: build object of Youtube API
    channel_ids: list of channel IDs
    
    Returns:
    ------
    dataframe with all channel stats for each channel ID
    
    """
    
    all_data = []

    request = youtube.channels().list(
        part="snippet,contentDetails,statistics",
        id=channel_ids
    )
    response = request.execute()
    
    for item in response['items']:
        data = {'channelName': item['snippet']['title'],
                'subscribers': item['statistics']['subscriberCount'],
                'views': item['statistics']['viewCount'],
                'totalVideos': item['statistics']['videoCount'],
                'playlistId': item['contentDetails']['relatedPlaylists']['uploads']
        }
        
        all_data.append(data)
    
    return(pd.DataFrame(all_data))

def get_video_ids(youtube, playlist_id):
    
    """
    Get video ids
    
    Params:
    ------
    youtube: build object of Youtube API
    playlist_id: playlist id of the channel
    
    Returns:
    ------
    dataframe with id of each videos
    
    """
    
    video_ids = []
    
    request = youtube.playlistItems().list(
        part="snippet,contentDetails",
        playlistId=playlist_id,
        maxResults = 50
    )
    response = request.execute()
    
    for item in response['items']:
        video_ids.append(item['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    while next_page_token is not None:
        request = youtube.playlistItems().list(
                    part='contentDetails',
                    playlistId = playlist_id,
                    maxResults = 50,
                    pageToken = next_page_token)
        response = request.execute()

        for item in response['items']:
            video_ids.append(item['contentDetails']['videoId'])

        next_page_token = response.get('nextPageToken')
        
    return video_ids

def get_video_details(youtube, video_ids):
    
    """
    Get video details
    
    Params:
    ------
    youtube: build object of Youtube API
    video_ids: list of channel IDs
    
    Returns:
    ------
    dataframe with video details for each video ID
    
    """

    all_video_info = []
    
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute() 

        for video in response['items']:
            stats_to_keep = {'snippet': ['channelTitle', 'title', 'categoryId', 'description', 'tags', 'publishedAt'],
                             'statistics': ['viewCount', 'likeCount', 'commentCount'],
                             'contentDetails': ['duration', 'definition', 'caption']
                            }
            video_info = {}
            video_info['video_id'] = video['id']

            for k in stats_to_keep.keys():
                for v in stats_to_keep[k]:
                    try:
                        video_info[v] = video[k][v]
                    except:
                        video_info[v] = None

            all_video_info.append(video_info)
        
    
    return pd.DataFrame(all_video_info)

def get_video_categories(youtube, categoryIds):
    """
    Get video categories by using ID
    
    Params:
    ------
    youtube: build object of Youtube API
    category_ids: list of category IDs
    
    Returns:
    ------
    dictionary of category title for each category ID
    
    """
    
    category_info = {}
    
    request = youtube.videoCategories().list(
        part="snippet",
        id=categoryIds
    )
    
    response = request.execute()
    
    for category in response['items']:
        # Make a dictionary that will contain 
        # categoryid followed with the categorytitle
        id = category['id']
        title  = category['snippet']['title']    
        category_info[id] = title
    
    return category_info
def generate_others_category(df):
    # Count total values for percentage
    total = 0
    for key, value in df.items():
        total += value
    
    # Count percentage of occurunces for each category
    dfcat_percentage = {key: (value / total)*100 for key, value in df.items()}
    others_count = 0
    
    dfcat_minority = dfcat_percentage.copy()
    
    # Get list of key for other candidates
    list_oth = []
    for key,value in dfcat_minority.items():
        if value < 10:
            list_oth.append(key)
    
    # to prevent error during dictionary changes, copy df
    df_copy = df.copy()
    count_oth = 0
    for key, value in df_copy.items():
        if key in list_oth:
            count_oth += value
            df.pop(key)
        df['Others'] = count_oth
        
    return df

def get_comments_in_videos(youtube, video_ids):
    """
    Get top level comments as text from all videos with given IDs (only the first 10 comments due to quote limit of Youtube API)
    Params:
    
    youtube: the build object from googleapiclient.discovery
    video_ids: list of video IDs
    
    Returns:
    Dataframe with video IDs and associated top level comment in text.
    
    """
    all_comments = []
    
    for video_id in video_ids:
        try:   
            request = youtube.commentThreads().list(
                part="snippet,replies",
                videoId=video_id
            )
            response = request.execute()
        
            comments_in_video = [comment['snippet']['topLevelComment']['snippet']['textOriginal'] for comment in response['items'][0:10]]
            comments_in_video_info = {'video_id': video_id, 'comments': comments_in_video}

            all_comments.append(comments_in_video_info)
            
        except: 
            # When error occurs - most likely because comments are disabled on a video
            print('Could not get comments for video ' + video_id)
        
    return pd.DataFrame(all_comments)     