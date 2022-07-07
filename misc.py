def playlist_descr() -> str:

    '''Returns a description for the playlist with the date created.'''

    from datetime import date

    months = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 
              7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}

    today = str(date.today())

    formatted_date = f"{months[int(today.split('-')[1])]} {today.split('-')[2]}, {today.split('-')[0]}"

    descr = f"This playlist was created from Spotipy by the courtesy of Lucas Phillips on {formatted_date}. Here are some recommended songs for you based on your top artists! Enjoy :D"

    return descr

def recent_artists(songs):

    '''Parameter: "get_recently_played()" || Returns a list of every artists of the user's recently listened to songs, including features. Duplicated are also included.'''

    #for track, index in songs:
    #    pass
    ##print(track[1]) # artist(s)
    #

    artists = [track[1].split(";") for track, _ in songs]

    def flatten(xss):
        return [x for xs in xss for x in xs]

    return flatten(artists)
