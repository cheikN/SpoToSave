import streamlit as st
import pandas as pd
import numpy as np

import requests

BASE_URL_FLASKAPI = "http://127.0.0.1:5000/"

def get_data(df):
    return df.drop(columns=[ 
        "track_id",
        "downloaded",
        "video_id",
        "transfer",
        "proccessed",
        "emo_russell",
        "lyrics"])

def get_lyrics(df,col):
    print("Print lyrics")
    st.session_state["tmp_data_ed"] = st.session_state["table_ed"]["edited_rows"]
    
    for key, value in st.session_state["tmp_data_ed"].items():
        if value["select"]:
            clean_lyrics = df.loc[int(key),"lyrics"].split("\n")
            if len(clean_lyrics) == 1:
                clean_lyrics = ["No lyrics"]
            artist = df.loc[int(key),"artist"]
            title = df.loc[int(key),"title"]
            col.header(f"\"{title}\" by {artist}")
            for x in clean_lyrics: 
                col.write(x)
            break

def issue_spo_api(e):
    print(e)
    print("needs to connect to spotify")


def get_liked():
    print("processed get liked")
    try:
        res = requests.request(method="get",url=BASE_URL_FLASKAPI+"get_liked")
        res = res.json()
        st.session_state["data"] = pd.DataFrame(res)
    except Exception as e:
        issue_spo_api(e)


def get_top_artist(ctx):
    print("processed get top ids")
    if st.session_state["data"] is not None :
        dt_f = st.session_state["data"]
        ids = dt_f["artist_id"].value_counts()[:5].keys().tolist()
        data_send = {"ids":ids}

        try:
            
            if st.session_state["top_art"] is None:
                res = requests.request(method="get",url=BASE_URL_FLASKAPI+"get_top_artist", json=data_send)
                res = res.json()
                st.session_state["top_art"] =  res

            for art in st.session_state["top_art"]:
                ct = ctx.container(border=True)
                col1, col2,col3 = ct.columns([1,1,20],gap="large")
                utl_image = art["image"][2]["url"]
                col1.image(utl_image,width=120)
                col3.write(f'Name : {art["name"]}')
                col3.write(f'Genre : { ", ".join(art["genre"])}')
                col3.write(f'Popularity : {art["popularity"]}')
        except Exception as e:
            issue_spo_api(e)
    else:
        ctx.write("NEED TO GET SOME DATE")

def get_stats(col):
    column_names =st.session_state["data"].columns
    mean_pop = st.session_state["data"]["popularity"].mean()
    col.write(f'Mean popularity tracks {mean_pop}')
    if "lang" in column_names:
        lang_5 = st.session_state["data"]["lang"].value_counts()[:5]
        qty_lang = lang_5.tolist()
        name_lang = lang_5.index
        lang_5 = ", ".join([f"{lg} ({qty})"for lg, qty in zip(name_lang,qty_lang)])
        col.write(f'Top 5 Language => {lang_5}')
    
    if "emo_russel" in column_names:
        emo_5 = st.session_state["data"]["emo_russel"].value_counts()[:2]
        qty_emo = emo_5.tolist()
        name_emo = emo_5.index
        emo_5 = ", ".join([f"{lg} ({qty})"for lg, qty in zip(name_emo,qty_emo)])
        col.write(f'Top 5 Emotion (Russel) => {emo_5}')

def main():
    
    st.set_page_config(layout="wide")
   
    if "connect" not in st.session_state:
        st.session_state.connect = False

    if "username" not in st.session_state:
        st.session_state["username"] = ""

    if "data" not in st.session_state:
        st.session_state["data"] = None
    
    if "top_art" not in st.session_state:
        st.session_state["top_art"] = None
    
    st.title('SpoToSave')
    
    col1, col2 = st.columns([0.7,0.3],gap="large")
    
    col1.header(f'DATA  { st.session_state["username"] }',divider='rainbow')
    
    if st.session_state["connect"] and st.session_state["data"] is None:
        if col1.button("get_liked"):
            with st.spinner('Wait for it...'):
                get_liked()
            st.success('Done!')
                

        if st.session_state["data"] is not None:
            #data_see = st.session_state["data"].loc[:,["artist", "title", "popularity"]]
            data_see = st.session_state["data"]
            col1.dataframe(data_see,hide_index=True)
            
            expand = col1.expander("TOP 5 ARTISTS",expanded=False)
            if expand:
                get_top_artist(expand)

    elif st.session_state["data"] is not None:
        col1.dataframe(st.session_state["data"],hide_index=True)
    else:
        st.write("Need to be connectec to spotify")
    
    col2.header("Statistics")
    if st.session_state["data"] is not None:
        get_stats(col2)

if __name__ == "__main__":
    main()