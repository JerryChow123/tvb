from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, \
    TextAreaField, FileField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'),
                             validators=[Length(min=0, max=140)])
    icon = FileField(_l("Icon") + " (jpg, png, bmp)")
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError(_('Please use a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('Say something'), validators=[DataRequired()])
    submit = SubmitField(_l('Submit'))


class ForumPostForm(FlaskForm):
    title = StringField(_l('Topic'))
    body = TextAreaField(_l('Content'), validators=[DataRequired()])
    submit = SubmitField(_l('Create Post'))


class ForumReplyForm(FlaskForm):
    body = TextAreaField(_l('Content'), validators=[DataRequired()])
    submit = SubmitField(_l('Reply'))