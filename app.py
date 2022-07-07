from spotifyrecentlyplayed import SpotifySongTracker, get_secrets
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from flask import *
import time

import os

app = Flask(__name__)

app.secret_key = "kt7823hodisazd9" # DO NOT CHANGE
app.config["SESSION_COOKIE_NAME"] = "Lucas Cookie"
TOKEN_INFO = "token_info"

os.environ['MPLCONFIGDIR'] = os.getcwd() + "/configs/"

client_id, client_secret = get_secrets()

is_logged_in = False
 
@app.route("/", methods = ["GET", "POST"])
def home():
    
    if request.method == "GET":
        return render_template("landingpage.html") 
    elif request.method == "POST":
        return redirect(url_for("login"))

@app.route("/aboutme", methods = ["GET", "POST"]) 
def about_me():

    if is_logged_in: # logged in
        return render_template("aboutme.html", logged_in_elem = True)
    else: #if request.method = "POST":
        if request.method == "POST":
            return redirect(url_for("login"))
        else:
            return render_template("aboutme.html", logged_in_elem = False) # log in button

@app.route("/login")
def login():

    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url()

    print(auth_url)

    return redirect(auth_url)

@app.route("/redirect")
def redirectPage():

    sp_oauth = create_spotify_oauth()
    session.clear()
    code = request.args.get("code")
    token_info = sp_oauth.get_access_token(code)
    session[TOKEN_INFO] = token_info

    return redirect("spotify-data")

@app.route("/spotify-data", methods = ["GET", "POST"])
def get_tracks():
        
    global is_logged_in
    is_logged_in = True

    try:
        token_info = get_token()
    except:
        redirect("login")

    #sp = spotipy.Spotify(auth = token_info["access_token"])   
    sst = SpotifySongTracker()

    top5 = sst.get_most_listened_to(get_id = False)
    
    top5_songs_rec, urls = sst.get_user_top_songs_recently()

    five_rec_songs = [song for song, _ in sst.get_recently_played(5)] #sst.get_recently_played(5)

    images = sst.get_artist_picture()

    artists, related_artists, links = sst.find_new_artists()[:-1]

    song_stats_graph = sst.graph_song_data()[0]

    breakdown_of_artists = sst.graph_artists_breakdown()

    breakdown_of_genres = sst.graph_genre_breakdown()[0]
    top_5_subgenres = sst.graph_genre_breakdown()[1]

    if request.method == "GET":

        return render_template("spotifystats.html", top_five_artists = list(zip(top5, images)), top_five_songs_recently = top5_songs_rec, 
                            urls = urls, five_recent_songs = five_rec_songs, artists_and_related_artists = zip(artists, related_artists, links), 
                            avg_graph = song_stats_graph, pie_graph_of_artists = breakdown_of_artists, bar_graph_of_genres = breakdown_of_genres, five_subgenres = top_5_subgenres)

                            # five_recent_songs = five_rec_songs.items()
                            # top_five_songs_recently = top5_songs_rec.items()

    if request.method == "POST":
        if "generateplaylistbutton" in request.form:
            
            newest_playlist_url = sst.make_playlist()[1]

            return render_template("spotifystats.html", top_five_artists = list(zip(top5, images)), top_five_songs_recently = top5_songs_rec, 
                            urls = urls, five_recent_songs = five_rec_songs, artists_and_related_artists = zip(artists, related_artists, links), 
                            avg_graph = song_stats_graph, pie_graph_of_artists = breakdown_of_artists, show_playlist = True, url = newest_playlist_url,
                            bar_graph_of_genres = breakdown_of_genres, five_subgenres = top_5_subgenres)

#@app.route("/", methods = ["POST"])
#def make_playlist():
#
#    return redirect("https://open.spotify.com/")

def get_token():
    token_info = session.get(TOKEN_INFO)

    if not TOKEN_INFO:
        raise "exception"
    now = int(time.time())

    is_expired = token_info["expires_at"] - now < 60

    if is_expired:
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info["refresh_token"])
    
    return token_info

def create_spotify_oauth():
    return SpotifyOAuth(client_id = client_id.decode(), 
                        client_secret = client_secret.decode(),
                        redirect_uri = url_for("redirectPage", _external = True),
                        scope = "user-library-read playlist-modify-public")

if __name__ == "__main__":
    app.run() 
