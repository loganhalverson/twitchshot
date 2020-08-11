# Logan Halverson
# Personal, properTwitchClipBot.py
# 19 July 2020

import os
import requests
import time
from slugify import slugify

'''
    os : used to handle directories.
    requests : used to make HTTP requests and download videos.
    slugify : used to ensure valid filenames from clip titles.
'''


class Twitch():


    # Initializes on a specified game, the time range, and how many clips to return.
    def __init__(self, clip_game, clip_amount=20, clip_filter='LAST_WEEK'):
        self.clip_game = clip_game
        self.clip_amount = clip_amount
        self.clip_filter = clip_filter  # LAST_DAY, LAST_WEEK, LAST_MONTH, ALL_TIME
        self.clip_links = []
        
        self.session = requests.session()
        self.session.headers = {
            "Client-ID": "kimne78kx3ncx6brgo4mv6wki5h1ko",  # !!!!! - I don't know if this specific ID works for people that aren't me.
        }
    

    # Prints the most popular games on Twitch by viewer count.
    def printTopGames(self, limit=10):
        
        payload = [{"operationName":"BrowsePage_AllDirectories","variables":{"limit":limit,"options":{"recommendationsContext":{"platform":"web"},"requestID":"JIRA-VXP-2397","sort":"VIEWER_COUNT","tags":[]}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"78957de9388098820e222c88ec14e85aaf6cf844adf44c8319c545c75fd63203"}}}]

        r = self.session.post('https://gql.twitch.tv/gql', json=payload)
        data = r.json()[0]['data']['directoriesWithTags']['edges']

        print('The Top {0} Games'.format(limit))

        for x in range(limit):
            name = data[x]['node']['name']
            viewers = data[x]['node']['viewersCount']
            print('{0}. {1} with {2} viewers.'.format(x+1, name, viewers))

    # Given the class variables, creates a specific request and retrieves the top clip links.
    def retrieveLinks(self, cursor=""):

        if cursor == "":
            payload = [{"operationName":"ClipsCards__Game","variables":{"gameName":self.clip_game,"limit":self.clip_amount,"criteria":{"languages":[],"filter":self.clip_filter}},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0d8d0eba9fc7ef77de54a7d933998e21ad7a1274c867ec565ac14ffdce77b1f9"}}}]
        else:
            payload = [{"operationName":"ClipsCards__Game","variables":{"gameName":self.clip_game,"limit":(self.clip_amount - len(self.clip_links)),"criteria":{"languages":[],"filter":self.clip_filter}, "cursor":cursor},"extensions":{"persistedQuery":{"version":1,"sha256Hash":"0d8d0eba9fc7ef77de54a7d933998e21ad7a1274c867ec565ac14ffdce77b1f9"}}}]

        r = self.session.post("https://gql.twitch.tv/gql",json=payload)

        try:
            for clip in r.json()[0]["data"]["game"]["clips"]["edges"]:
                self.clip_links.append(clip['node']['url'])

            assert len(self.clip_links) == self.clip_amount

            return self.clip_links

        except TypeError:
            print("Reached TypeError Exception!")
            return []
        
        except AssertionError:
            print("Didn't return the amount of clips requested! Moving with cursor...")
            cursor = (r.json()[0]["data"]["game"]["clips"]["edges"])[-1]["cursor"]
            print(f"Remaining Clips to Retrieve : {self.clip_amount - len(self.clip_links)}")
            print(f"Cursor Value : {cursor}")
            self.clip_links = self.retrieveLinks(cursor)
            return self.clip_links

            
    def retrieveData(self, clip_links):
        clips = []
        for link in clip_links:
            clips.append(self.retrieveClipData(link))
        return clips

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
            url : A url linking to the clip itself on twitch.tv
            dl : A direct video download link for the highest quality available
            thumbnail : A image link to the thumbnail of the clip
            game : The game the clip is from
            author : The channel the clip is from
            views : The views the clip has
            title : The title of the clip, made by the user who clipped it
            filename : A valid OS filename generated from the clip_title.
            embed : An HTML embed link made from method t.generateEmbed().
        '''

        clip_data = {
            'url' : link,
            'dl' : data[3]['data']['clip']['videoQualities'][0]['sourceURL'],
            'thumbnail' : data[4]['data']['clip']['thumbnailURL'],
            'game' : data[0]['data']['clip']['game']['name'],
            'author' : data[0]['data']['clip']['broadcaster']['displayName'],
            'views' : data[1]['data']['clip']['viewCount'],
            'title' : data[2]['data']['clip']['title'],
        }

        clip_data['filename'] = slugify(clip_data['title'])
        clip_data['embed'] = self.generateEmbed(clip_data['url'], str('127.0.0.1'))
        clip_data['valid'] = 'true'

        return clip_data


    # Given a clip, generates the embed link that will be used on a website.
    def generateEmbed(self, clip_url, parent):  
        slug = clip_url[24:]
        template = "https://clips.twitch.tv/embed?clip={0}&parent={1}".format(slug, parent)
        return template

def validateGame(game):

    headers = {
        'Client-ID' : 'kimne78kx3ncx6brgo4mv6wki5h1ko',
        'Accept' : 'application/vnd.twitchtv.v5+json'
    }

    r = requests.get('https://api.twitch.tv/kraken/clips/top', headers=headers, params={'game' : game})

    if r.json()['clips'] == []:
        return False  # Invalid game.
    else:
        return True