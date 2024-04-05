import pandas as pd
import matplotlib.pyplot as plt

#from musixmatch import Musixmatch
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from lyricsgenius import Genius
import numpy as np


import math
import re

from deep_translator import GoogleTranslator
from lingua import Language, LanguageDetectorBuilder

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from kneed import KneeLocator
import json

with open('creditentials_all.json') as credits_file:
    creditential = json.load(credits_file)

GENIUS_API_KEY = creditential["GENIUS_API_KEY"]

emotions_name_angle = {
    "activation" : 0.0,
    "alert" : 18.0,
    "excited" : 36.0,
    "elated" : 54.0,
    "happy" : 72.0,
    "pleasant" : 90.0,
    "contented" : 108.0,
    "serene" : 126.0,
    "relaxed" : 144.0,
    "calm" : 162.0,
    "dactivation/sleepy" : 180.0,
    "bored" : 198.0,
    "lethargic" : 216.0,
    "depressed" : 234.0,
    "sad" : 252.0,
    "unpleasant" : 270.0,
    "upset" : 288.0,
    "stressed" : 306.0,
    "nervous" : 324.0,
    "tense" : 342.0,
}


emotions_stats = {
    "activation" : [],
    "alert" : [],
    "excited" : [],
    "elated" : [],
    "happy" : [],
    "pleasant" : [],
    "contented" : [],
    "serene" : [],
    "relaxed" : [],
    "calm" : [],
    "dactivation/sleepy" : [],
    "bored" : [],
    "lethargic" : [],
    "depressed" : [],
    "sad" : [],
    "unpleasant" : [],
    "upset" : [],
    "stressed" : [],
    "nervous" : [],
    "tense" : [],
}

def build_anothers_title(title):
        #change Pt two => Pt 2 and inverse
        list_titles = [title]
        dic = {
            "10": "ten",
            "0": "zero",
            "1": "one",
            "2": "two",
            "3": "three",
            "4": "four",
            "5": "five",
            "6": "six",
            "7": "seven",
            "8": "eight",
            "9": "nine",
        }

        reg_part = re.compile("\s+pt\W*\d+$|\s+part\W*\d+$",flags=re.IGNORECASE)
        res = re.search(reg_part, title)

        if res != None: #CASE if it's pt 2 => pt two
            start = res.start()
            end = res.end()

            clean_tile_to = title[start:end].lower()
            #add space
            for key, value in dic.items():
                clean_tile_to = clean_tile_to.replace(key, " "+key)
            list_titles.append(title[:start]+clean_tile_to)

        else:
            reg_expression = "|".join([f"\W+pt\W+{value}$|\W+part\W+{value}$" for key, value in dic.items()])

            reg_part = re.compile(reg_expression,flags=re.IGNORECASE)
            res = re.search(reg_part, title)

            if res != None: #CASE if it's pt two => pt 2
                start = res.start()
                end = res.end()
                clean_tile_to = title[start:end].lower()
                for key, value in dic.items():
                    clean_tile_to = clean_tile_to.replace(value, " "+key)
                list_titles.append(title[:start]+clean_tile_to)

        return list_titles

def get_emo_fromValEner(valence,energy):
    pt_udt = [valence,energy]
    pt_udt = create_vector(pt_udt,[0.5,0.5])
    pred_angle_upd = angle_between_vectors(pt_udt)
    emo = closest_value(emotions_name_angle,pred_angle_upd)[0]
    return emo

def angle_between_vectors(v2):
  """
  Calculates the angle between two vectors in degrees (0-360).

  Args:
      v1: A numpy array representing the first vector.
      v2: A numpy array representing the second vector.

  Returns:
      The angle between the two vectors in degrees (0-360).
  """
  v1 = [0,1]
  # Calculate the dot product
  dot_product = np.dot(v1, v2)

  # Calculate the magnitudes
  magnitude1 = np.linalg.norm(v1)
  magnitude2 = np.linalg.norm(v2)

  # Check for zero vectors (division by zero)
  if magnitude1 == 0 or magnitude2 == 0:
    return 0

  # Use arctan2 to handle angles in all quadrants
  angle_rad = np.arctan2(v1[1], v1[0]) - np.arctan2(v2[1], v2[0])

  # Convert to degrees and ensure the angle is between 0 and 360
  angle_deg = np.degrees(angle_rad) % 360.0

  return angle_deg

def circle_points(r, n):
    circles = []
    for r, n in zip(r, n):
        t = np.linspace(0, 2 * np.pi, n, endpoint=False)
        x = r * np.sin(t) + 0.5
        y = r * np.cos(t) + 0.5
        circles.append(np.c_[x, y])
    return circles

def closest_value(data,value):
    min_ecart = 999999999
    best_angle = -1
    best_emo = ""
    for emo,angle in data.items(): #ameliorable
        if abs(angle-value) < min_ecart:
            min_ecart = abs(angle-value)
            best_angle = angle
            best_emo = emo
    return best_emo,best_angle

def create_vector(point,origin):
    return([point[0] - origin[0], point[1] - origin[1]])


def get_lyrics_info(title : str, artist : str, genius : Genius, sentiment : SentimentIntensityAnalyzer = None, detector : LanguageDetectorBuilder=None, translator : GoogleTranslator=None):
    print(f"get lyrics info from {title} by {artist}")
    print("---------------------------------NEW SONG TO ANALYSE-------------------------------------------")
    clean_lyrics = None
    lang = None 
    score_lyric = 0

    titles = build_anothers_title(title)

    try:
        list_artist = artist.split(",")
        main_artist = list_artist[0]

        i = 0
        while i < len(titles):
            clean_tile = titles[i]
            song = genius.search_song(clean_tile, main_artist,get_full_info=True)
            
            if song != None:
                print(f"{clean_tile} FOUND in Genius")
                break
            i+=1

        if song == None:
            if len(list_artist) > 1:
                print("try to find another version by swapping")
                main_artist = list_artist[1] #all romanized song by this author
                song = genius.search_song(title, main_artist,get_full_info=True)

                if song == None:
                    print("try to find with all artists version")
                    song = genius.search_song(title, artist,get_full_info=False)

                if song == None:
                    print("try to find romanized version")
                    featuring = " ".join([art for art in list_artist[1:]])
                    title +=f" feat {featuring} romanized"
                    main_artist = "Genius Romanizations" #all romanized song by this author
                    song = genius.search_song(title, main_artist,get_full_info=True)
        
        
        if song == None:
            print("Artists , Title (romanized also) not found in Genius")
            return {"lyrics" : clean_lyrics, "lang": lang, "score_lyrics" : score_lyric}

        song = song.to_dict()
        lyrics = song["lyrics"]
        remove_emb = re.compile("\d*Embed$")
        lyrics_clean = re.sub(remove_emb,"",lyrics)
        clean_lyrics = "\n".join(lyrics_clean.split("\n")[1:])
        output_info = {"lyrics" : clean_lyrics}
        
        if detector is not None:
            language = detector.detect_language_of(clean_lyrics)

            lang = language.name

            if language.name != "ENGLISH":
                translator.source = language.name

                if translator is not None:
                    clean_lyrics = translator.translate(clean_lyrics)

        if sentiment:
            sentiment_score = sentiment.polarity_scores(clean_lyrics)
            valence_lyric = (sentiment_score['compound'] + 1)/2
            score_lyric = valence_lyric

        output_info["lang"] = lang
        output_info["score_lyrics"] = score_lyric
        return output_info
    
    except Exception as error:
        print(error)
        print("Not found on Genius")
        return {"lyrics" : clean_lyrics, "lang": lang, "score_lyrics" : score_lyric}

def compute_emo_rusell(df : pd.DataFrame, with_lyrics : bool = False):
    print("compute emotions")

    genius = None
    analyser = None
    translator = None
    detector = None

    if with_lyrics:
        genius = Genius(GENIUS_API_KEY, skip_non_songs=False, excluded_terms=["(Remix)", "(Live)"], remove_section_headers=True)

        analyser = SentimentIntensityAnalyzer()

        translator = GoogleTranslator(source='auto', target='en')
        detector = LanguageDetectorBuilder.from_all_languages().with_low_accuracy_mode().build()
    

    for ind in df.index:
        #print("---------------------------------NEW SONG TO ANALYSE-------------------------------------------")
        valence = df.loc[ind,"valence"]
        energy = df.loc[ind,"energy"]
        valence_upd = valence
        title, artist = df.loc[ind,"title"], df.loc[ind,"artist"]

        if with_lyrics:
            info_lyrics = get_lyrics_info(title, artist, genius, analyser, detector, translator)
        
            df.loc[ind,"lyrics"] = info_lyrics["lyrics"]
            
            df.loc[ind,"lang"] = info_lyrics["lang"]

            df.loc[ind, "score_lyrics"] = info_lyrics["score_lyrics"]

            if info_lyrics["score_lyrics"] == 0.0:
                print("Undectect language")
                print("Don't using lyric valance")
            else:
                valence_upd = (valence + info_lyrics["score_lyrics"]) / 2 # [0,2]to [0,1]
                df.loc[ind,"valence"] = valence_upd

        emo = get_emo_fromValEner(valence_upd,energy)
        df.loc[ind, "emo_russel"] = emo
    
    return df



def build_data(df,):
    return df.drop(columns=[ "artist",
        "title",
        "popularity",
        "track_id",
        "downloaded",
        "video_id",
        "transfer",
        "proccessed",
        "lyrics",
        "lang",
        "emo_russell", #delete
        "emo_russel",
        "energy","danceability"])

def compute_kmeans(df):
    print("compute emotions")

    nrj_danciab = (df.loc[:,"energy"] + df.loc[:,"danceability"])/2
    df["nrj_danc"] = nrj_danciab
    features = df.drop(columns=["energy","danceability"])
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features)
    
    kmeans_kwargs = {
        "init": "random",
        "n_init": 10,
        "max_iter": 300,
        "random_state": 42,
        }

    # A list holds the SSE values for each k
    sse = []
    for k in range(1, 11):
        kmeans = KMeans(n_clusters=k, **kmeans_kwargs)
        kmeans.fit(scaled_features)
        sse.append(kmeans.inertia_)
    
    kl = KneeLocator(
            range(1, 11), sse, curve="convex", direction="decreasing"
        )

    opti_cluster = kl.elbow
    print(opti_cluster)

    kmeans = KMeans(n_clusters=opti_cluster, **kmeans_kwargs)
    val = kmeans.fit_predict(scaled_features)
    
    pca = PCA(n_components=2)
    data = pca.fit_transform(scaled_features)
    #uniq = np.unique(val)

    return data, val

if __name__ == "__main__":
    compute_emo_rusell()