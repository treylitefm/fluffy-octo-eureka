from lxml import html
import requests
import string
import json
from re import search
import time

from genius_model import Model

def fetch_artists(path=None):
    print 'Fetching artists'
    
    try:
        artists = load(path)['data']
        print 'Loading artists from:', path
        return artists
    except:
        pass

    alpha = list(string.ascii_lowercase)
    alpha = ['z']
    links = []
    count = 0

    for letter in alpha:
        i = 1
        while True:
            full_url = url+'/artists-index/'+letter+'/all' + ('?page='+_to_u_string(i) if i > 1 else '')
            page = requests.get(full_url)
            tree = html.fromstring(page.content)
            results = tree.xpath('//*[@class="artists_index_list"]//a/@href')
            if results:
                links += results
            else:
                break
            print full_url, count
            i += 1
            count += 1

    print 'Total:', len(links)
    return links
    

def fetch_songs_for_artist(link, path=None):
    print 'Fetching songs for artist link:', link

    artist_name = link.split('/')[-1]

    page = requests.get(link)
    tree = html.fromstring(page.content) 

    match = tree.xpath('//form[contains(@id, edit_artist_)]/@id');
    numeric_id = match[0].split('_')[-1]
    
    print 'Artists Name:', artist_name
    print 'Artist Id:', numeric_id

    links = []
    i = 2
    count = 1
    while True:
        print url+'/artists/songs?for_artist_page='+numeric_id+'id='+artist_name+'&page='+_to_u_string(i)+'&pagination=true', count
        page = requests.get(url+'/artists/songs?for_artist_page='+numeric_id+'id='+artist_name+'&page='+_to_u_string(i)+'&pagination=true')
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
    print 'Genius Link:', link
    page = requests.get(link)
    tree = html.fromstring(page.content)

    artists = tree.xpath('//*[contains(@class, "text_artist") or contains(@class, "featured_artists")]/a/text()')
    artists = map(_cleanse, artists)
    artists = _map_lyrics_to_artists(artists, tree)

    name = _get_song_name(tree)
    views = _get_views(tree)
    producers = _get_producers(tree)
    writers = _get_writers(tree)
    song_link = _get_song_link(tree)

    #print "Name:", name
    #print "Views:", views
    #print "Producers:", producers
    #print "Writers:", writers
    #print "Song Link:", song_link
    #print "Artists & Lyrics", artists

    return {
            "song_name": name,
            "views": views,
            "producers": producers,
            "writers": writers,
            "song_link": song_link,
            "artist_lyrics": artists
            }
    

def _map_lyrics_to_artists(artists, tree):
    no_features = len(artists) is 1
    artists = dict(zip(artists, [[] for i in range(len(artists))]))
    lyrics = tree.xpath('//div[@class="lyrics"]/p//text()')
    lyrics = map(_cleanse, lyrics)
    lyrics = filter(lambda s: s and not s.isspace(), lyrics)
    current_artist = None


    if (no_features): #logic for giving all lyrics to main artist
        current_artist = artists.keys()[0]
        for snippet in lyrics:
            if "[" not in snippet:
                artists[current_artist].append(snippet)
    else: #logic for giving lyrics to artists depending on verse\'s preceding artist tag
        #print artists

        for snippet in lyrics:
            m = search('\[([\w\s]*[:\/]\s)?([\w\s\.\$]+)(.+\(([\w\.\s\$]*)\))?\]', snippet);
            #print snippet
            try:
                #print 'Group:', m.group(2)
                current_artist = m.group(2) #TODO: account for cases where a verse is done by two artists, for example: guilty conscience and donkey milk
            except:
                #print snippet, 'no match', current_artist, artists.get(current_artist), artists
                for artist in artists.keys():
                    if current_artist is not None:
                        if current_artist in artist:
                            artists[artist].append(snippet)
                            break
                        else:
                            #print "Not a key within artists dictionary: ", current_artist
                            pass
    return artists

def _get_song_name(tree):
    song_name = tree.xpath('//*[contains(@class,"text_title")]/text()')
    song_name = map(_cleanse, song_name)
    return song_name

def _get_views(tree):
    #views = tree.xpath('//*[contains(@class,"song_views")]/text()') 
    #views is a pseudo-element so it is not attainable through conventional means
    #TODO: find ways of scraping pseudo-element
    #views = map(_cleanse, views)
    return []

def _get_producers(tree):
    producers = tree.xpath('//*[contains(@class,"producer_artists")]/a/text()')
    producers = map(_cleanse, producers)
    return producers

def _get_writers(tree):
    writers = tree.xpath('//*[contains(@class,"writer_artists")]/a/text()')
    writers =  map(_cleanse, writers)
    return writers

def _get_song_link(tree):
    song_link = tree.xpath('//*[contains(@class, "audio_link")]/a/@href')
    song_link = map(_cleanse, song_link)
    return song_link

def _cleanse(text):
    text = text.strip()
    text = text.replace(",", "")
    text = text.replace("'", "")
    return text.lower()

def _to_u_string(text):
    return ''.join(str(text)).encode('utf-8')

def _insert_songs(data, model):
    return model.insert('songs', name=''.join(data['song_name']), views=''.join(data['views']), song_link=''.join(data['song_link']))

def _insert_artists(data, model):
    print '\n'.join(data['artist_lyrics'].keys())
    for artist in data['artist_lyrics'].keys():
        model.insert('artists', name=artist, song_id=data['song_id'])

def _insert_producers(data, model):
    for producer in data['producers']:
        model.insert('producers', name=producer, song_id=data['song_id'])

def _insert_writers(data, model):
    for writer in data['writers']:
        model.insert('writers', name=writer, song_id=data['song_id'])

def _insert_lyrics(data, model):
    for artist in data['artist_lyrics'].keys():
        model.insert('lyrics', artist=artist, snippet=' '.join(data['artist_lyrics'][artist]), song_id=data['song_id'])

def _insert_all(data):
    m = Model('genius.db')
    song_id = _insert_songs(data, m)
    data['song_id'] = song_id
    _insert_artists(data, m)
    _insert_producers(data, m)
    _insert_writers(data, m)
    _insert_lyrics(data, m)

def save(data, path):
    with open(path, 'w') as fp:
        json.dump({'data': data}, fp)

def load(path):
    with open(path, 'r') as json_data:
        return json.load(json_data)

def main():
    start_time = time.time()

    global url
    url = 'http://genius.com'
    samples = [
    'http://genius.com/Odd-future-oldie-lyrics',
    'http://genius.com/Chaka-khan-through-the-fire-lyrics',
    'http://genius.com/Kanye-west-through-the-wire-lyrics',
    'http://genius.com/Eminem-guilty-conscience-lyrics',
    'http://genius.com/Tyler-the-creator-assmilk-lyrics'
    ]

    #_insert_all(fetch_song_info(samples[1]))
    #for track in samples:
    #    _insert_all(fetch_song_info(track))
    path = 'res/artists.json'

    artist_links = dict(map(lambda link: (link, False), fetch_artists(path)))
    for artist_link in artist_links.keys():
        if artist_links[artist_link] is True:
            print 'Passing: ',artist_link
            pass
        song_links = fetch_songs_for_artist(artist_link)
        for song_link in song_links:
            info = fetch_song_info(song_link)
            _insert_all(info)
        artist_links[artist_link] = True
        save(artist_links, path)
        
    elapsed_time = time.time() - start_time
    print "\nFinished in "+str(elapsed_time)+" seconds" 
    #print fetch_songs_for_artist('http://genius.com/artists/Toni-braxton')
    #print fetch_song_info('http://genius.com/Toni-braxton-youve-been-wrong-lyrics')
    #print fetch_song_info('http://genius.com/A-for-jer-lyrics')
    #print fetch_song_info('http://genius.com/Accurate--lyrics')


if __name__ == "__main__":
    main()
