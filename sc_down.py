from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3
import mutagen
import urllib
import urllib2
import json
import string
import soundcloud
import simplejson
import os

#	CONSTANTS	#

CONST_SOUND_DL_URL = "http://streampocket.com/json2?stream="


#	GLOBAL VAR	#

likeList = []


#	 CLASSES	#

class Sound(object):
	def __init__(self, title, user, url, artworkURL):
		self.title = title
		self.user = user
		self.URL = url
		self.artworkURL = artworkURL


#	FUNCTIONS	#

def getSecrets():
	f = open("secrets.json")
	secrets = json.load( f )

	scLikesURL = secrets["SC_URL"]
	clientID = secrets["CLIENT_ID"]
	clientSecret = secrets["CLIENT_SECRET"]

	return (scLikesURL, clientID, clientSecret)


def getSoundCloudData(likesURL, clientID, clientSecret):
	print("Gathering SoundCloud Likes...")

	#Set Up Client
	client = soundcloud.Client(client_id=clientID)

	#Resolve User from Profile URL
	userName = client.get('/resolve', url=likesURL)

	likes = client.get('/users/' + str(userName.id) + '/favorites')
	for like in likes:
		#Get Sound MetaData
		name = like.title
		url = like.permalink_url
		artwork = like.artwork_url

		#Get Username of Uploader
		userID = like.user_id
		uploader = client.get("/users/" + str(userID))
		user = uploader.username

		#Ask user to download
		varDownload = AskToDownload(like.title.encode('utf-8', 'ignore'))
		download = False
		if varDownload[1]:
			break
		elif varDownload[0]:
			#Add to likeList
			likeList.append(Sound(name, user, url, artwork))

	print("\nDone Gathering Likes")
	printLikeList()


def printLikeList():
	if len(likeList) == 0:
		print "LikeList is empty\n"
	for like in likeList:
		titleTemp = like.title
		userTemp = like.user
		print(titleTemp.encode('utf-8', 'ignore'))
		print("\tBy: " + userTemp.encode('utf-8', 'ignore'))
		print("\tURL: " + like.URL)
		if(like.artworkURL is not None):
			print("\tImage URL: " + like.artworkURL)
		print ""


def AskToDownload(title):
	goodResponse = False
	download = False
	done = False
	while not goodResponse:
		varResponse = raw_input("Download " + title + "? (y/n/done) ")
		if varResponse == 'y':
			download = True
			done = False
			goodResponse = True
		elif varResponse == 'n':
			download = False
			done = False
			goodResponse = True
		elif varResponse == 'done':
			download = False
			done = True
			goodResponse = True
		else:
			print "Response not recognized, input 'y' or 'n' or 'done'\n" 
	return (download, done)


def DownloadLikeList():
	for like in likeList:
		DownloadMP3FromURL(like)
	# Remove temp.jpg
	os.remove("temp.jpg")


def DownloadMP3FromURL(like):

	url = like.URL
	name = cleanFileName(like.title)

	#Encode URL to be passed as argument in URL
	encodedURL = urllib.quote_plus(url)

	#Combine URLs to create download URL
	downloadURL = CONST_SOUND_DL_URL + encodedURL

	print(like.title.encode('utf-8', 'ignore'))

	print("Preparing Stream...")

	numTried = 0;
	failed = True;
	#Get JSON response from download URL
	try:
		while(numTried < 5):
			response = urllib2.urlopen(downloadURL)
			if(response.info()["Content-Length"] != "0"):
				failed = False;
				print("Success")
				break;
			print("StreamPocket Failed, retrying...")
			numTried += 1;
	except Exception as e:
		print(e)

	if(failed):
		print("StreamPocket Failed - Not Downloading")

	print("Stream Ready")

	#Parse JSON
	j = simplejson.loads(response.read())
	soundURL = j["recorded"]

	#Open Sound from URL
	try:
		data = urllib2.urlopen(soundURL)
	except Exception as e:
		print(e)

	print("Beginning Download...")

	#Prepare Filename
	fileName = name.encode('utf-8', 'ignore')
	fileName = fileName + ".mp3"

	#Write sound to file
	songFile = open(fileName, "wb")
	songFile.write(data.read())
	songFile.close()

	print("Download Complete")

	print("Updating MP3 File\n")

	updateMP3Info(fileName, like)


def updateMP3Info(fileName, like):

	try:
		meta = EasyID3(fileName)
	except error:
		meta = mutagen.File(fileName, easy=True)
		meta.add_tags()

	meta['title'] = like.title
	meta['artist'] = like.user
	meta.save()

	if(like.artworkURL is not None):
		addArtwork(fileName, like)
	else:
		print("Artwork Skipped")

def addArtwork(fileName, like):
	imageURL = like.artworkURL

	largerImageURL = getLargerImage(imageURL)

	urllib.urlretrieve(largerImageURL, "temp.jpg")

	audio = MP3(fileName, ID3=ID3)

	# add ID3 tag if it doesn't exist
	try:
	    audio.add_tags()
	except error:
	    pass

	audio.tags.add(
	    APIC(
	        encoding=3, # 3 is for utf-8
	        mime='image/jpeg', # image/jpeg or image/png
	        type=3, # 3 is for the cover image
	        desc=u'Cover',
	        data=open('temp.jpg', 'rb').read()
	    )
	)
	audio.save()

def getLargerImage(imgURL):
	if imgURL.endswith("large.jpg"):
		imgURL = imgURL[:-9]
		imgURL += "t500x500.jpg"
	else:
		print("\n\n\nUnknown Image URL suffix - Check\n\n\n")
	return imgURL



def cleanFileName(fileName):
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	newFileName = ''.join(c for c in fileName if c in valid_chars)
	return newFileName


#	MAIN 	#
secrets = getSecrets()

getSoundCloudData(secrets[0], secrets[1], secrets[2])
DownloadLikeList()