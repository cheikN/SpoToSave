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
    clean_info = sorted(clean_info.lower().split(" "))
    clean_info = " ".join(clean_info).strip()
    
    return clean_info

def get_item_from_search_response(response, title, artist, confidence=0.7):

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
            
            if best_score >= 0.9: #get the best
                return best_item
    
    if best_item is None: #found nothing
        return None
            
    if best_score >= confidence:
        return best_item
    
    best_artist = clean_string(best_item['artist_names'])
    to_find_art = clean_string(artist)
    score_similarty = SequenceMatcher(None, to_find_art, best_artist).ratio()
    print(score_similarty, best_artist,to_find_art)
    if score_similarty >= 0.8 and best_score >= 0.5:
        return best_item
    
    #compare only non-roman characters
    expr_non_char = re.compile("[^a-z\s]+") #for non roman characteres

    to_cmpre = best_item["title"]+" "+best_item['artist_names']
    to_cmpre = clean_string(to_cmpre)
    non_cmpre = re.findall(expr_non_char,to_cmpre)
    non_infos = re.findall(expr_non_char,clean_infos)

    print(non_cmpre,non_infos)
    nb_cmpre = len(non_cmpre)
    nb_info = len(non_infos)
    is_same = non_cmpre == non_infos and len(non_infos) != 0 and len(non_cmpre) != 0

    if  (nb_info == 0 and nb_cmpre > 0) or (nb_cmpre == 0 and nb_info > 0) and not is_same:
        non_cmpre = " ".join(non_cmpre)
        non_infos = " ".join(non_infos)
        wo_cmpre = to_cmpre.replace(non_cmpre,"")
        wo_info = clean_infos.replace(non_infos,"")
        print(wo_cmpre, wo_info)
        score_similarty = SequenceMatcher(None, wo_cmpre, wo_info).ratio()
        is_same = score_similarty > 0.9
    
    """for cmpre, info in zip(non_cmpre, non_infos):
        if cmpre != info:
            is_same = False
            break
    """
    if is_same:
        return best_item
    
    return None

def search(token, title, artist):

    search_term = title+" "+ artist
    genius_search_url = f"http://api.genius.com/search?q={search_term}&access_token={token}"
    response = requests.get(genius_search_url)
    response = response.json()["response"]
    best_item = get_item_from_search_response(response, title, artist)
    if best_item is None:
        return None
    if best_item["lyrics_state"] != "complete":
        return None
    url = best_item["url"]
    lyrics = get_lyrics(url)

    return lyrics if lyrics != "" else None


def get_lyrics(url):
    response = requests.get(url)
    html = response.text

    new_re = re.compile("Lyrics__Container-.*")

    clean_str = html.replace("<br/>", "\n")
    cleanSoup = BeautifulSoup(clean_str,features="html.parser")
    div_lyrics = cleanSoup.find_all("div", class_=new_re)
    
    lyrics ="".join([container_lyrics.get_text() for container_lyrics in div_lyrics ])
    #remove [Chorus] etc
    headers = re.compile("\[.*?\]")
    lyrics = re.sub(headers,"", lyrics)
    
    return lyrics.strip()

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

def main():
    print("lyrics scrapper genius")
    with open('creditentials_all.json') as credits_file:
        creditential = json.load(credits_file)

    GENIUS_API_KEY = creditential["GENIUS_API_KEY"]

    artist_csv = "Mobb Deep"
    list_artists = artist_csv.split(",")
    print(list_artists[:3])
    main_artist = " ".join(list_artists[:3])
    print(f"Looking for the main artist {main_artist}")
    title = "Shook Ones, Pt. II"
    titles = build_anothers_title(title)
    i = 0
    print(titles)
    while i < len(titles):
        clean_tile = titles[i]
        print(search(GENIUS_API_KEY,clean_tile,main_artist))
        i+=1
    
    string = "Shook Ones, Pt. II Pt. II"
    roman_numerals = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
    arabic_numerals = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

    for i in range(len(roman_numerals)):
        pattern = r"\bPt. " + roman_numerals[i] + r"\b"
        string = re.sub(pattern, "part "+arabic_numerals[i], string)
        
    print(string)
if __name__ == "__main__":
    main()