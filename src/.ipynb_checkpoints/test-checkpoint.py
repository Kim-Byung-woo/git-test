# -*- coding: utf-8 -*-
"""
Created on Fri Apr  2 15:32:25 2021

@author: Admin
"""

import pandas as pd
df = pd.read_pickle('siteA_weekly_data_20191118_20191124.pickle')

#%%




df['category_depth3'] = df.apply(lambda x: x['category'].split(' > ')[2], axis = 1)
list_depth3 = df['category_depth3'].unique()

df_res = df[df['category_depth3'] == list_depth3[0]]

import matplotlib.pyplot as plt


plt.rc('font', size = 20, family='gulim')
fig, ax0 = plt.subplots(figsize=(25, 10))


ax0.set_title("카테고리별 판매수량")
str_label = f'{list_depth3[0]}'
ax0.plot(df_res['sold_day'],df_res['sell_amount'], 'r-', label= str_label)

ax0.set_ylabel("sell_amount")
ax0.grid(False)
ax0.legend(loc = 1)