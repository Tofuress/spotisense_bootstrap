import os

from flask import Flask, session, redirect, url_for, request, render_template

from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import FlaskSessionCacheHandler
from spotify_service import *

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(64)

client_id = '6eccdbfd6845441f9ace3028b5ef7337'
client_secret = 'e67b8650c40041b085cc5f13a8e4e476'
redirect_uri = 'http://localhost:5000/callback'
scope = 'user-library-read user-read-currently-playing playlist-read-collaborative user-library-modify playlist-read-private playlist-modify-public playlist-modify-private user-top-read user-modify-playback-state user-read-playback-state'

cache_handler = FlaskSessionCacheHandler(session)
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=cache_handler,
    show_dialog=True
)
sp = Spotify(auth_manager=sp_oauth)


@app.route('/')
def main():
    return render_template('intro.html')


@app.route("/authorize")
def home():
    auth_url = sp_oauth.get_authorize_url()
    return redirect(auth_url)
    #return redirect(url_for('get_playlists'))


@app.route('/callback')
def callback():
    sp_oauth.get_access_token(request.args['code'])
    return redirect(url_for('index'))

@app.route('/index')
def index():
    tokens = session.get('tokens')
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)
    access_token = cache_handler.get_cached_token()['access_token']
    sp = Spotify(auth=access_token)
    data = user_content(sp)
    playlists = playlist(sp)
    return render_template('index.html', data=data, playlists=playlists)


@app.route('/playlist_intro')
def playlist_intro():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return render_template("intro.html")
    #sp = Spotify(auth=session['tokens'].get('access_token'))
    playlists = playlist(sp)
    return render_template('playlist_intro.html', playlists=playlists)


@app.route('/playlist_select', methods=['GET', 'POST'])
def playlist_select():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return render_template("intro.html")
    select = request.form.get('comp_select')
    #sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    stats = playlist_calculation(sp, select)
    playlist_name = (select.split("'"))[3]
    return render_template("playlist_select.html", playlist=playlist_name, stats=stats)


@app.route("/recs")
def recs():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return render_template("intro.html")
    # sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    genres = []
    for gen in sp.recommendation_genre_seeds()['genres']:
        genres.append(gen)
    return render_template("recs.html", genre=genres)


@app.route("/recs_final", methods=['GET', 'POST'])
def recs_final():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return render_template("intro.html")
    specs = {
        'name': request.form['name'],
        'number': request.form['quantity'],
        'select': request.form.getlist('comp_select'),
        'dance': request.form['danceability'],
        'energy': request.form['energy'],
        'valence': request.form['valence']
    }
    if not specs.get('dance'):
        specs.pop('dance')
    if not specs.get('energy'):
        specs.pop('energy')
    if not specs.get('valence'):
        specs.pop('valence')
    name = recs_playlist(cache_handler.get_cached_token()['access_token'], specs=specs)
    return render_template("recs_final.html", name=name)


@app.route("/top_stats_intro")
def top_stats_intro():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return render_template("intro.html")
    return render_template("top_stats_intro.html")


@app.route("/top_stats", methods=['GET', 'POST'])
def top_stats():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return render_template("intro.html")
    limit = request.form['limit']
    time = request.form['time']
    print(cache_handler.get_cached_token())
    top = get_top(cache_handler.get_cached_token()['access_token'], limit, time)
    return render_template("top_stats.html", stats=top)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/related_artists")
def related_artists():
    return render_template("related_artists.html")


@app.route("/for_nerds")
def for_nerds():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        return render_template("intro.html")
    # sp = spotipy.Spotify(auth=session['tokens'].get('access_token'))
    data = user_content(sp)
    return render_template("for_nerds.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(401)
def spotify_exception(error):
    return render_template('401.html'), 401
'''''
@app.route('/get_playlists')
def get_playlists():
    if not sp_oauth.validate_token(cache_handler.get_cached_token()):
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

    playlists = sp.current_user_playlists()
    playlists_info = [(pl['name'], pl['external_urls']['spotify']) for pl in playlists['items']]
    playlists_html = '<br>'.join([f'{name}: {url}' for name, url in playlists_info])

    return playlists_html
'''

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
