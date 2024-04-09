# SpoToSave
## Description
It is project where you can get info (features,lyrics, emotion) about your liked song from Spotify. It based on Flask (API part) and streamlit for the frontend.
Contains:
- **Data**: Get data info : title, artist, features song (ernergy, valence...) and also a Top 5 artists.
- **Emotion**: Compute emotion from the **Circumplex model of emotion (Russell)**. With only valence and energy from song it is not perfect.
For example, a song can be happy but the lyrics are not. That's why it is important to also compute the valence of lyrics and add to valence of the song.
Even with that, this method is limited.
- **Similarity**: Compute Kmeans with the features of song (danceability, energy, instrumentalness, key, liveness, loudness, mode, speechiness, tempo, valence) (herfe for more details : https://developer.spotify.com/documentation/web-api/reference/get-audio-features)
From the output of kmeans, you can create playlist. It will be named (Cluster_0 etc)
- **GameLyrics**: Try to find where the lyrics come from (tiitle, artist)
- **Download**: With the help of pytube, it donwload all your liked song. It takes times. It better to use the script *csv_to_download.py*

## Prerequisites
Needs to have Spotify API key and Genius API key.
Add api keys in a file .json or you can put them in your os environnement.
In my case, it like thise : 
```json
{
    "spotify" :{
        "client_id" : "your key",
        "client_secret" : "your key"
    },
    "GENIUS_API_KEY" : "your key"
}
```
This project use Flask, streamlit, spotipy, pytube, lyricsgenius, vaderSentiment, deep_translator, lingua
