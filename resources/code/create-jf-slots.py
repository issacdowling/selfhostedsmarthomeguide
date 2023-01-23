import requests
import json
import re

# Define Jellyfin Server Info
jellyfinurl = ""
jellyfinauth = ""
userId = ""
itemId = ""
headers = {"X-Emby-Token": jellyfinauth,}

# Function for getting list of artists
def getAlbumArtists():
  albumArtistsInfo = []
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Artists/AlbumArtists", headers = headers)
  receivedJson = json.loads(get.text)
  # Opens "Items" key in JSON file
  albumArtists = receivedJson["Items"]
  for albumArtist in albumArtists:
    print("Adding albumartist: " + str(albumArtist["Name"]))
    # For each item (one item is all the info for a specific Album Artist),
    # add the value in the "Name" and "Id" keys to a dict
    albumArtistsInfo.append({"Name" : albumArtist["Name"], "Id" : albumArtist["Id"]})
  return albumArtistsInfo

# Function for getting list of albums
def getAlbums(userid):
  albumsInfo = []
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&IncludeItemTypes=MusicAlbum", headers = headers)
  receivedJson = json.loads(get.text)
  # Opens "Items" key in JSON file
  albums = receivedJson["Items"]
  for album in albums:
    print("Adding album: " + album["Name"])
    # For each item (one item is all the info for a specific Album),
    # add the value in the "Name" and "Id" keys to a dict
    albumsInfo.append({"Name" : album["Name"], "Id" : album["Id"], "AlbumArtist" : album["AlbumArtist"]})
  return albumsInfo

# Function for getting list of songs
def getSongs(userid):
  songsInfo = []
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&IncludeItemTypes=Audio", headers = headers)
  receivedJson = json.loads(get.text)
  # Opens "Items" key in JSON file
  songs = receivedJson["Items"]
  for song in songs:
    print("Adding song: " + song["Name"])
    # For each item (one item is all the info for a specific Album Artist),
    # add the value in the "Name" and "Id" keys to a list
    songsInfo.append({"Name" : song["Name"], "Id" : song["Id"], "AlbumArtist" : song["AlbumArtist"]})
  return songsInfo

# Function for getting list of playlists
def getPlaylists(userid):
  playlistsInfo = []
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&IncludeItemTypes=Playlist", headers = headers)
  receivedJson = json.loads(get.text)
  # Opens "Items" key in JSON file
  playlists = receivedJson["Items"]
  for playlist in playlists:
    print("Adding playlist: " + playlist["Name"])
    # For each item (one item is all the info for a specific Album Artist),
    # add the value in the "Name" and "Id" keys to a list
    playlistsInfo.append({"Name" : playlist["Name"], "Id" : playlist["Id"]})
  return playlistsInfo

# Function for getting list of favourited songs
def getFavouriteSongs(userid):
  favouriteSongsInfo = []
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&Filters=IsFavorite&IncludeItemTypes=Audio", headers = headers)
  receivedJson = json.loads(get.text)
  # Opens "Items" key in JSON file
  favouriteSongs = receivedJson["Items"]
  for favouriteSong in favouriteSongs:
    print("Adding favourite: " + favouriteSong["Name"])
    # For each item (one item is all the info for a specific song),
    # add the value in the "Name" and "Id" keys to a list
    favouriteSongsInfo.append({"Name" : favouriteSong["Name"], "Id" : favouriteSong["Id"]})
  return favouriteSongsInfo

# Function for getting list of songs within something (e.g, artist, album)
def getSongsWithin(userid,itemid):
  songsInfo = []
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items?Recursive=true&IncludeItemTypes=Audio&parentId=" + itemid, headers = headers)
  receivedJson = json.loads(get.text)
  # Opens "Items" key in JSON file
  songs = receivedJson["Items"]
  for song in songs:
    # For each item (one item is all the info for a specific Album Artist),
    # add the value in the "Name" and "Id" keys to a list
    songsInfo.append({"Name" : song["Name"], "Id" : song["Id"]})
  return songsInfo

# Function for getting details associated with song ID
def getSongDetails(userid,itemid):
  # Send get request to AlbumArtists API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Users/"+userid+"/Items/" + itemid, headers = headers)
  song = json.loads(get.text)
  # Remove Extraneous Info From Date Field
  premiere_date = song["PremiereDate"].split("-")
  premiere_date[2] = songInfo[:2]
  # add the values to a list
  songInfo = {"Name" : song["Name"], "AlbumArtist" : song["AlbumArtist"], "Album" : song["Album"], "PremiereDate" : premiere_date, "IsFavourite" : song["UserData"]["IsFavorite"], "MainGenre" : song["GenreItems"][0]["Name"], "PlayCount" : song["UserData"]["PlayCount"], "Codec" : song["MediaStreams"][0]["Codec"], "BitRate" : song["MediaStreams"][0]["BitRate"], "BitDepth" : song["MediaStreams"][0]["BitDepth"], "Id" : song["Id"], "PrimaryAlbumImageTag" : song["AlbumPrimaryImageTag"]}
  return songInfo

# Function for downloading media
def getItemDownload(itemid):
  # Send get request to Item Download API endpoint on the Jellyfin server with authentication
  get = requests.get(jellyfinurl+"/Items/"+itemid+"/Download", headers = headers)
  # If request successful, save file
  if get.status_code == 200:
    currentSong = open("currentMedia", "wb")
    currentSong.write(get.content)
    currentSong.close()

# Function for making Rhasspy-compatible slots for music-related media
def genMusicSlots():
  # Save albumartists, albums, playlists, and songs to variables
  print("Saving album artists")
  albumArtistsList = getAlbumArtists()
  print("Saving albums")
  albumsList = getAlbums(userId)
  print("Saving songs")
  songsList = getSongs(userId)
  print("Saving playlists")
  playlistsList = getPlaylists(userId)

  # Create file with ($albumartistName):($albumartistId) with each on new line
  print("Creating albumartists file")
  with open("albumartists", "w") as albumArtists:
    for pos in range(len(albumArtistsList)):
      albumArtists.write("(" + re.sub('[^A-Za-z0-9 ]+', '', albumArtistsList[pos]["Name"]) + "):" + albumArtistsList[pos]["Id"] + "\n")

  # Create file with ($albumName):($albumId) with each on new line
  print("Creating albums file")
  with open("albums", "w") as albums:
    for pos in range(len(albumsList)):
      albums.write("(" + re.sub('[^A-Za-z0-9 ]+', '', albumsList[pos]["Name"]) + " [by " + re.sub('[^A-Za-z0-9 ]+', '', albumsList[pos]["AlbumArtist"]) + "]):" + albumsList[pos]["Id"] + "\n") 

  # Create file with ($songName):($songId) with each on new line
  print("Creating songs file")
  with open("songs", "w") as songs:
    for pos in range(len(songsList)):
      songs.write("(" + re.sub('[^A-Za-z0-9 ]+', '', songsList[pos]["Name"]) + " [by " + re.sub('[^A-Za-z0-9 ]+', '', songsList[pos]["AlbumArtist"]) + "]):" + songsList[pos]["Id"] + "\n") 

  # Create file with ($playlistName):($playlistID) with each on new line (or "noPlaylists" if they have no playlists)
  print("Creating playlists file")
  with open("playlists", "w") as playlists:
    if playlistsList:
      for pos in range(len(playlistsList)):
        playlists.write("(" + re.sub('[^A-Za-z0-9 ]+', '', playlistsList[pos]["Name"]) + ")" + ":" + playlistsList[pos]["Id"] + "\n")
    else:
      playlists.write("noPlaylists")

genMusicSlots()