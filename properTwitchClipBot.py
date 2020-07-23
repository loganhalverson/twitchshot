# Logan Halverson
# Personal, properTwitchClipBot.py
# 19 July 2020

import os
import requests
from slugify import slugify
from PIL import Image
import moviepy.editor as mpy

'''
    os : used to handle directories.
    requests : used to make HTTP requests and download videos.
    slugify : used to ensure valid filenames from clip titles.
    image : used to handle previewing clips.
    mpy : used to work with video files
'''

class Twitch():


    # Initializes on a specified game, the time range, and how many clips to return.
    def __init__(self, clip_game, clip_amount=20, clip_filter='LAST_WEEK'):
        self.clip_game = clip_game
        self.clip_amount = clip_amount
        self.clip_filter = clip_filter
        
        self.session = requests.session()
        self.session.headers = {
            "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko"  # !!!!! - I don't know if this specific ID works for people that aren't me.
        }
    

    # Given the class variables, creates a specific request and retrieves the top clip links.
    def retrieveClipLinks(self):

        clip_links = []

        payload = [{"operationName":"ClipsCards__Game","variables":{"gameName":self.clip_game,"limit":self.clip_amount,"criteria":{"languages":[],"filter":self.clip_filter}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0d8d0eba9fc7ef77de54a7d933998e21ad7a1274c867ec565ac14ffdce77b1f9"}}}]

        r = self.session.post("https://gql.twitch.tv/gql",json=payload)

        for clip in r.json()[0]["data"]["game"]["clips"]["edges"]:
            clip_links.append(clip['node']['url'])

        return clip_links


    # Given the link to a clip, retrieves all useful data from it.
    def retrieveClipData(self, link):

        # The slug is the auto-generated clip name, found in the url. The HTTP request
        # works off of that, so it is retrieved from the url and stored as String slug.
        slug = link[24:]
        
        # This is the headers the HTTP request is sent with.
        payload = [ {"operationName":"ClipsView","variables":{"slug":slug},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"4480c1dcc2494a17bb6ef64b94a5213a956afb8a45fe314c66b0d04079a93a8f"}}},{"operationName":"ClipsViewCount","variables":{"slug":slug},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"00209f168e946123d3b911544a57be26391306685e6cae80edf75cdcf55bd979"}}},{"operationName":"ClipsTitle","variables":{"slug":slug},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"f6cca7f2fdfbfc2cecea0c88452500dae569191e58a265f97711f8f2a838f5b4"}}},{"operationName":"VideoAccessToken_Clip","variables":{"slug":slug},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"9bfcc0177bffc730bd5a5a89005869d2773480cf1738c592143b5173634b7d15"}}}, {"operationName":"WatchLivePrompt","variables":{"slug":slug},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"d65226c25ec2335f7550351c7041f4080a2531f4e330375fef45c7a00e4f4016"}}}]

        r = self.session.post('https://gql.twitch.tv/gql', json=payload)
        data = r.json()

        '''
        CLIP_DATA VALUES:

            clip_url : A url linking to the clip itself on twitch.tv
            clip_dl : A direct video download link for the highest quality available
            clip_thumbnail : A image link to the thumbnail of the clip
            clip_game : The game the clip is from
            clip_author : The channel the clip is from
            clip_views : The views the clip has
            clip_title : The title of the clip, made by the user who clipped it
            clip_filename : A valid OS filename generated from the clip_title.

        '''

        clip_data = {
            'clip_url' : link,
            'clip_dl' : data[3]['data']['clip']['videoQualities'][0]['sourceURL'],
            'clip_thumbnail' : data[4]['data']['clip']['thumbnailURL'],
            'clip_game' : data[0]['data']['clip']['game']['name'],
            'clip_author' : data[0]['data']['clip']['broadcaster']['displayName'],
            'clip_views' : data[1]['data']['clip']['viewCount'],
            'clip_title' : data[2]['data']['clip']['title'],
        }

        clip_data['clip_filename'] = slugify(clip_data['clip_title'])

        return clip_data


    # Packages all retrieved clips into a list and returns it.
    def retrieveClips(self):
        clip_links = self.retrieveClipLinks()
        clips = []

        for link in clip_links:
            clips.append(self.retrieveClipData(link))

        return clips


    # Overriding print() to print all data about a clip given a clip dict.
    def print(self, clip_data):
        print('URL : ' + clip_data['clip_url'])
        print('DOWNLOAD : ' + clip_data['clip_dl'])
        print('THUMBNAIL : ' + clip_data['clip_thumbnail'])
        print('GAME : ' + clip_data['clip_game'])
        print('TITLE : ' + clip_data['clip_title'])
        print('FILENAME : ' + clip_data['clip_filename'])
        print('AUTHOR : ' + clip_data['clip_author'])
        print('VIEWS : ' + str(clip_data['clip_views']))
        print()


    # This method goes through a list of clips and shows the user the thumbnail of each.
    # It then removes any clip not approved by the user from the list.
    # This method is also **godawful** from a user persepective. This will be changed once we
    # reach the GUI implementation stage, but as of now its just honestly atrocious.
    def validateClips(self, clips):
        
        print("We'll be reviewing the clips by looking at their thumbnail.")
        print("If the clip looks valid, type OK.")
        valid_clips = []

        for clip in clips:

            filename = clip['clip_filename'] + '.jpg'
            target = os.path.join(os.getcwd(), filename)

            # print('Filename : {0}\nTarget : {1}'.format(filename, target))

            with open(target, 'wb') as f:
                r = requests.get(clip['clip_thumbnail'])
                f.write(r.content)
                
            im = Image.open(filename)
            im.show()

            answer = input('Approve clip? ')
            if answer.lower() == 'ok': 
                valid_clips.append(clip)

            os.remove(filename)

        return valid_clips

    # Given a clip, generates the embed link that will be used on a website.
    def generateEmbed(self, clip, parent, height=378, width=620):  
        slug = clip['clip_url'][24:]
        template = '<iframe src="https://clips.twitch.tv/embed?clip={0}&parent={1}" frameborder="0" allowfullscreen="true" scrolling="no" height="{2}" width="{3}"></iframe>'.format(slug, parent, height, width)
        return template


class Video():

    def downloadClips(self, clips):

        dirname = os.path.dirname(__file__)

        for clip in clips:
            directory = (os.path.join(dirname, clip['clip_filename'] + ".mp4"))

            with open(directory, 'wb') as f:
                r = requests.get(clip['clip_dl'])
                f.write(r.content)
                print('Successfully saved ' + clip['clip_filename'])


t = Twitch('valorant', 5, 'LAST_WEEK') 
v = Video()

# All necessary steps so far are taken using these three methods.
clips = t.retrieveClips()
#clips = t.validateClips(clips)
v.downloadClips(clips)

