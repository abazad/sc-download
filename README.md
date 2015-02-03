sc-download
===========

Python SoundCloud downloading script

This script allows the user to automatically download a sound from SoundCloud given a user profile.  The script gathers a list of sounds from the user's like list.  In order to use the script, a file named *secrets.json* must be generated.
All selected songs are downloaded have the title, artist and album artwork mp3 tags updated.  The mp3 title is set to the sound name, the artist tag is set to the sound's uploader, and the artwork is set to the artwork found on SoundCloud.

#### Generating *secrets.json*

In order to generate the *secrets.json* file, you need to gather a few pieces of information from SoundCloud

```
{
	"FILENAME": "secrets.json",
	"SC_URL": "https://soundcloud.com/mike-genovese-1",
	"CLIENT_ID": "957uh0471pei2d104ptnz4e4h1p06731",
	"CLIENT_SECRET": "10hy0v1e9p0676ptuvucyt0as5e6bw9z"
}
```
*SC_URL*: This is a URL to the user profile in which the sounds should be gathered

*CLIENT_ID*: This is the ID provided by SoundCloud when registering an app in their [Developer Portal] (https://developers.soundcloud.com/)

*CLIENT_SECRET*: This is the secret key provided by SoundCloud when registering an app in their [Developer Portal] (https://developers.soundcloud.com/)
