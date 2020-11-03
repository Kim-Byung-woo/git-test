# -*- coding: utf-8 -*-
"""
Created on Wed Jul 22 18:10:57 2020

@author: A
"""
#%%
'''
============== Read me ================

video_url 변수에 크롤링 하고 싶은 유튜브 영상의 주소를 저장 후 프로그램을 실행해야 합니다.
1. https://www.youtube.com에 점속
2. 사용자가 원하는 유튜브 영상을 클릭합니다.
3. 해당 영상의 주소를 복사
4. video_url에 복사된 주소를 저장.
5. 프로그램(크콜링) 실행 -자동으로 크롬 드라이버 실행되오니 드라이버를 강제 종료, 최소화 하지 마시오.
6. 저장된 xlsx 파일 확인

'''
#%%
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from collections import Counter
from wordcloud import WordCloud
from konlpy.tag import Twitter

def get_noun(comment_txt):
    twitter = Twitter()
    noun = []
    
    if len(comment_txt)>0:
        tw = twitter.pos(comment_txt)
        for i,j in tw:
            if j == 'Noun':
                noun.append(i)
    return noun
#%%

# 크롬 드라이버 실행
path = 'chromedriver.exe'
driver = webdriver.Chrome(path)

# 크리에이터의 특정 video 페이지를 연다.
video_url = 'https://www.youtube.com/watch?v=CQA7cdxozHY&list=WL&index=19&t=0s' #  https://www.youtube.com/watch?v=gH_w8dOGAso
driver.get(video_url)

delay = 3
driver.implicitly_wait(delay)
#driver.maximize_window()
body = driver.find_element_by_tag_name('body')
time.sleep(delay)

SCROLL_PAUSE_TIME = 0.5 # 한번 스크롤 하고 멈출 시간 설정
# 더보기 버튼 클릭을 위해 최초 1회 스크롤 다운
#body.send_keys(Keys.PAGE_DOWN)
#time.sleep(SCROLL_PAUSE_TIME)

# 더보기 클릭
more_button = driver.find_element_by_xpath('//*[@id="more"]/yt-formatted-string')
more_button.click()

# 크롤링을 위해 화면 맨 아래까지 스크롤 내리기
while True:
    last_height = driver.execute_script('return document.documentElement.scrollHeight')
    # 현재 화면의 길이를 리턴 받아 last_height에 넣음
    for i in range(10):
        body.send_keys(Keys.PAGE_DOWN)
        # body 본문에 END키를 입력(스크롤내림)
        time.sleep(SCROLL_PAUSE_TIME)
    new_height = driver.execute_script('return document.documentElement.scrollHeight')
    if new_height == last_height:
        break;
    
html = driver.page_source
soup = BeautifulSoup(html, 'lxml')

# 댓글 id 추출
all_comment_id = soup.find_all('a', {'id' : 'author-text'})
comment_id = [soup.find_all('a', {'id' : 'author-text'})[n].text for n in range(0,len(all_comment_id))]
comment_id = [i.strip() for i in comment_id]

# 댓글 추출(답글 제외)
all_comment_contents = soup.find_all('yt-formatted-string', {'id' : 'content-text'})
comment_contents = [soup.find_all('yt-formatted-string', {'id' : 'content-text'})[n].text for n in range(len(all_comment_contents))]
comment_contents = [i.strip() for i in comment_contents]

# 댓글 데이터 프레임 생성
df_comment_info = pd.DataFrame()
df_comment_info['comment id'] = comment_id
df_comment_info['comment'] = comment_contents

# 각각의 태그들로 영상 정보추출을 한다.
video_title = soup.find('h1', 'title style-scope ytd-video-primary-info-renderer').text
channel_name = soup.find('ytd-channel-name', {'id' : 'channel-name'}).find('a', 'yt-simple-endpoint style-scope yt-formatted-string').text
subscribe = soup.find('yt-formatted-string',  {'id' : 'owner-sub-count'}).text
subscribe_num = (float(''.join(ele for ele in subscribe if ele.isdigit() or ele == '.'))) # 문자열에서 소수점 추출
if subscribe.find('만') != -1:
    subscribe_num = subscribe_num * 10000
elif subscribe.find('천') != -1:
    subscribe_num = subscribe_num * 1000
else:
    subscribe_num = subscribe_num
video_length = soup.find('span',  {'class' : 'ytp-time-duration'}).text
video_desc = soup.find('div', {'id' : 'description'}).text
upload_date = soup.find('div', {'id' : 'date'}).find('yt-formatted-string', 'style-scope ytd-video-primary-info-renderer').text
upload_date = upload_date.replace('. ', '-') # 날짜 포맷 수정
upload_date = upload_date.replace('.', '') # 날짜 포맷 수정
view_cnt = soup.find('span', 'view-count style-scope yt-view-count-renderer').text

like_count = soup.find('paper-tooltip', {'class' : "style-scope ytd-sentiment-bar-renderer"}).text
like_count = like_count.strip()
if like_count != '':
    like_cnt = int(like_count.split(' / ')[0].replace(',', ''))
    unlike_cnt = int(like_count.split(' / ')[1].replace(',', ''))
else:
    like_cnt = 'Private'
    unlike_cnt = 'Private'
    
comment_cnt = soup.find('ytd-comments', {'id' : 'comments'}).find('yt-formatted-string', 'count-text style-scope ytd-comments-header-renderer').text

driver.close()

# 영상 데이터 프레임 생성
df_video_info = pd.DataFrame()
df_video_info['channel name'] = pd.Series(channel_name)
df_video_info['subscribe count'] =  pd.Series(subscribe_num)
df_video_info['title'] = pd.Series(video_title)
# df_video_info['play time'] =  pd.Series(video_length) # 광고 영상이 있는 경우 광고영상의 길이를 가져옴
df_video_info['view count'] =  pd.Series(int(''.join(ele for ele in view_cnt if ele.isdigit() or ele == '.'))) # 문자열에서 숫자 추출
df_video_info['upload date'] =  pd.Series(upload_date)
df_video_info['like count'] =  like_cnt
df_video_info['unlike count'] =  unlike_cnt
df_video_info['comment count'] =  pd.Series(int(''.join(ele for ele in comment_cnt if ele.isdigit() or ele == '.'))) # 문자열에서 숫자 추출
df_video_info['describe'] =  pd.Series(video_desc)



# 이모티콘 제거
emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                u'\U00010000-\U0010ffff'  # not BMP characters
    "]+", flags=re.UNICODE)

# 분석에 어긋나는 불용어구 제외 (특수문자, 의성어)
han = re.compile(r'[ㄱ-ㅎㅏ-ㅣ!?~,".\n\r#\ufeff\u200d]')
 
# 그 다음으로는 기존의 데이터에서 댓글컬럼만 뽑아냅니다
comment_list = []
for i in range(len(df_comment_info)):
    comment_list.append(df_comment_info['comment'].iloc[i])
 

# 최종적으로 compile한 문자열을 이용하여 불용어구를 제외하고 댓글을 보기 쉽게 데이터 프레임으로 저장합니다.
comment_result = []
for i in comment_list:
    tokens = re.sub(emoji_pattern,"",i)
    tokens = re.sub(han,"",tokens)
    comment_result.append(tokens)

df_comment_info['mining comment'] = comment_result


# xlsx 파일 생성
xlxs_dir = channel_name + '_video_info.xlsx'
# Write two DataFrames to Excel using to_excel(). Need to specify an ExcelWriter object first.
# 2개 이상의 DataFrame을 하나의 엑셀 파일에 여러개의 Sheets 로 나누어서 쓰려면 먼저 pd.ExcelWriter() 객체를 지정한 후에, sheet_name 을 나누어서 지정하여 써주어야 합니다. 
with pd.ExcelWriter(xlxs_dir) as writer:
    df_video_info.to_excel(writer, sheet_name = 'video')
    df_comment_info.to_excel(writer, sheet_name = 'comment')
#%%
# load file

df_read_video_info = pd.read_excel(xlxs_dir, sheet_name = 'video')
df_read_comment = pd.read_excel(xlxs_dir, sheet_name = 'comment')


for idx in range(len(df_read_comment)):
    comment = df_read_comment.iloc[idx]['comment']
    print(comment)




