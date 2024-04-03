import streamlit as st
import pandas as pd
import numpy as np

import requests


import matplotlib.pyplot as plt

from matplotlib import colors as mcolors
from utils.help_plots import plot_radar

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

def issue_spo_api(e):
    print(e)
    print("needs to connect to spotify")

def get_features_name():
    list_ft = ["danceability",
                "energy",
                "key",
                "loudness",
                "mode",
                "speechiness",
                "acousticness",
                "instrumentalness",
                "liveness",
                "valence",
                "tempo"]
    return list_ft

def transfrom_toList(arr):
    list_trs = []
    for v in arr:
        list_trs.append(v[0])
    return np.array(list_trs)

def label_toColor(labels,colors):
    list_colors = []
    color_names = list(colors.keys())
    for l in labels:
        cname = color_names[l*5]
        list_colors.append(colors[cname])
    return list_colors


def plot_kmeans():
    labels = st.session_state["kmeans_data"].loc[:,["label"]].to_numpy()
    labels = transfrom_toList(labels)

    st.session_state["kmeans_data"]["color_lab"] = label_toColor(labels,mcolors.CSS4_COLORS)

    
    st.scatter_chart(data=st.session_state["kmeans_data"],x='0',
                                y='1',
                                color="color_lab")


def create_playlist(ind,labels):
    state_btn = st.session_state.get(f'key_button_{ind}',False)
    if state_btn:
        print(f'clicked button {ind}')
        track_ids = st.session_state["data"].loc[labels == ind,"track_id"].tolist()
        infos = {
            "username" : st.session_state.get("username", ""),
            "playlist_name" : f'cn_cluster_{ind}_date',
            "playlist_description" : "generate automatically from cluster",
            "track_ids" : track_ids
        }
        try:
            print("create playlist")
            res = requests.request(method="get",url=BASE_URL_FLASKAPI+"create_playlist", json=infos)
            res = res.json()
        except Exception as e:
            issue_spo_api(e)
        

def get_info_cluster():
    labels = st.session_state["kmeans_data"].loc[:,["label"]].to_numpy()
    labels = transfrom_toList(labels)
    uniq = np.unique(labels)
    nb_cluster = len(uniq)

    columns_to_see = ["title","artist", "valence","energy", "danceability"]
    if "emo_russel" in st.session_state["data"].columns:
        columns_to_see.append("emo_russel")


    for i in range(nb_cluster):
        ctx = st.container(border=True)
        ctx.title(f':red[CLUSTER {i}]')
        col1, col2, col3 = ctx.columns([2.4,1,1],gap="medium")
        col1.write("Infos of all musics from the cluster")
        col1.dataframe(st.session_state["data"].loc[labels == i,columns_to_see],hide_index=True,use_container_width=True)

        features_names = get_features_name()
        fig, mean_df = plot_radar(labels,i,features_names)
        col2.write("Mean of all features")
        column_config= {
            "": "Feature",
            "0": ""
        }
        col2.dataframe(mean_df,hide_index=False,use_container_width=True,height=425,column_config=column_config)
        col3.write("Radar chart of the features")
        col3.pyplot(fig)
        col3.button("Create playlist",key=f'key_button_{i}',on_click=create_playlist(i,labels),use_container_width=True)


def compute_kmeans():
    print("processed get russel emo")
    
    try:
        if st.session_state["kmeans_data"] is None:
            print("go to kmeans compute")
            fts = get_features_name()
            dt_f = st.session_state["data"]
            ids = dt_f.loc[:,fts].to_json()
            data_send = {"df":ids}
            res = requests.request(method="get",url=BASE_URL_FLASKAPI+"get_kmeans_emo", json=data_send)
            res = res.json()
            ret_df = pd.read_json(StringIO(res))
            st.session_state["kmeans_data"] = ret_df

    except Exception as e:
        issue_spo_api(e)

def main():
    
    st.set_page_config(layout="wide")
   
    if "connect" not in st.session_state:
        st.session_state.connect = False

    if "data" not in st.session_state:
        st.session_state["data"] = None
    
    if "kmeans_data" not in st.session_state:
        st.session_state["kmeans_data"] = None
    
    st.title('SpoToSave')
    
    st.header(f'Similarity with kmeans',divider='rainbow')
    
    if st.session_state["data"] is not None and st.session_state["connect"]:
        if st.button("compute_kmeans"):
            compute_kmeans()

        if st.session_state["kmeans_data"] is not None:
            #plot_kmeans()
            get_info_cluster()
    else:
        st.write("Need to be connectec to spotify")

if __name__ == "__main__":
    main()