from flask_wtf import FlaskForm
from wtforms import BooleanField, HiddenField, SelectField
from wtforms.fields import StringField, SubmitField
from wtforms.validators import InputRequired, Length

#Klasse CreateTodoForm erbt von FlaskForm
class CreateTodoForm(FlaskForm):  # (1.)
    description = StringField(validators=[InputRequired(), Length(min=5)])  # (2.)
    submit = SubmitField('Create')

   
class TodoForm(FlaskForm):  # (1.)
    method = HiddenField()  # (2.)
    id = HiddenField()
    complete = BooleanField()
    description = StringField(validators=[InputRequired()])
    list_id = SelectField(coerce=int, choices=[], validate_choice=False)  # (3.)
    submit = SubmitField('Update')
