import os

from flask import Flask, session, url_for, request, redirect, jsonify, Response
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import MemoryCacheHandler

import pandas as pd
import re, json
from emotion_api import compute_emo_rusell, compute_kmeans
from io import StringIO

BASE_URL_STRMLIT = "http://192.168.1.132:8501"

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

with open('creditentials_all.json') as credits_file:
    creditential = json.load(credits_file)

client_id = creditential["spotify"]["client_id"]
client_secret = creditential["spotify"]["client_secret"]
redirect_uri ='http://localhost:5000/callback'
scope = 'user-library-read,playlist-modify-private,playlist-read-private, playlist-read-collaborative'

cache_handler = MemoryCacheHandler()

sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True,
    open_browser=True
)

sp = None


def get_all_artists(artists):
    separator = ", "
    all_artists = separator.join([art['name'] for art in artists])
    return all_artists

def clean_title(title,artists):
    list_artists = artists.split(",")
    reg_add_artist = "".join([f"|\W*\s*with {artist.strip()}\s*|\s*{artist.strip()}\s*" for artist in list_artists[1:]])
    reg_title = re.compile("\W*\s*ft[\.\s+]|\W*\s*feat[\.\s+]"+reg_add_artist,flags=re.IGNORECASE)
    clean_tile = re.split(reg_title,title)
    clean_tile = list(filter(None, clean_tile))[0] #remove empty (stress) => ['',stress,''] => [stress]
    return clean_tile

def merge(list1, list2):
 
    merged_list = [(list1[i], list2[i]) for i in range(0, len(list1))]
     
    return merged_list

def check_token():
    #Token valid? 
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        #return redirect(auth_url)
        return auth_url
    return "/"

@app.route('/')
def home():
    url = check_token()
    #return redirect("http://localhost:8501")
    #return redirect(url_for("get_liked"))
    token_available = url == "/"
    return jsonify({"message" : {"body" : {"spot_url": url, "token_available":token_available}}, "code" : 202})

@app.route('/callback')
def callback():
    print("call back")
    print(request)
    
    ret = sp_oauth.get_access_token(request.args['code'])
    #return jsonify({"message" : "Connecté à spotify!", "code" : 201})
    ret = jsonify(ret)
    ret.status_code = 200
    #resp = Response(response=json.dumps(ret), status=200,  mimetype="text/plain")
    return redirect(BASE_URL_STRMLIT+"?con=1", code=302)

@app.route('/get_username')
def get_username():
    print("get_username")
    ret = sp_oauth.cache_handler.get_cached_token()
    sp = Spotify(auth=ret["access_token"])
    cur_user = sp.current_user()
    print(cur_user)
    ret = jsonify(cur_user)
    return ret

@app.route('/get_top_artist')
def get_top_artist():
    print("get_top_artist")
    ret = sp_oauth.cache_handler.get_cached_token()
    sp = Spotify(auth=ret["access_token"])

    ids = request.json['ids']
    list_arts = []
    print(ids)
    for id in ids:
        tmp_ar = sp.artist(id)
        data_art = {
            "name" : tmp_ar["name"],
            "genre" : tmp_ar["genres"],
            "popularity" : tmp_ar["popularity"],
            "image" : tmp_ar["images"], #list of 3 size of image
        }
        list_arts.append(data_art)
    ret = jsonify(list_arts)
    return ret

@app.route("/get_liked")
def get_liked():
    
    #check_token()
    ret = sp_oauth.cache_handler.get_cached_token()
    sp = Spotify(auth=ret["access_token"])

    all_ret = False
    cur_off  = 0
    infos = "<br>"
    step = 0
    
    data = {
        "artist" : [],
        "title": [],
        "popularity" : [],
        "danceability" : [],
        "energy" : [],
        "key" : [],
        "loudness" : [],
        "mode" : [],
        "speechiness" : [],
        "acousticness" : [],
        "instrumentalness" : [],
        "liveness" : [],
        "valence" : [],
        "tempo" : [],
        "track_id" : [],
        "artist_id" : []
    }

    """data = {
        "artist" : [],
        "title": [],
        "popularity" : [],
        "track_id" : [],
        "artist_id" : []
    }"""
    
    
    try:
        df_liked = pd.read_csv("liked_features_.csv",sep = '\t')
        titles = list(df_liked.loc[:,"title"])
        artists = list(df_liked.loc[:,"artist"])
        #title_art = merge(titles,artists)
        id_tracks = list(df_liked.loc[:,"track_id"])
        print("CSV Found, Updating data")
    except FileNotFoundError:
        titles = []
        artists = []
        title_art = []
        id_tracks = []
        print("CSV not Found, creating csv data")

    #retrieve all songs (limit max is 50)
    while not all_ret:
        print("start retrieve")
        liked_song = sp.current_user_saved_tracks(limit=50, offset=cur_off)
        
        for idx, item in enumerate(liked_song['items']):
            print("NEXT MUSIQUE")
            
            track = item['track']

            title = track['name']

            #artist = track['artists'][0]['name']
            #tmp_ar = sp.artist(track['artists'][0]["id"])
            artists = get_all_artists(track['artists'])

            title = clean_title(title,artists)


            #tit_art = (title,artist)

            id_t = item['track']['id']
            #for pandas
            if id_t not in id_tracks:
                print(f"ADD new liked songs {title} from {artists}")
                #titles.append(title)
                #artists.append(artist)
                data["title"].append(title)
                data["artist"].append(artists)
                data["popularity"].append(item['track']["popularity"])
                data["track_id"].append(id_t)
                data["artist_id"].append(track['artists'][0]["id"])

                try:
                    features_track = sp.audio_features(id_t)[0]

                    data["danceability"].append(features_track["danceability"])
                    data["energy"].append(features_track["energy"])
                    data["key"].append(features_track["key"])
                    data["loudness"].append(features_track["loudness"])
                    data["mode"].append(features_track["mode"])
                    data["speechiness"].append(features_track["speechiness"])
                    data["acousticness"].append(features_track["acousticness"])
                    data["instrumentalness"].append(features_track["instrumentalness"])
                    data["liveness"].append(features_track["liveness"])
                    data["valence"].append(features_track["valence"])
                    data["tempo"].append(features_track["tempo"])
                    

                except:
                    #max retries issues
                    data["danceability"].append(None)
                    data["energy"].append(None)
                    data["key"].append(None)
                    data["loudness"].append(None)
                    data["mode"].append(None)
                    data["speechiness"].append(None)
                    data["acousticness"].append(None)
                    data["instrumentalness"].append(None)
                    data["liveness"].append(None)
                    data["valence"].append(None)
                    data["tempo"].append(None)
        
        nb = len(liked_song['items'])
        
        if nb < 50:
            all_ret = True
        else:
            step += 1
            cur_off = 50 * step

    nb_tracks = len(data["track_id"])
    """data.update({
        "downloaded" : [False for i in range(nb_tracks)],
        "video_id" : ["" for i in range(nb_tracks)],
        "transfer" : [False for i in range(nb_tracks)], #transfer to youtube
        "proccessed" : [False for i in range(nb_tracks)], #proccessed songs
        "score_lyrics" : [0 for i in range(nb_tracks)],
        "lyrics" : ["" for i in range(nb_tracks)],
        "lang" : ["" for i in range(nb_tracks)],
        "emo_russel" : ["" for i in range(nb_tracks)]
    })"""
    df_liked  = pd.DataFrame(data)
    #df_liked.to_csv('liked_features.csv', sep = '\t', index=False)
    df_liked = df_liked.to_json(orient="records")
    #ret = jsonify(df_liked,status=200, mimetype='application/json')
    #ret.status_code = 200
    #return redirect("http://192.168.1.132:8501")
    ret = Response(df_liked, mimetype='application/json')
    #return redirect(BASE_URL_STRMLIT, code=302,Response=ret)

    #print(sp.current_user_playlists())
    return ret


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/get_russel_emo")
def get_russel_emo():
    print("get_russel_emo")
    wl = request.json['wl']
    df = request.json['df']
    df = pd.read_json(StringIO(df))
    df_emo = compute_emo_rusell(df,wl)
    df_emo = df_emo.to_json()
    ret = jsonify(df_emo)
    return ret

@app.route("/get_kmeans_emo")
def get_kmeans_emo():
    print("get_kmeans_emo")
    df = request.json['df']
    df = pd.read_json(StringIO(df))
    data_pca, val_kmeans = compute_kmeans(df)
    pdt_rt = pd.DataFrame(data_pca)
    pdt_rt["label"] = val_kmeans
    pdt_rt = pd.DataFrame(pdt_rt).to_json()
    ret = jsonify(pdt_rt)
    return ret

@app.route("/create_playlist", methods=["PUT"])
def create_playlist():
    #infos = request.json['infos']
    track_ids = request.json["track_ids"]
    playlist_name = request.json["playlist_name"]
    playlist_description = request.json["playlist_description"]

    ret = sp_oauth.cache_handler.get_cached_token()
    sp = Spotify(auth=ret["access_token"])

    user_id = sp.me()['id']
    playlists = sp.user_playlists(user_id)["items"]

    for pl in playlists:
        name = pl["name"]
        if name == playlist_name:
            ret = {"code" : 403, "link":pl["external_urls"]["spotify"]}
            return ret

    ret = sp.user_playlist_create(user_id, playlist_name, public=False,description = playlist_description)
    id_playlist = ret["id"]
    sp.playlist_add_items(playlist_id=id_playlist, items=track_ids)
    return {"code" : 203,"link":ret["external_urls"]["spotify"]}

if __name__ == "__main__":
    app.run(debug=False)