# Logan Halverson
# Personal, videoEditor.py
# 05 August 2020

import os
import requests
import time
import shutil
import random

from slugify import slugify
import moviepy.editor as mpy

class Video():

    def __init__(self, render_name):
        
        self.video_filenames = []
        self.video_file_clips = []
        self.render_name = render_name
        self.id = str(int(999999999999 * random.random()))
        
        # Makes a randomized folder name and works within it for each user.
        
        if not os.path.basename(os.getcwd()) == 'video':
           os.chdir(os.path.dirname(os.path.abspath(__file__)) + '\\video')

        os.mkdir(self.id)
        os.chdir(self.id)

    # Downloads the video from the links, saves as valid filename.
    def downloadVideo(self, links):

        for fname, dlink in links.items():

            filename = fname + '.mp4'
            self.video_filenames.append(filename)
            with open(filename, 'wb') as f:
                video = requests.get(dlink)
                f.write(video.content)
                self.video_file_clips.append(mpy.VideoFileClip(filename))

    def compositeVideo(self, links):

        # Downloads the video from the links, saves as valid filename.
        for fname, dlink in links.items():
            
            filename = fname + '.mp4'
            self.video_filenames.append(filename)

            with open(filename, 'wb') as f:
                video = requests.get(dlink)
                f.write(video.content)
                self.video_file_clips.append(mpy.VideoFileClip(filename))

        # Concatenates the videos.
        final_clip = mpy.concatenate_videoclips(self.video_file_clips, method="compose")
        self.render_name = slugify(self.render_name)
        self.render_name += '.mp4'
        final_clip.write_videofile(self.render_name)


    def uploadVideo(self):

        # DELETE USER INSTANCE OF VIDEO FOLDER
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + '\\video')

        # # This has to be done not during the render process, but some time after with
        # # a cleanup function. It can't modify files in use.
        # shutil.rmtree(self.id)
        
        # DROPBOX/GOOGLE DRIVE upload rendered video, return download link to FLASK app
        return "you're mom gay"

# links = {
#     'superman64' : 'downloadlink1',
#     'mariogowoo' : 'downloadlink3',
#     'heeohooaa' : 'downloadlink2'
# }
