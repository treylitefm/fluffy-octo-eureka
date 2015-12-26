from lxml import html
import requests
import string
import json
from re import search


def fetch_artists():
    alpha = list(string.ascii_lowercase)
    
    links = []
    count = 0
    for letter in alpha:
        i = 1
        while True:
            full_url = url+'/artists-index/'+letter+'/all' + ('?page='+str(i) if i > 1 else '')
            page = requests.get(full_url)
            tree = html.fromstring(page.content)
            results = tree.xpath('//*[@class="artists_index_list"]//a/@href')
            if results:
                links += results
            else:
                break
            print full_url,count
            i += 1
            count += 1

    return links

def fetch_songs_for_artist(link):
    artist_name = link.split('/')[-1]

    page = requests.get(link)
    tree = html.fromstring(page.content) 

    match = tree.xpath('//form[contains(@id, edit_artist_)]/@id');
    numeric_id = match[0].split('_')[-1]
    
    print artist_name, numeric_id

    links = []
    i = 2
    count = 1
    while True:
        print url+'artists/songs?for_artist_page='+numeric_id+'id='+artist_name+'&page='+str(i)+'&pagination=true', count
        page = requests.get(url+'artists/songs?for_artist_page='+numeric_id+'id='+artist_name+'&page='+str(i)+'&pagination=true')
        tree = html.fromstring(page.content)
        results = tree.xpath('//a[contains(@class,"song_name")]/@href');
        if results:
            links += results
        else:
            break
        i += 1
        count +=1

    return links

def fetch_song_info(link):
    '''
    link, name, artist, features, views, lyrics, produced by if present, written by if present, youtube link
    use artists and features to distribute verses
    '''
    page = requests.get(link)
    tree = html.fromstring(page.content)

    results = tree.xpath('//p/text()[contains(.,"Verse")]')
    #//*/text()[contains(., "Verse") or contains(., "Intro") or contains(., "Bridge") or contains(., "Outro") or contains(., "Hook") or contains(., "Interlude")]
    #contains left and right braces, then parse out song part and keep artist name?

    artists = tree.xpath('//*[contains(@class, "text_artist") or contains(@class, "featured_artists")]/a/text()')
    artists = map(_cleanse, artists)
    return _map_lyrics_to_artists(artists, tree)

def _map_lyrics_to_artists(artists, tree):
    no_features = len(artists) is 1
    artists = dict(zip(artists, [[] for i in range(len(artists))]))
    lyrics = tree.xpath('//div[@class="lyrics"]/p//text()')
    lyrics = map(_cleanse, lyrics)
    lyrics = filter(lambda s: s and not s.isspace(), lyrics)


    if (no_features): #logic for giving all lyrics to main artist
        current_artist = artists.keys()[0]
        for snippet in lyrics:
            if "[" not in snippet:
                artists[current_artist].append(snippet)
    else: #logic for giving lyrics to artists depending on verse\'s preceding artist tag
        #print artists

        for snippet in lyrics:
            m = search('\[([\w\s]*:\s)?([\w\s\.\$]+)(.+\(([\w\.\s\$]*)\))?\]', snippet);
            try:
                #print m.group(2)
                current_artist = m.group(2) #TODO: account for cases where a verse is done by two artists, for example: guilty conscience and donkey milk
            except:
                #print snippet,'no match',current_artist, artists.get(current_artist)
                if current_artist in artists:
                    artists[current_artist].append(snippet)
                else:
                    #print "Not a key within artists dictionary: ", current_artist
                    pass
                pass
    return artists



def _cleanse(text):
    text = text.strip()
    text = text.replace(",", "")
    return text.lower()


def save(data, path):
    with open(path, 'w') as fp:
        json.dump({'artists': data}, fp)


def main():
    global url
    url = 'http://genius.com/'

    samples = [
    'http://genius.com/Odd-future-oldie-lyrics',
    'http://genius.com/Chaka-khan-through-the-fire-lyrics',
    'http://genius.com/Kanye-west-through-the-wire-lyrics',
    'http://genius.com/Eminem-guilty-conscience-lyrics',
    'http://genius.com/Tyler-the-creator-assmilk-lyrics'
    ]
    
    print fetch_song_info(samples[2])
    #print fetch_songs_for_artist(url+'artists/Aaliyah/')
    #for i in samples:
     #   print fetch_song_info(i)

if __name__ == "__main__":
    main()
