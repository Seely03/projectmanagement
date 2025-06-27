from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, IntegerField
from wtforms.validators import DataRequired, Optional, Length, NumberRange

class ProjectForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    status = SelectField('Status', choices=[
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Completed', 'Completed')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ], validators=[DataRequired()])
    start_date = DateField('Start Date', validators=[DataRequired()])
    end_date = DateField('End Date', validators=[Optional()])

class TaskForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=1, max=100)])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    status = SelectField('Status', choices=[
        ('To Do', 'To Do'),
        ('In Progress', 'In Progress'),
        ('Done', 'Done')
    ], validators=[DataRequired()])
    priority = SelectField('Priority', choices=[
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    ], validators=[DataRequired()])
    effort_points = SelectField('Effort Points', choices=[
        (1, '1 - Very Small'),
        (2, '2 - Small'),
        (3, '3 - Medium'),
        (5, '5 - Large'),
        (8, '8 - Very Large'),
        (13, '13 - Extra Large'),
        (21, '21 - Epic')
    ], coerce=int, validators=[DataRequired()])
    user_id = SelectField('Assignee', coerce=int, validators=[Optional()]) 