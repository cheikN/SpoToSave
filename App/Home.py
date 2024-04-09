import pandas as pd
import numpy as np
import streamlit as st
import requests

BASE_URL_FLASKAPI = "http://127.0.0.1:5000/"


def issue_spo_api(e):
    print(e)
    print("needs to connect to spotify")


def get_name():
    print("processed get [username]")
    try:
        res = requests.request(method="get",url=BASE_URL_FLASKAPI+"get_username")
        res = res.json()
        st.session_state["username"] = res["display_name"]
        
    except Exception as e:
        issue_spo_api(e)


def main():
    
    st.set_page_config(layout="wide")
    st.title('SpoToSave')

    if "data" not in st.session_state:
        st.session_state["data"] = None

    if "from_csv" not in st.session_state:
        st.session_state["from_csv"] = False

    res = requests.request(method="get",url=BASE_URL_FLASKAPI)
    res = res.json()
    ulr_auth_spot = res["message"]["body"]["spot_url"]
    st.session_state["auth_link"] = ulr_auth_spot
    st.session_state["connect"] = res["message"]["body"]["token_available"]
    
    url_link = st.session_state.get("auth_link","/")


    if not st.session_state["connect"]:
        st.session_state["connect"] = int(st.query_params.get("con",0))

    if not st.session_state["connect"]:
        cols = st.columns([1,5,1])
        intro_text = str("""Welcome to SpoToSave, your one-stop destination for exploring the emotional landscapes of your favorite Spotify songs! Are you curious about the intricate emotions that music evokes within you? Look no further. Our platform specializes in collecting and analyzing data from the songs you love on Spotify, providing you with insightful visualizations and interpretations.
\nAt SpoToSave, we go beyond merely listing your top tracks. We delve deep into the emotional essence of each song, utilizing the Circumplex Model of Emotion developed by psychologist James A. Russell. Through this model, we dissect the complex interplay of emotions embedded within the music you cherish, offering a unique perspective on how it impacts your mood and perception.
\nOur intuitive interface allows you to seamlessly navigate through your Spotify library, exploring the emotional journey each song undertakes. Whether it's the exhilarating highs of a dance anthem or the introspective depths of a soulful ballad, we're here to unravel the emotional tapestry woven by your musical preferences.
\nJoin us on a journey of discovery as we decode the emotional nuances of your Spotify playlist. SpoToSave is where data meets emotion, transforming your listening experience into a captivating exploration of the human psyche through music.""")
        cols[1].write(intro_text)
        #cols[1].link_button("Connect to spotify",url=url_link,)
        cols11 = cols[1].columns([1,1])
        cols11[0].markdown(f'<a href="{url_link}" target="_self"><button style="background-color:black; inline-size: -moz-available;">Connect to spotify</button></a>',unsafe_allow_html=True)
        up_file = cols11[1].file_uploader("Import data (csv file)")
        if up_file is not None:
            dataframe = pd.read_csv(up_file)
            st.session_state["data"] = dataframe
            st.session_state["from_csv"] = True
            st.toast('Data collected!', icon='🎉',)
    else:
        if "username" not in st.session_state and st.session_state["data"] is None:
            get_name()
            st.session_state["from_csv"] = False
            st.toast('Connected to Spotify!', icon='🎉')
        st.write("Welcome "+st.session_state.get("username", ""))
        up_file = st.file_uploader("Import data (csv file)")
        if up_file is not None:
            dataframe = pd.read_csv(up_file)
            st.session_state["data"] = dataframe
            st.session_state["from_csv"] = True
            st.toast('Data collected!', icon='🎉',)
        #st.switch_page("pages/Data.py")

    
    

if __name__ == "__main__":
    main()