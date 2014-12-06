import urllib
import urllib2
import json

import soundcloud

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






#	MAIN 	#
secrets = getSecrets()

getSoundCloudData(secrets[0], secrets[1], secrets[2])
DownloadLikeList()






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
		DownloadMP3FromURL(like.URL, like.title)


def DownloadMP3FromURL(url, name):
	#Encode URL to be passed as argument in URL
	encodedURL = urllib.quote_plus(url)

	#Combine URLs to create download URL
	downloadURL = CONST_SOUND_DL_URL + encodedURL

	print("Preparing Stream...")

	#Get JSON response from download URL
	try:
		response = urllib2.urlopen(downloadURL)
	except Exception as e:
		print(e)

	print("Stream Ready")

	#Parse JSON
	j = json.loads(response.read())
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

	print("Download Complete\n")