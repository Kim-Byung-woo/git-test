# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 01:29:23 2020

@author: user

"""
#%%
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import re
import time
import codecs
import os

#%%
## 파일에서 단어를 불러와 posneg리스트를 만드는 코드

positive = [] 
negative = [] 
posneg = []

file_dir = os.getcwd() # 현재 파일 경로 추출
file_dir = os.path.dirname(file_dir) # 상위 경로 추출 - 코드 파일과 단어 리스트 파일 위치가 틀려서

# pos = codecs.open("./positive_words_self.txt", 'rb', encoding='UTF-8') 
pos = codecs.open(file_dir + "/positive_words_self.txt", 'rb', encoding='UTF-8') 

while True: 
    line = pos.readline() 
    line = line.replace('\n', '') 
    positive.append(line) 
    posneg.append(line) 
    
    if not line: break 
pos.close()
 
neg = codecs.open(file_dir + "/negative_words_self.txt", 'rb', encoding='UTF-8')

while True: 
    line = neg.readline() 
    line = line.replace('\n', '') 
    negative.append(line) 
    posneg.append(line) 
    
    if not line: break 
neg.close()
#%%
# 크롤링한 댓글 불러오기
xlxs_dir = file_dir + '/data/comment_sample.xlsx'

df_video_info = pd.read_excel(xlxs_dir, sheet_name = 'video')
df_comment = pd.read_excel(xlxs_dir, sheet_name = 'comment')

for idx in range(len(df_comment)):
    comment = df_comment.iloc[idx]['comment']
    print(comment)
#%%
# 댓글 전처리
    
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
list_comment = []
for i in range(len(df_comment)):
    list_comment.append(df_comment['comment'].iloc[i])
 

# 최종적으로 compile한 문자열을 이용하여 불용어구를 제외하고 댓글을 보기 쉽게 데이터 프레임으로 저장합니다.
list_prep_comment = [] # 전처리된 댓글 리스트
for i in list_comment:
    tokens = re.sub(emoji_pattern,"",str(i))
    tokens = re.sub(han,"",tokens)
    list_prep_comment.append(tokens)

# 네이버 맞춤법 검사 후 수정
from hanspell import spell_checker
list_prep_comment = [spell_checker.check(x).checked for x in list_prep_comment]

#%% 형태소 추출
from konlpy.tag import *

kkma = Kkma()
komoran = Komoran()
okt = Okt() 

list_kkma = []
for i in list_prep_comment:
    b = kkma.morphs(i) # morphs: 형태소 추출
    list_kkma.append(b) # 추출된 형태소를 list에 추가

list_komoran = []
for i in list_prep_comment:
    b = komoran.morphs(i) # morphs: 형태소 추출    
    list_komoran.append(b) # 추출된 형태소를 list에 추가
    
list_okt = []
for i in list_prep_comment:
    b = okt.morphs(i) # morphs: 형태소 추출
    list_okt.append(b) # 추출된 형태소를 list에 추가
#%%
print(list_kkma)
#%%
# 유사도 측정
from sklearn.feature_extraction.text import TfidfVectorizer
# TF-IDF는 가중치를 구하는 알고리즘 -> 단어 발생 빈도인 TF에서, 전체 발생 횟수에 따른 패널티를 부여해준 개념이 바로 TF-IDF
# 예를 들어 1.문서간의 비슷한 정도, 2.문서 내 단어들에 척도를 계산하여 핵심어를 추출
# TF는 간단하게 말해서 문서 내 특정 단어의 빈도를 말합니다.
# DF는 해당 단어가 나타난 문서의 수
# IDF는 DF값에 역수
# 특정 단어 T가 모든 문서에 등장하는 흔한 단어라면 TF-IDF 가중치는 낮춰줍니다.
tfidf_vectorizer = TfidfVectorizer(min_df=1) # min_df: 최소값 min_df = 2인 경우 빈도가 1번인 단어는 제외

label_kkma = []
for i in list_kkma:
    a=[]
    a.append(' '.join(i)) # 분리된 형태소를 문자열로 바인딩 후 리스트에 추가
    a.append(' '.join(positive)) # 유사도 측정을 위해 긍정 단어 리스트를 형태소 리스트에 추가 
    a.append(' '.join(negative)) # 유사도 측정을 위해 부정 단어 리스트를 형태소 리스트에 추가 
    
    # Bag of Words란 단어들의 순서는 전혀 고려하지 않고, 단어들의 출현 빈도(frequency)에만 집중하는 텍스트 데이터의 수치화 표현 방법입니다.
    # 벡터화: 행렬을 N by 1 형태로 변환 -> 특징을 수치화 하여 계산을 빠르게 하기 위해서
    tfidf_matrix_twitter = tfidf_vectorizer.fit_transform(a) # 문장 내 단어들을 tf-idf 값으로 가중치를 설정하여 BOW 벡터를 만든다.
    
    # TF-IDF행렬과 TF-IDF 전치행렬을 곱하면 유사도를 구할수 있습니다.
    # 행렬의 곱에서 나온 유사도는 cosine_similarity 함수의 결과값과 같다.
    document_distance = (tfidf_matrix_twitter * tfidf_matrix_twitter.T) # 전치행렬을 곱하여 유사도 계산
    if document_distance.toarray()[0][1] > document_distance.toarray()[0][2]:
        label_kkma.append('1')
    elif document_distance.toarray()[0][1] < document_distance.toarray()[0][2]:
        label_kkma.append('-1')
    else:
        label_kkma.append('0')

label_komoran = []
for i in list_komoran:
    a=[]
    a.append(' '.join(i))
    a.append(' '.join(positive))
    a.append(' '.join(negative))
    tfidf_matrix_twitter = tfidf_vectorizer.fit_transform(a)
    document_distance = (tfidf_matrix_twitter * tfidf_matrix_twitter.T)
    if document_distance.toarray()[0][1] > document_distance.toarray()[0][2]: # 댓글이 긍정단어와 유사도가 큰 경우
        label_komoran.append('1') # 1 = 긍정
    elif document_distance.toarray()[0][1] < document_distance.toarray()[0][2]: # 댓글이 부정단어와 유사도가 큰 경우
        label_komoran.append('-1') # 2 = 부정
    else:
        label_komoran.append('0')
        
label_okt = []
for i in list_okt:
    a=[]
    a.append(' '.join(i))
    a.append(' '.join(positive))
    a.append(' '.join(negative))
    tfidf_matrix_twitter = tfidf_vectorizer.fit_transform(a)
    document_distance = (tfidf_matrix_twitter * tfidf_matrix_twitter.T)
    if document_distance.toarray()[0][1] > document_distance.toarray()[0][2]:
        label_okt.append('1')
    elif document_distance.toarray()[0][1] < document_distance.toarray()[0][2]:
        label_okt.append('-1')
    else:
        label_okt.append('0')
        
#%%
df_comment_result = pd.DataFrame(list_prep_comment, columns=["prep comment"])

df_comment_result['kkma label'] = label_kkma
df_comment_result['komoran label'] = label_komoran
df_comment_result['okt label'] = label_okt














#%%
for idx in range(len(df_read_comment)):
    
    comment_data = df_read_comment.iloc[idx]['mining comment']
    
    for i in range(len(posneg)): 
        posflag = False 
        negflag = False 
        if i < (len(positive)-1): 
            # print(title_data.find(posneg[i])) 
            if comment_data.find(posneg[i]) != -1: 
                posflag = True 
                print(i, "positive?","테스트 : ", comment_data.find(posneg[i]),"비교단어 : ", posneg[i], "인덱스 : ", i, comment_data) 
                break 
            
        if i > (len(positive)-2): 
            if comment_data.find(posneg[i]) != -1: 
                negflag = True 
                print(i, "negative?","테스트 : ",comment_data.find(posneg[i]),"비교단어 : ", posneg[i], "인덱스 : ", i, comment_data) 
                break 
        
        if posflag == True: 
            df_read_comment['label'].iloc[idx] = 1 
            # print("positive", j) 
        elif negflag == True: 
            df_read_comment['label'].iloc[idx] = -1 
            # print("negative", j) 
        elif negflag == False and posflag == False: 
            df_read_comment['label'].iloc[idx] = 0 
            # print("objective", j)





#%%
from konlpy.tag import Okt
from collections import Counter

str_test = '너무 감사합니다'
str_test.find('감사')

okt = Okt()
o_noun = okt.nouns(str_test)
o_morphs = okt.morphs(str_test)

print(okt.pos(str_test, norm = True, stem = True))























































