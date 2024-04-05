import streamlit as st
import pandas as pd
import numpy as np

import requests

from io import StringIO
#from emotion_api import plot_example_emo
from utils.help_plots import plot_example_emo

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

def get_lyrics(ind,ctx,df):
    if "lyrics" in df.columns:
        artist = df.loc[ind,"artist"].split(",")

        if len(artist) > 2:
            artist = ", ".join(artist[:2])+ "..."
        else:
            artist = ", ".join(artist)

        title = df.loc[ind,"title"]
        ctx.header(f'Lyrics : {title} by {artist}')
        ct_lyrics =  ctx.container(height=820)
        lyrics = ["No Lyrics found with Genius API or Instrumental music"]
        if type(df.loc[ind,"lyrics"]) == str:
            lyrics = df.loc[ind,"lyrics"].split("\n")

        for lg in lyrics:
            ct_lyrics.write(lg)
    else:
        ctx.write("Activate lyrics if you want to get them")

def issue_spo_api(e):
    print(e)
    print("needs to connect to spotify")

def concact_df(df,df2):
    column_names = df2.columns
    for col_name in column_names:
        df[col_name] = df2.loc[:,col_name]
    return df

def make_button_table(shape_column,fields, df,ctx,ctx_l):
    # # Show user table 
    assert len(shape_column) == len(fields)+1
    colms = ctx.columns(shape_column)

    for col, field_name in zip(colms, fields):
        # header
        col.text(field_name)

    for ind in df.index:
        cols = ctx.columns(shape_column)
        for col,name in zip(cols,fields):
            curr_val = df.loc[ind,name]
            if type(curr_val) == np.float64:
                curr_val = curr_val.round(2)
            col.write(curr_val)

        #disable_status = user_table['disabled'][x]  # flexible type of button
        #button_type = "Unblock" if disable_status else "Block"
        button_phold = cols[-1].empty()  # create a placeholder
        
        do_action = button_phold.button("lyrics", key=f'key_btn_table{ind}')
        if do_action:
            #button_phold.empty()  #  remove button
            get_lyrics(ind,ctx_l,df)
            fig = plot_example_emo(ind,df)
            st.session_state["fig_exp"] = fig

        
def compute_russel():
    print("processed get russel emo")
    
    try:
        if st.session_state["emo_rusel"][0] is None or st.session_state["emo_rusel"][1] != st.session_state["ckbx_wl"]:
            dt_f = st.session_state["data"]
            ids = dt_f.loc[:,["artist","title","valence", "energy"]].to_json()
            data_send = {"df":ids, "wl" : st.session_state["ckbx_wl"]}
            res = requests.request(method="get",url=BASE_URL_FLASKAPI+"get_russel_emo", json=data_send)
            res = res.json()
            ret_df = pd.read_json(StringIO(res))
            st.session_state["emo_rusel"] = (ret_df,st.session_state["ckbx_wl"])
            concact_df(st.session_state["data"],st.session_state["emo_rusel"][0])
        
        exp_idx = 0
        fig = plot_example_emo(exp_idx,st.session_state["emo_rusel"][0])
        st.session_state["fig_exp"] = fig
        
    except Exception as e:
        issue_spo_api(e)

def main():
    
    st.set_page_config(layout="wide")
   
    if "connect" not in st.session_state:
        st.session_state.connect = False

    if "fig_exp" not in st.session_state:
        st.session_state["fig_exp"] = None
    
    if "wLyric" not in st.session_state:
        st.session_state["wLyric"] = None

    if "data" not in st.session_state:
        st.session_state["data"] = None
    
    if "emo_rusel" not in st.session_state:
        st.session_state["emo_rusel"] = (None,False)
    
    from_csv = st.session_state.get("from_csv", False)
    st.title('SpoToSave')
    
    col1, col2 = st.columns([0.7,0.3],gap="large")
    
    col1.header(f'Emotion compute via Circumflex of Russel',divider='rainbow')
    print(from_csv)
    if st.session_state["data"] is not None and st.session_state["connect"] and not from_csv:
        ctx_btn = col1.container()
        colbtn1, colbtn2, colbtn3 = ctx_btn.columns([1,1,4])
        if colbtn1.button("compute_russel"):
            with st.spinner('Wait for it...'):
                compute_russel()
            st.toast("Compute Russell done!")

        colbtn2.checkbox("With lyrics",key="ckbx_wl")

        if st.session_state["emo_rusel"][0] is not None:
            fields = list(st.session_state["emo_rusel"][0].columns)

            if "lyrics" in fields:
                fields.remove("lyrics")

            if st.session_state["emo_rusel"][1]:
                shape_column = [2,2,1,1,1,1,1,1]
            else:
                shape_column = [2,2,1,1,1,1]
            ctx = col1.container(border=True,height=500)
            make_button_table(shape_column,fields, st.session_state["emo_rusel"][0],ctx,col2)
        
        if st.session_state["fig_exp"] is not None:
            col11, col21,col31 = col1.columns([1,3,1],gap="small") 
            col21.pyplot(st.session_state["fig_exp"])
    
    elif st.session_state["data"] is not None and from_csv:
        print("csv")
        fields = ["artist", "title", "valence", "energy", "emo_russel"]
        csv_column = st.session_state["data"].columns
        if "lang" in csv_column and "score_lyrics" in csv_column:
            fields.append("lang")
            fields.append("score_lyrics")
            shape_column = [2,2,1,1,1,1,1,1]
        else:
            shape_column = [2,2,1,1,1,1]
        ctx = col1.container(border=True,height=500)
        make_button_table(shape_column,fields, st.session_state["data"],ctx,col2)
        
        if st.session_state["fig_exp"] is not None:
            col11, col21,col31 = col1.columns([1,3,1],gap="small") 
            col21.pyplot(st.session_state["fig_exp"])
    else:
        st.write("Need to be connected to spotify")

if __name__ == "__main__":
    main()