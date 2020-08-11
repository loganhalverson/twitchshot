import os

from flask_wtf import FlaskForm
from wtforms import (
                      StringField,
                      SelectField,
                      IntegerField,
                      SubmitField,
                      PasswordField
                    )
from wtforms.validators import DataRequired, NumberRange, Length


class TwitchForm(FlaskForm):

  csrf_token = os.urandom(32)  # CSRF Token. It has to be declared here and referenced in the HTML. 
  game_name = StringField('Game Name', validators=[DataRequired()])
  time_range = SelectField('Time Range', choices=[('LAST_DAY', 'Last Day'), ('LAST_WEEK', 'Last Week'), ('LAST_MONTH', 'Last Month'), ('ALL_TIME', 'All Time')])
  clip_amount = IntegerField('Clip Amount (1-50)', [NumberRange(min=1, max=50, message='Please enter a number between one and fifty.')]) 
  submit = SubmitField('Submit')

# class TestingForm(FlaskForm):

#   csrf_token = os.urandom(32)
#   clip_index = IntegerField('Clip Number', [NumberRange(min=0, message='Please enter a valid index.')])
#   submit = SubmitField('Submit')

class ChoiceForm(FlaskForm):

  csrf_token = os.urandom(32)
  approve = SubmitField('Approve')
  reject = SubmitField('Reject')
  submit = SubmitField('Submit')

class RenderForm(FlaskForm):

  csrf_token = os.urandom(32)
  name = StringField('Final Video Name', validators=[DataRequired(), Length(min=1, max=100, message='Too long of a filename. Does it really need to be that long?')])
  submit = SubmitField('Start Rendering')