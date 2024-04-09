from bs4 import BeautifulSoup, Tag
import requests
import re,json
from difflib import SequenceMatcher

def clean_string(info):
    punctuation = re.compile("[!#$%'()*+,.\\\/;<=>?@\[\]\^`{|}~]")
    punc2 = re.compile("[-_&]")
    #expr_non_char = re.compile("[^a-zA-Z\s]")
    clean_info = re.sub(punctuation,"",info)
    clean_info = re.sub(punc2," ",clean_info)
    #clean_info = re.sub(expr_non_char,"",clean_info)
    clean_info = sorted(clean_info.split(" "))
    clean_info = " ".join(clean_info).lower().strip()

    return clean_info

def tmp():
    # Convert list to dictionary
        top_hits = response['sections'][0]['hits']

        # Check rest of results if top hit wasn't the search type
        sections = sorted(response['sections'],
                          key=lambda sect: sect['type'] == type_)

        hits = [hit for hit in top_hits if hit['type'] == type_]
        hits.extend([hit for section in sections
                     for hit in section['hits']
                     if hit['type'] == type_])
        best_item = None
        best_score = 0
        best_score_art = 0
        best_score_title = 0
        for hit in hits:
            item = hit['result']
            
            score_similarty_art = SequenceMatcher(None, clean_str(item['artist_names']), clean_str(artist)).ratio()
            print(item['artist_names'], artist)
            score_similarty = SequenceMatcher(None, clean_str(item[result_type]), clean_str(title)).ratio()
            print(score_similarty, score_similarty_art)
            if score_similarty_art + score_similarty  > 1.2: #same artists or close
                if score_similarty_art + score_similarty > best_score:
                    if self._result_is_lyrics(item):
                        best_score_title = score_similarty
                        best_score_art = score_similarty_art
                        best_score = best_score_art + best_score_title
                        best_item = item
                        
                        if best_score + score_similarty_art == 2.0: #get the best
                            break
            else: #name invert
                new_art = clean_str(item['artist_names']).split(" ")
                new_art.reverse()
                new_art = " ".join([art for art in new_art])
                print(f"[REVERSE ARTIST] {new_art}")
                score_similarty_art = SequenceMatcher(None, new_art, clean_str(artist)).ratio()
                if score_similarty_art + score_similarty  > 1.2: #same artists or close
                    if score_similarty_art + score_similarty > best_score:
                        if self._result_is_lyrics(item):
                            best_score_title = score_similarty
                            best_score_art = score_similarty_art
                            best_score = best_score_art + best_score_title
                            best_item = item

                            if best_score + score_similarty_art == 2.0: #get the best
                                break

            #if clean_str(item[result_type]) == clean_str(title):
            #    return item
        if best_score_art >= 0.6 and best_score_title >= 0.7:
            return best_item
        if best_score_art >= 0.9 and best_score_title >= 0.4:
            return best_item
        return None

def get_item_from_search_response(response, title, artist):

    # Convert list to dictionary
    top_hits = response['hits']
    best_item = None
    best_score = 0
    infos = title+" "+artist
    clean_infos = clean_string(infos)

    for hit in top_hits:
        item = hit['result']
        to_cmpre = item["title"]+" "+item['artist_names']
        to_cmpre = clean_string(to_cmpre)
        score_similarty = SequenceMatcher(None, to_cmpre, clean_infos).ratio()
        print(to_cmpre+ " [......] "+clean_infos+" =====> "+str(score_similarty))
        if score_similarty > best_score:
            best_score = score_similarty
            best_item = item
            
            if best_score == 1.0: #get the best
                return best_item
            
    if best_score >= 0.7:
        return best_item
    return None
def main():
    print("lyrics scrapper genius")
    with open('creditentials_all.json') as credits_file:
        creditential = json.load(credits_file)

    GENIUS_API_KEY = creditential["GENIUS_API_KEY"]
    artist_csv = "KEY, TAEYEON"
    list_artists = artist_csv.split(",")
    main_artist = " " .join(list_artists)
    print(f"Looking for the main artist {main_artist}")
    title = "Hate that…"

    search_term = title+ " "+ main_artist
    genius_search_url = f"http://api.genius.com/search?q={search_term}&access_token={GENIUS_API_KEY}"
    response = requests.get(genius_search_url)
    response = response.json()["response"]
    best_item = get_item_from_search_response(response, title, main_artist)
    #url = "https://genius.com/Kid-cudi-mr-solo-dolo-iii-lyrics"
    url = best_item["url"]
    response = requests.get(url)
    html = response.text
    #soup = BeautifulSoup(html,features="html.parser")

    new_re = re.compile("Lyrics__Container-.*")
    re_replace = re.compile("<\/i>|<i>|<b>|<\/b>")
    clean_str = re.sub(re_replace, "\n", str(html))

    cleanSoup = BeautifulSoup(clean_str,features="html.parser")
    div_lyrics = cleanSoup.find_all("div", class_=new_re)
    list_lyrics = []
    for container_lyrics in div_lyrics:
        list_lyrics+=(list(container_lyrics.stripped_strings))

    #pattern = re.compile("\[.*Chorus.*]$|\[.*Verse.*]$|\[.*Intro.*]$|\[.*Outro.*]$|\[.*Refrain.*]$|\[.*Drop.*]$|\[.*Bridge.*]")
    pattern = re.compile("\[.*?\]*")
    lyrics = ""
    for line in list_lyrics:
        if not re.search(pattern, line):
            lyrics+= line+"\n"
        else:
            print(f"String matches pattern: {line}")
            lyrics+= "\n"
    print(lyrics)
    
    
if __name__ == "__main__":
    main()
