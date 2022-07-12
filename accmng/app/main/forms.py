from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SelectField, SubmitField, DateField, FloatField
from wtforms.validators import DataRequired, Length, Email, Regexp 
from wtforms import ValidationError


class NameForm(FlaskForm):
    name = StringField('What is your name?', validators=[DataRequired()])
    submit = SubmitField('Submit')


class DocumentForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    timestamp = DateField('Created', [DataRequired()])
    sum = FloatField('Sum', validators=[DataRequired()])
    body = TextAreaField('Content', validators=[DataRequired()],render_kw={'rows':'6'})
    confirmation_status = SelectField('Confirmation status',
                                        validators=[DataRequired()],
                                        choices=[('undefined','Undefined'),
                                                 ('confirmed', 'Confirmed'),
                                                 ('rejected', 'Rejected')])
    submit = SubmitField('Submit')
