import requests
import spotipy


def user_content(sp):
    results = sp.current_user_playing_track()
    if results:
        link = results['item']['external_urls']['spotify']
        parsing = link.split('/')
        newlink = parsing[0] + '//' + parsing[1] + '/' + parsing[2] + "/embed/" + parsing[3] + '/' + parsing[4]
        stats = sp.audio_features(parsing[4])
        complete_stats = {
            "dance": int(stats[0]['danceability'] * 100),
            "valence": int(stats[0]['valence'] * 100),
            "energy": int(stats[0]['energy'] * 100),
            "tempo": int(stats[0]['tempo'])
        }
        user_data = sp.current_user()['display_name']
        temp = {
            "name": results['item']['name'],
            "artist": results['item']['artists'][0]['name'],
            "link": newlink,
            "stats": complete_stats,
            "user": user_data
        }
        return temp

# функция получения плейлиста
def playlist(sp):
    playlists = sp.current_user_playlists()
    list = []
    for playlist in playlists['items']:
        id = playlist['external_urls']['spotify'].split("/")[4]
        playlist_obj = {
            "name": playlist['name'],
            "id": id
        }
        list.append(playlist_obj)
    return list

def playlist_calculation(sp, select):
    count = 0
    danceability = 0
    valence = 0
    energy = 0
    tempo = 0
    song_list = []
    for song in sp.playlist_tracks(select.split("'")[7])['items']:
        audio_feature = sp.audio_features(song['track']['external_urls']['spotify'].split("/")[4])
        song_list.append(song['track']['external_urls']['spotify'].split("/")[4])
        danceability += audio_feature[0]['danceability']
        valence += audio_feature[0]['valence']
        energy += audio_feature[0]['energy']
        tempo += audio_feature[0]['tempo']
        count += 1
    avg_danceability = int((danceability * 100) / count)
    avg_valence = int((valence * 100) / count)
    avg_energy = int((energy * 100) / count)
    avg_tempo = int(tempo / count)
    stats = {
        'danceability': avg_danceability,
        'valence': avg_valence,
        'energy': avg_energy,
        'tempo': avg_tempo
    }
    return stats

def recs_playlist(token, specs):
    url = "https://api.spotify.com/v1/recommendations?"
    url += "limit=" + str(specs['number']) + "&market=US&"
    url += "seed_genres="
    count = len(specs['select'])
    if count == 1:
        url += str((specs['select'])[0])
    else:
        i = 0
        while i != count - 1:
            url += str((specs['select'])[i]) + "%2C"
            i+=1
        url += str((specs['select'])[count - 1])
    if 'dance' in specs:
        dance = float(specs['dance']) / 100
        url += "&target_danceability=" + str(dance)
    if 'energy' in specs:
        energy = float(specs['energy']) / 100
        url += "&target_energy=" + str(energy)
    if 'valence' in specs:
        valence = float(specs['valence']) / 100
        url += "&target_valence=" + str(valence)
    tracks = []
    data = requests.get(url, headers={"Authorization": 'Bearer ' + token}).json()
    for track in data['tracks']:
        tracks.append(track['uri'])
    sp = spotipy.Spotify(auth=token)
    user_id = sp.current_user()['id']
    sp.user_playlist_create(user_id, specs['name'], public=True,
                            description="Плейлист создан с помощью Spotisense.")
    playlist_id = (sp.current_user_playlists(1, 0)['items'][0]['id'])
    sp.playlist_add_items(playlist_id, tracks)
    return specs['name']


def get_top(token, limit, time):
    limit = str(limit)
    url = "https://api.spotify.com/v1/me/top/artists?time_range=" + time + "&limit=" + limit
    artist_data = requests.get(url, headers={"Authorization": 'Bearer ' + token}).json()
    print(artist_data)
    url = "https://api.spotify.com/v1/me/top/tracks?time_range=" + time + "&limit=" + limit
    track_data = requests.get(url, headers={"Authorization": 'Bearer ' + token}).json()
    artists = []
    for artist in artist_data['items']:
        artists.append(artist['name'])
    tracks = []
    for track in track_data['items']:
        tracks.append(track['name'])
    len_tracks = len(tracks)
    complete_obj = {
        'artists': artists,
        'tracks': tracks,
        'len_tracks': len_tracks
    }
    return complete_obj

def for_nerds(sp):
    results = sp.current_user_playing_track()
    if results:
        link = results['item']['external_urls']['spotify']
        parsing = link.split('/')
        newlink = parsing[0] + '//' + parsing[1] + '/' + parsing[2] + "/embed/" + parsing[3] + '/' + parsing[4]
        stats = sp.audio_features(parsing[4])
    complete_stats = {

    }
    return complete_stats


