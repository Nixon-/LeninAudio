__author__ = 'Nixon'

from flask import Flask, render_template, request
from pymongo import MongoClient
import configurations
from Song import Song
import json
import string
from Playlist import Playlist
import threading
import time
import copy

playlist_t = -1
playlist = Playlist()
update_t = -1


def continuous_play():
    global playlist
    while True:
        #playlist.play_next_song()
        while not playlist.audioPlayer.is_stopped():
            time.sleep(1)


def update_playlist():
    while True:
        playlist.update_song_list()
        time.sleep(10)


app = Flask(__name__)


@app.route("/")
def main():
    return render_template("base.html")


@app.route('/_submit_song', methods=['POST'])
def _submit_song():
    title = request.form['title']
    artist = request.form['artist']
    Song(artist, title)
    return json.dumps({"code" : 200})


@app.route("/_get_song_listing.json", methods=["GET"])
def _get_song_listing():
    client = MongoClient()
    coll = client[configurations.DB.NAME][configurations.DB.COLLECTIONS.SONGS]
    songs = dict()
    songs['songs'] = sanitize_song(list(coll.find({}).sort("upvotes", 1)))
    return str(songs).replace("'", '"')


@app.route("/_get_playlist_listing.json", methods=['GET'])
def _get_playlist_listing():
    songs = dict()
    songs['songs'] = sanitize_song(playlist.song_list)
    return str(songs).replace("'", '"')


@app.route("/_upvote_song", methods=["POST"])
def _upvote_song():
    artist = request.json['artist']
    title = request.json['title']
    Song(artist, title).upvote()
    return json.dumps({"code" : 200})


@app.route("/_downvote_song", methods=["POST"])
def _downvote_song():
    artist = request.json['artist']
    title = request.json['title']
    Song(artist, title).downvote()
    return json.dumps({"code" : 200})


def sanitize_song(song_list):
    new_list = list()
    for song in song_list:
        new_song = copy.deepcopy(song)
        del new_song['_id']
        new_song['title'] = string.capwords(song['title'])
        new_song['artist'] = string.capwords(song['artist'])
        new_list.append(new_song)
    return new_list

if __name__ == "__main__":
    playlist_t = threading.Thread(target=continuous_play)
    playlist_t.daemon = True
    playlist_t.start()
    update_t = threading.Thread(target=update_playlist)
    update_t.daemon = True
    update_t.start()
    app.run()