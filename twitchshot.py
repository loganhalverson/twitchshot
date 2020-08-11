import os
from threading import Thread
import concurrent.futures

from flask import Flask, render_template, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect

from twitchClips import Twitch, validateGame
from videoEditor import Video
from tsForms import TwitchForm, ChoiceForm, RenderForm

app = Flask(__name__)
csrf = CSRFProtect(app)
app.config.from_pyfile('tsConfig.py')


@app.route('/', methods=['POST', 'GET'])
def index():

    session.clear()
    session['finished'] = False
    form = TwitchForm()

    # The form is properly filled out.
    if form.validate_on_submit():
        game = form.game_name.data
        time = form.time_range.data
        amount = str(form.clip_amount.data)

        # checks if game name is valid
        if validateGame(game):
            return redirect(url_for('clips', game=game, time=time, amount=amount, clip_index=0))
        else:
            return redirect(url_for('error'))

    else:
        return render_template('tsIndex.html', form=form)


@app.route('/clips/<game>/<time>/<amount>/<clip_index>', methods=['POST', 'GET'])
def clips(game, time, amount, clip_index):

    # This means it is the first time the user reaches the page.
    if 'clips' not in session:

        twt = Twitch(game, int(amount), time)

        with concurrent.futures.ThreadPoolExecutor() as executor:
            clips = list(executor.map(twt.retrieveClipData, twt.retrieveLinks()))

        session['clips'] = clips

        return redirect(url_for('clips', game=game, time=time, amount=amount, clip_index=str(0)))

    # One of the three choice buttons was pressed.
    if request.method == 'POST':
        
        clip_index = int(clip_index)

        if(request.values.has_key('approve')):
           return redirect(validate('true', game, time, amount, clip_index))

        if(request.values.has_key('reject')):
            return redirect(validate('false', game, time, amount, clip_index))
        
        if(request.values.has_key('submit')):
            approved_clips = {}
            
            # Creates a key:value pair of valid-filename:download-link.
            for clip in session['clips']:
                if clip['valid'] == 'true':
                    approved_clips[clip['filename']] = clip['dl']
            
            session['downloads'] = approved_clips
            return redirect(url_for('render'))

    form = ChoiceForm()
    return render_template('tsClips.html', game=game, clips=session['clips'], display_clip=session['clips'][int(clip_index)], current_index=str(clip_index), form=form)


@app.route('/render', methods=['POST', 'GET'])
def render():
    
    form = RenderForm()

    # get confirmation from user to start -- therefore a post request to this page
    if form.validate_on_submit():

        v = Video(form.name.data)
        # v.compositeVideo(session['downloads'])
        session['download_link'] = v.uploadVideo()
        session['finished'] = True

        return redirect(url_for('finished'))

    else:
        
        return render_template('tsRender.html', form=form)

@app.route('/finished')
def finished():

    return render_template('tsFinished.html', download=session['download_link'])

@app.route('/about/')
def about():

    return '<h1>oh hey this is an about page</h1>'

@app.route('/error/')
def error():
    return f'<h1>ya blew it</h1>'


# Handles approval/rejection of clips.
def validate(boolean, game, time, amount, clip_index):

    temp_storage = session['clips']  # Sets the sesssion to a temporary variable to ensure valid changes.

    temp_storage[clip_index]['valid'] = boolean  # Sets the clip to the given 'boolean'.

    if((clip_index + 1) < (len(temp_storage))):  # Moves the user to the next clip if there is one, restarts the index if there isn't.
        session['clips'] = temp_storage
        return (url_for('clips', game=game, time=time, amount=amount, clip_index=clip_index+1))
    else:
        session['clips'] = temp_storage
        return (url_for('clips', game=game, time=time, amount=amount, clip_index=0))


if __name__ == "__main__":
    app.run()
