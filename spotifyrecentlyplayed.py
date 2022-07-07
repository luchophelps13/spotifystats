import sys
import spotipy
from spotipy.oauth2 import SpotifyOAuth

import matplotlib as mpl
import matplotlib.pyplot as plt

from collections import Counter

import requests
import urllib

import io
import base64
from PIL import Image
import numpy as np
from ordered_set import OrderedSet

from cryptography.fernet import Fernet

import time

import itertools
from more_itertools import sort_together

from misc import playlist_descr, recent_artists

import os

def get_secrets():

    with open("secrets/key.key", "rb") as k:
        key = k.read() # I encrypted the client_id and client_secret with a fernet key
   

    with open("secrets/secrets.txt") as s:
        #secrets\secrets.txt
        secrets = s.read() # get the id and secret

    f_key = Fernet(key)
    client_id, client_secret = f_key.decrypt(secrets.split("\n")[0].encode()), f_key.decrypt(secrets.split("\n")[1].encode()) 
                                            # the id is the first line, get that line ("\n" is newling), encode it, decrypt it repeat


    return client_id, client_secret 

client_id, client_secret = get_secrets()

mpl.rcParams['font.size'] = 8.0 # FOR WEB VERSION
mpl.rcParams['text.color'] = 'white' # FOR WEB VERSION
mpl.rcParams['axes.labelcolor'] = 'white' # FOR WEB VERSION
mpl.rcParams['xtick.color'] = 'white' # FOR WEB VERSION
mpl.rcParams['ytick.color'] = 'white' # FOR WEB VERSION

sp = spotipy.Spotify(client_credentials_manager=SpotifyOAuth(client_id = client_id.decode(), 
                                                             client_secret = client_secret.decode(),
                                                             redirect_uri = "http://localhost:5000/redirect",
                                                             scope = "user-library-read user-read-recently-played playlist-modify-public")) 

recently = sp.current_user_recently_played()["items"]

class SpotifySongTracker: # no __init__ needed

    def get_recently_played(self, limit=50) -> list: # -> indicates return type, not required just to eliminate confusion
        # 50 is the max number of recent tracks Spotipy allows you to look at/ can look at
        '''Returns the user's recently listened to tracks with the artist.''' # DOCSTRING, user can highlight the function to see a description

        results = sp.current_user_recently_played(limit) # Number of tracks the user wants (max 50)
        songs = [] 
        index = 0

        for _, item in enumerate(results['items']): # will separate each track, artist. '_' is a placeholder used because the first value is not important

            # print(_, item) _ is the index (0-> limit), item is the JSON dictionary containing artist, track, duration, etc.

                                                    # enumerate is used to loop over multiple values with the same length simultaneously
            info = item['track'] # 'href': 'https://api.spotify.com/v1/tracks/5SF1kcOiOmtZFUIQNGC4TC', 'id': '5SF1kcOiOmtZFUIQNGC4TC', 'is_local': False, 
                                
                                 #'name': 'The Birds Pt. 1 - Original', 'popularity': 41, 'preview_url': None, 'track_number': 5, 
                                 # 'type': 'track', 'uri': 'spotify:track:5SF1kcOiOmtZFUIQNGC4TC'}, 'played_at': '2022-04-28T21:54:09.179Z', 'context': None}
                                # GIGANTIC JSON DICT

            artist = ""
            
            artists_count = len(info["artists"])

            #if info["name"] == "Vertigo":
            #    for i in range(len(info["artists"])):
            #        print(info['artists'][i]['name'])

            #if artists_count > 1:
            #    for i in range(len(info["artists"]) - 1):
            #        artist += f"{info['artists'][i]['name']}, "     # At key 'artists' -> artists': [{'external_urls': {'spotify': 'https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ'}, 'href': 'https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ', 'id': '1Xyo4u8uXC1ZmMpatF05PJ', 
            #                                                        # 'name': 'The Weeknd', 'type': 'artist', 'uri': 'spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ'}]
            #                                                        # Get the 0th value (list), then key 'name'
            #else:
            for i in range(len(info["artists"])):
                artist += f"{info['artists'][i]['name']}; "                 

            artist = artist[:-2]

            track = info["name"] # 'name': 'U2' (or whatever)

            songs.append([[track, artist], [index + 1]]) # append (add) song and artist to list, e.g. 'Bohemian Rhapsody - Queen' (Song - artists)

            index += 1

        return songs # return the list, so value can be accessed outside of the function by calling the function
                     # then setting a value equal to the call of a function (a = test())

    def get_user_top_songs_recently(self):
        top_songs_rec = []
        top_songs_urls = []

        i = 0

        #rec = s.get_recently_played(50)

        #top_songs = [song["name"] for song in sp.current_user_top_tracks(5)["items"]]

        #for song, _ in rec:
        #    if song[0] in top_songs:
        #        print("recent song in recent top", song)


        for song in sp.current_user_top_tracks(5)["items"]:
            top_songs_rec.append([[song['name'], [song['artists'][0]['name']]], [i + 1]])
            top_songs_urls.append(song['external_urls'])

            i += 1

        return top_songs_rec, top_songs_urls

    def get_user_top_albums(self):
        top_albums = {}
        top_albums_urls = []

        print(sp.curre(5)['items'][0]['name'])

        i = 0

        for song in sp.current_user_top_tracks(5)["items"]:
            top_albums.update({f"{song['artists'][0]['name']} - {song['name']}": i + 1})
            top_albums_urls.append(song['external_urls'])

            i += 1

        return top_albums, top_albums_urls

    def graph_artists_breakdown(self):
        '''Graphs artists user has recently listened to in a pie chart.'''

        songs_per_artist = {}
        artists = []
        songs = s.get_recently_played()

        #print(songs)

        artists = recent_artists(songs) # right hand side
        #print([song.split(" ; ") for song in songs])  #[song.split(" - ")[0] for song in songs])
        #for artist in artists:

            #if len(artist.split(", ")) > 1:
            #    multiple = artist.split(", ") # featured artists
            #    artists.append(multiple)

        for i in range(len(songs)):
            songs_per_artist.update({artists[i]: artists.count(artists[i])}) # e.g. {The Beatles - 5}

        artists = list(songs_per_artist.keys()) # {key, value}, get the keys
        num_songs = list(songs_per_artist.values())


        index = [i for i, j in enumerate(num_songs) if j == max(num_songs)] # most songs is most listened to artist recently
        most_listened_to_artist = []
        explode = np.zeros((1, len(artists))).tolist() # array of 0s the size of the number of artists

        for i in range(len(index)):
            most_listened_to_artist.append(artists[i])
            explode[0][index[i]] = 0.1 

        explode = explode[0] # explode the first (most listened to) artist

        def func(pct, allvals): # Stack overflow, not mine
            absolute = int(round(pct/100 * np.sum(allvals)))
            if pct <= 5: # avoid clutter
                return ""

            return "{:.1f}%\n({:d} songs)".format(pct, absolute)
        
        fig = plt.figure()
        fig.set_size_inches(7, 7)

        plt.pie(num_songs, explode = explode, labels = artists, autopct = lambda pct: func(pct, num_songs)) # percent makeup of each artist
        plt.title("The Artists You Listened to The Most Recently: ", fontsize = 15)
        
        buf_2 = io.BytesIO()
        plt.savefig(buf_2, format='png', transparent = True, bbox_inches = "tight")
        buf_2.seek(0)

        pie_graph = urllib.parse.quote(base64.b64encode(buf_2.read()).decode())

        return pie_graph

    def get_most_listened_to(self, get_id = False):

        artists = []
        artists_ids = []

        for i in range(len(recently)):
            artists.append(recently[i]["track"]["artists"][0]["name"]) # get each artist
            artists_ids.append(recently[i]["track"]["artists"][0]["uri"])

        new_list = [item for items, c in Counter(artists).most_common() for item in [items] * c] # STACK OVERFLOW 
        new_list = OrderedSet(new_list) # a set is a 
        top5_artists = new_list[0:5]

        if get_id:
            return top5_artists, artists_ids
        else:
            return top5_artists

    def find_new_artists(self):
        '''Recommend a new artist for each artist listened to.'''

        artists = []
        artists_id = []

        genres = {} # in development still

        related_artists = []
        related_artists_links = []
        related_artists_ids = []
        

        for i in range(len(recently)):
            artists_id.append(recently[i]["track"]["artists"][0]["id"])

        for j in range(len(recently)):
            if sp.artist(recently[j]["track"]["artists"][0]["id"])["popularity"] > 5: 
                genres.update({recently[j]["track"]["artists"][0]["id"] : sp.artist(artists_id[j])["genres"][0]})
                artists.append(recently[j]["track"]["artists"][0]["name"])

        artists_listened_to = list(OrderedSet(artists)) #only one of each
        related_artists_links = list(OrderedSet(related_artists_links))

        for i in range(len(genres)):
            related_artists.append(sp.artist_related_artists(list(genres.keys())[i])["artists"][0]["name"]) # ‘sp.artist_related_artists’ is a built in function that takes in an artists ID, 
            # so we will do that then convert their ID to their name to make sense to the user 
            related_artists_links.append(sp.artist_related_artists(list(genres.keys())[i])["artists"][0]["external_urls"]["spotify"])
            related_artists_ids.append(sp.artist_related_artists(list(genres.keys())[i])["artists"][0]["id"])

        return artists_listened_to, related_artists, related_artists_links, related_artists_ids # WEB VERSION

    def graph_song_data(self):
        '''Create 2 graphs of song data, containing averages of info. such as tempo, valence, energy, and duration.'''

        songs_id = []
        audio_features = []

        for i in range(len(s.get_recently_played())):
            songs_id.append(sp.current_user_recently_played()["items"][i]["track"]["uri"].strip("spotify:track:"))
            audio_features.append(sp.audio_features(songs_id[i])[0])

        # STATS TO LOOK AT

        avg_danceability = []
        avg_energy = []
        avg_speechiness = []
        avg_acousticness = []
        avg_instrumentalness = []
        avg_liveness = []
        avg_valence = []
        avg_tempo = []
        avg_duration = []

        for af in audio_features:
            try:
                avg_danceability.append(af["danceability"])
                avg_energy.append(af["energy"])
                avg_speechiness.append(af["speechiness"])
                avg_acousticness.append(af["acousticness"])
                avg_instrumentalness.append(af["instrumentalness"])
                avg_liveness.append(af["liveness"])
                avg_valence.append(af["valence"])
                avg_tempo.append(af["tempo"])
                avg_duration.append(af["duration_ms"])

            except TypeError: # some random errors
                pass

        # FIND AVERAGE
        avg_danceability = np.mean(avg_danceability)
        avg_energy = np.mean(avg_energy)
        avg_speechiness = np.mean(avg_speechiness)
        avg_acousticness = np.mean(avg_acousticness)
        avg_instrumentalness = np.mean(avg_instrumentalness)
        avg_liveness = np.mean(avg_liveness)
        avg_valence = np.mean(avg_valence)
        avg_tempo = np.mean(avg_tempo)
        avg_duration = np.mean(avg_duration) / 60000 # 1000 milliseconds in a second, 60 seconds in a minute

        avgs = {"Danceability": avg_danceability, "Energy": avg_energy, "Speechiness": avg_speechiness, 
        "Acousticness": avg_acousticness, "Instrumentalness": avg_instrumentalness, "Liveness": avg_liveness, "Valence": avg_valence,
        "Duration (min)": avg_duration}

        categories = list(avgs.keys())
        values = list(avgs.values())

        #plt.tight_layout()

        fig, axs = plt.subplots(1, 2, figsize=(9, 3), sharey=False)
        axs[0].scatter(categories, values)
        axs[0].set_xticklabels(labels = categories, rotation = 70)
        axs[1].scatter("Tempo (BPM)", avg_tempo)
        fig.suptitle("Average Stats for the Songs You've Recently Listened To", fontsize = 15)

        buf = io.BytesIO()
        fig.savefig(buf, format='png', transparent = True, bbox_inches="tight")
        buf.seek(0)

        plot_data = urllib.parse.quote(base64.b64encode(buf.read()).decode())
 
        return plot_data, axs

    def graph_genre_breakdown(self):        
        top_6_big_genres = {"Adult Contemporary": 0, "Alternative": 0, "Avante-Garde": 0, "Blues": 0, "Classical": 0, 
                            "Disco": 0, "Electronic": 0, "Experimental": 0, "Folk": 0, "Funk": 0, "Hip Hop": 0, "Indie": 0, "Jazz": 0, 
                            "Latin": 0, "Metal": 0, "Neo Soul": 0, "Pop": 0, "Progressive": 0, "Psychedelic": 0, "Punk": 0, "R&B": 0, 
                            "Reggae": 0, "Rock": 0, "Samba": 0, "Soul": 0, "Traditional": 0, "Video game music": 0, "Worship": 0}

        top_5_subgrenres = []

        top_tracks = sp.current_user_top_tracks()["items"]

        #print(top_tracks[0].keys())

        g = sp.artist(top_tracks[0]["artists"][0]["external_urls"]["spotify"])["genres"]


        for i in range(len(top_tracks)):
            #print(sp.artist(top_tracks["artists"][0]["external_urls"]["spotify"])["genres"]) # keys are dict_keys(['album', 'artists', 'available_markets', 'disc_number', 'duration_ms', 'explicit', 
                               # 'external_ids', 'external_urls', 'href', 'id', 'is_local', 'name', 'popularity', 'preview_url', 
                               # 'track_number', 'type', 'uri'])

            genres = sp.artist(top_tracks[i]["artists"][0]["external_urls"]["spotify"])["genres"]

            #print(genres)

            top_5_subgrenres.append(genres)

            genres = genres[0] # use most prevalent genre || ['alternative r&b', 'hip hop', 'lgbtq+ hip hop', 'neo soul', 'pop']
                               # -> 'alternative r&b)
  
            if "adult contemporary" in genres:
                top_6_big_genres["Adult Contemporary"] += 1
            if "avante-garde" in genres:
                top_6_big_genres["Avante-Garde"] += 1
            if "classical" in genres:
                top_6_big_genres["Classical"] += 1
            if "electronic" in genres or "electronica" in genres or "edm" in genres or "house" in genres:
                top_6_big_genres["Electronic"] += 1
            if "funk" in genres:
                top_6_big_genres["Funk"] += 1
            if "country" in genres or "country roads" in genres or "folk" in genres or "roots" in genres or "bluegrass" in genres:
                top_6_big_genres["Folk"] += 1          
            if "hip hop" in genres or "rap" in genres or "trap" in genres:
                top_6_big_genres["Hip Hop"] += 1
            if "indie" in genres:
                top_6_big_genres["Indie"] += 1
            if "jazz" in genres:
                top_6_big_genres["Jazz"] += 1
            if "metal" in genres or "djent" in genres:
                top_6_big_genres["Metal"] += 1
            if "neo soul" in genres:
                top_6_big_genres["Neo Soul"] += 1
            if "pop" in genres:
                top_6_big_genres["Pop"] += 1 
            if "progressive" in genres or "prog" in genres:
                top_6_big_genres["Progressive"] += 1
            if "psychedelic" in genres or "psychedelia" in genres:
                top_6_big_genres["Psychedelic"] += 1
            if "punk" in genres or "ska" in genres:
                top_6_big_genres["Punk"] += 1
            if "r&b" in genres or "rhythm and blues" in genres or "merseybeat" in genres:
                top_6_big_genres["R&B"] += 1
            if "rock" in genres or "merseybeat" in genres or "skiffle" in genres:
                top_6_big_genres["Rock"] += 1
            if "soul" in genres:
                top_6_big_genres["Soul"] += 1
            if "bossa nova" in genres or "samba" in genres:
                top_6_big_genres["Samba"] += 1
            if "video game music" in genres:
                top_6_big_genres["Video Game Music"] += 1
            if "worship" in genres:
                top_6_big_genres["Worship"] += 1
                
        for key in list(top_6_big_genres.keys()):
            if top_6_big_genres[key] == 0:
                top_6_big_genres.pop(key)

        keys = list(top_6_big_genres.keys())
        values = list(top_6_big_genres.values())

        fig, ax = plt.subplots(figsize=(8, 6))
        fig = plt.gcf()
        ax.bar(keys, values)
        

        ax.set_title("Bar Plot of Distribution of Your Genres :D", fontsize = 15, pad = 20)
        ax.set_xlabel('Genre')
        ax.set_xticks(ticks = [x for x in range(len(keys))])
        ax.set_xticklabels(labels = keys)
        ax.set_ylabel('# of Songs')

        buf_3 = io.BytesIO()
        plt.savefig(buf_3, format='png', transparent = True, bbox_inches = "tight")
        buf_3.seek(0)

        bar_graph = urllib.parse.quote(base64.b64encode(buf_3.read()).decode())

        top_5_subgrenres = list(itertools.chain.from_iterable(top_5_subgrenres)) # Combine list of lists to one single list

        top_5_subgrenres = OrderedSet([item.title() for items, c in Counter(top_5_subgrenres).most_common() for item in [items] * c])[0:5]
        # Sort list of every genre by frequency, remove duplicates

        return bar_graph, list(top_5_subgrenres)

    def get_artist_picture(self): # LABELS ARE IN RIGHT ORDER, IMAGES ARE IN WRONG ORDER
        top5 = list(s.get_most_listened_to()) # ["U2", "Weeknd", "Kendrick", "EWF", "J. Cole"]
        last_artists_images = []
        indicies = []

        for i in range(len(recently)): # we need to find the ID of each artist
            if recently[i]["track"]["artists"][0]["name"] in top5: # if recent artist is in the user's top 5 most listened to
                indicies.append(top5.index(recently[i]["track"]["artists"][0]["name"]))
            #{'external_urls': {'spotify': 'https://open.spotify.com/artist/1Xyo4u8uXC1ZmMpatF05PJ'}, 
            # 'href': 'https://api.spotify.com/v1/artists/1Xyo4u8uXC1ZmMpatF05PJ', 'id': '1Xyo4u8uXC1ZmMpatF05PJ', 
            # 'name': 'The Weeknd', 'type': 'artist', 'uri': 'spotify:artist:1Xyo4u8uXC1ZmMpatF05PJ'}
            #[top5[i]]


        for i in range(len(recently)):
            if recently[i]["track"]["artists"][0]["name"] in top5:

                #print("\n\n", recently, "\n\n") # recently[i]["track"]["artists"][0]["id"]
                last_artists_images.append(sp.artist(recently[i]["track"]["artists"][0]["id"])["images"][0]["url"]) # get each image from the JSON

        top_artists_images = OrderedSet(sort_together([indicies, last_artists_images])[1])
        
        #top_artists_images = list(OrderedSet(last_artists_images))
        imgs = []

        for i in range(len(top_artists_images)):
            im = Image.open(requests.get(top_artists_images[i], stream=True).raw)
            
            ### FOR WEBSITE VERSION VVV

            buf = io.BytesIO()
            im.save(buf, format="jpeg") #png
            #image_file.convert('RGB').save(t_filename, "PNG", optimize=True)
            buf.seek(0)
            plot_data = urllib.parse.quote(base64.b64encode(buf.read()).decode()) # FROM STACK OVERFLOW, used so I don't have to download every image
            imgs.append(plot_data)
        
        return imgs

    def make_playlist(self, is_public = False):

        recommended_artists_ids = list(OrderedSet(s.find_new_artists()[-1]))

        user = sp.me()["external_urls"]["spotify"].strip("https://open.spotify.com/user/")

        new_playlist = sp.user_playlist_create(user, "Spotify Stats Recommended Artists Playlist", description = playlist_descr(), public = is_public)

        recommended_artists_songs = []

        def get_playlist_songs(list1): #, list2):

            new_list = []

            for i in range(5):
                new_list.append(sp.recommendations(list1[0:5], limit = 10)['tracks'][i]["uri"])
                new_list.append(sp.recommendations(list1[5:10], limit = 10)['tracks'][i]["uri"])

            #for j in range(len(recommended_artists_ids)):
            #    new_list.append(sp.recommendations(list2[j], limit = 1)['tracks'][i]["uri"])

            return new_list


        new_songs = get_playlist_songs(recommended_artists_ids) # our problem is its only adding the 0th and 5th

        # REMOVE DUPLICATES
        i = 0
        for i in range(len(new_songs)):
            if new_songs.count(new_songs[i]) > 1:
                new_songs[i] = sp.recommendations(new_songs[i])
                

        sp.user_playlist_add_tracks(sp.me()["external_urls"]["spotify"].strip("https://open.spotify.com/user/"), new_playlist["id"], new_songs) # try using the song's uri

        #print(new_playlist["id"]) #[0]["id"][0]["external_urls"][0]["spotify"].split("/embed/"))

        playlist_url = f"https://open.spotify.com/embed/playlist/{new_playlist['id']}?utm_source=generator&theme=0"

        return recommended_artists_songs, playlist_url

    def format_top_or_recent(self, list_):

        list_ = str(list_).strip("OrderedSet()[]()") #get rid of "OrderedSet(...) and the list brackets"

        return list_

    def t(self):
        #return sp.me()["external_urls"]["spotify"].strip("https://open.spotify.com/user/") #["display_name"]
        lz_tracks = sp.artist_top_tracks('spotify:artist:36QJpDe2go2KgaRleHCDTp')

        for track in lz_tracks['tracks'][:3]:
            print(track["name"], track["external_urls"]["spotify"])

def load():

    print("\n\nWelcome! This project uses the Spotipy Python library to show the user their recent artists, recommend new artists, and graph song data.\n Let's get you started!")

    choice = input("\nLet's start with your recently plyed artists and songs!. Type 'Yes' to proceed (case sensitive) and 'No' to exit the program: ")

    if choice == "Yes":
        num_songs = input("\nHow many recent songs would you like? The max is 50, so please enter an integer between 1 and 50, and if you're not sure, enter 'Not sure': ")

        recent = s.get_recently_played()
        
        if num_songs == "Not sure":
            print("\n", recent, "\n")
            print("\nWow! You have great taste!")

            print(f"Now, because you like {s.find_new_artists()[0]}, I recommend {s.find_new_artists()[1]}") # s.find_new_artists() returns current artists, new artists, and a hyperlink to that artist's spotify (web)

        elif isinstance(num_songs, int):
            print("\n", s.get_recently_played(num_songs), "\n")
            print("\nWow! You have great taste!")

            print(f"\nNow, because you like {s.find_new_artists()[0]}, I recommend {s.find_new_artists()[1]}")

        else: 
            print("Invalid input")

    else: # Invalid input will exit the program as well.
        sys.exit()

    second_choice = input("\n\nNow, would you like to see your top 5 (or less*) artists as of late, or a pie graph of your favorite artists? Input 'top 5' or 'graph'\n")

    if second_choice == "top 5":
        print("\nYour top 5 (or less*) as of late: ", s.format_top_or_recent(s.get_most_listened_to())) # remove 'OrderedSet(...) formatting from list of top artists

        time.sleep(2) # allow user to look at data

        print("\nNow let's see that graph!")
        s.graph_artists()

    elif second_choice == "graph":
        s.graph_artists()

        time.sleep(2) # wait 2 seconds

        print("\nSweet. Let's see that top five! ")
        time.sleep(2)
        print("\nYour top 5 (or less*) as of late: ", s.format_top_or_recent(s.get_most_listened_to())) 
    else:
        print("\nInvalid input")

    final_choice = input("\n\nFinally, would you like to see some graphs about your music taste, including average tempo, acousticness, danceability, duration, and more? Please enter 'Yes' or 'No'.\n")

    if final_choice == "Yes":
        
        fig = s.graph_song_data()[1] # access 2nd parameter of function return, 1st is for saving graph in a string buffer to be sent to HTML

        plt.show() # show the graph created using matplotlib

        print("Thank you so much for using the program! The web version will be released shortly! For now and for more updates, check my github: www.github.com/luchophelps13") 

        sys.exit()


    else:
        print("Thank you so much for using the program! The web version will be released shortly! For now and for more updates, check my github: www.github.com/luchophelps13") 
        sys.exit()

s = SpotifySongTracker() # create instance of class
if __name__ == "__main__": 
    rec = s.get_user_top_songs_recently()[0]

    for item in rec:
        print(item[0][1][0])
