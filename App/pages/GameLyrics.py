import streamlit as st
import random as rd
import unicodedata
from difflib import SequenceMatcher
import re

MAX_ATTEMPT = 5

def clean_str(s):
    """Cleans a string to help with string comparison.

    Removes punctuation and returns
    a stripped, NFKC normalized string in lowercase.

    Args:
        s (:obj:`str`): A string.

    Returns:
        :obj:`str`: Cleaned string.

    """
    punctuation = r"""!"#$%&'()*+,-./:;<=>?@[\]^_`{|}~"""
    punctuation_ = punctuation + "’" + "\u200b"
    string = s.translate(str.maketrans('', '', punctuation_)).strip().lower()
    return unicodedata.normalize("NFKC", string)

def end_round(res, to_find, title, artist,succes=False):
    if succes:
        res.success(f'Good job! It was {title} by {artist}')
    else:
        res.error(f'You failed, the anwser was : {title} by {artist}')
    
    if "video_id" in to_find.columns:
        video_id = to_find["video_id"].values[0]
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        res.video(video_url)
    st.session_state["recap"] = []

def sumbit(title,artist,to_find,res):
    st.session_state.answer = st.session_state.get("answer_text","")
    st.session_state.answer_text = ""

    attempt = st.session_state.get("attempt",0)
    #audis_streams = st.session_state.get("audio_streams","")
    rand_ind = st.session_state.get("rand_ind", None)
    recap = st.session_state.get("recap",[])

    answer = st.session_state.get('answer', '')
    clean_answer = clean_string(answer)
    score_similarty = SequenceMatcher(None, clean_answer, st.session_state["clean_info"]).ratio()

    if score_similarty >= 0.8:
        st.session_state["found"] = True
        st.session_state["attempt"] = 0

        end_round(res,to_find,title, artist,succes=True)
        return ""
    
    elif(score_similarty > 0.6 and score_similarty < 0.8):
        res.warning("Almost, maybe missing some words...")
    
    st.session_state["found"] = False
    st.session_state["attempt"] +=1
    
    if attempt >= MAX_ATTEMPT:
        st.session_state["found"] = True
        st.session_state["attempt"] = 0

        end_round(res ,to_find, title, artist, succes=False)

        return ""

    if attempt >= MAX_ATTEMPT - 2:
        #st.audio(audis_streams[0][0], start_time=30, end_time=45)
        res.warning("Few attempts left...")
        res.text("Little recap")
        for idx, reca in enumerate(recap):
            ans = reca["answer"]
            score = reca["score"]
            res.text(f'Answer {idx+1} - {ans} with score {score:.2f}')

    recap.append({"answer" : clean_answer, "score" : score_similarty})

def get_new_lyrics(data):
    #rand_ind = rd.randint(0,len(data)-1)
    to_find = data.sample()

    lyrics = to_find["lyrics"].values[0]
    lyrics = lyrics.split("\n")
    nb_line = 4
    rand_lyric = rd.randint(0,len(lyrics)-nb_line-1)
    lyrics_to = "\n".join(lyrics[rand_lyric:rand_lyric+nb_line])

    title = to_find["title"].values[0]
    artist = to_find["artist"].values[0].split(",")[0]
    
    st.session_state["rand_ind"] = lyrics.index
    return lyrics_to, title, artist, to_find

def clean_string(info):
    punctuation = re.compile("[!#$%'()*+,.\\\/;<=>?@\[\]\^`{|}~]")
    punc2 = re.compile("[-_&]")
    clean_info = re.sub(punctuation,"",info)
    clean_info = re.sub(punc2," ",clean_info)
    clean_info = sorted(clean_info.split(" "))
    clean_info = " ".join(clean_info).lower().strip()

    return clean_info

def main():
    st.set_page_config(layout="centered")
    st.title("Do you know your liked songs ?")
    
    play_game = st.container()
    res = st.container()
    data = st.session_state.get("data",None)
    title = ""
    artist = ""
    data = data.dropna()
    if data is not None :
        if "lyrics" in data.columns:

            if "attempt" not in st.session_state:
                st.session_state["attempt"] = 0
            
            if "recap" not in st.session_state:
                st.session_state["recap"] = []

            found = st.session_state.get("found", True)

            clean_info = st.session_state.get("clean_info", "")

            lyrics_to = st.session_state.get("lyrics_to", "")

            title = st.session_state.get("title", "")
            artist = st.session_state.get("artist", "")
            to_find = st.session_state.get("to_find", None)

            if found:
                lyrics_to, title, artist, to_find = get_new_lyrics(data)
                
                st.session_state["lyrics_to"] = lyrics_to
                st.session_state["title"] = title
                st.session_state["artist"] = artist
                st.session_state["to_find"] = to_find

                clean_info = title+" "+artist
                st.session_state["clean_info"] = clean_string(clean_info)


            play_game.text(lyrics_to)

            play_game.text_input("Answer",key="answer_text", on_change=sumbit,args=(title,artist,to_find,res))

        else:
            st.write("No lyrics information in the data. Please go to Emotion page and activate lyric option when compute Russell Emotion")

    else:
        st.write("No lyrics information in the data. Please go to Emotion page and activate lyric option when compute Russell Emotion")

if __name__ == "__main__":
    main()