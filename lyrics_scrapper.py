from bs4 import BeautifulSoup, Tag
import requests
import re

def tmp():
    def _get_item_from_search_response(self, response, title, artist, type_, result_type):
        """Gets the desired item from the search results.

        This method tries to match the `hits` of the :obj:`response` to
        the :obj:`response_term`, and if it finds no match, returns the first
        appropriate hit if there are any.

        Args:
            response (:obj:`dict`): A response from
                :meth:‍‍‍‍`Genius.search_all` to go through.
            search_term (:obj:`str`): The search term to match with the hit.
            type_ (:obj:`str`): Type of the hit we're looking for (e.g. song, artist).
            result_type (:obj:`str`): The part of the hit we want to match
                (e.g. song title, artist's name).

        Returns:
            :obj:‍‍`str` \\|‌ :obj:`None`:
            - `None` if there is no hit in the :obj:`response`.
            - The matched result if matching succeeds.
            - The first hit if the matching fails.

        """

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
def main():
    print("lyrics scrapper genius")
    url = "https://genius.com/Kid-cudi-mr-solo-dolo-iii-lyrics"
    response = requests.get(url)
    html = response.content
    #soup = BeautifulSoup(html,features="html.parser")

    new_re = re.compile("Lyrics__Container-.*")
    re_replace = re.compile("<\/i>|<i>|<b>|<\/b>")

    clean_str = re.sub(re_replace, "", str(html))
    cleanSoup = BeautifulSoup(clean_str,features="html.parser")
    div_lyrics = cleanSoup.find_all("div", class_=new_re)
    list_lyrics = []
    for container_lyrics in div_lyrics:
        list_lyrics+=(list(container_lyrics.stripped_strings))
    
    pattern = re.compile("\[.*Chorus.*]$|\[.*Verse.*]$|\[.*Intro.*]$|\[.*Outro.*]$|\[.*Refrain.*]$|\[.*Drop.*]$")
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
