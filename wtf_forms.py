from django.forms import EmailField
from flask_wtf import FlaskForm, validators
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, FileField, SelectField
from wtforms.validators import DataRequired, InputRequired, Email
from wtforms.fields.html5 import EmailField


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrateForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    repeatpassword = PasswordField('Повторите пароль', validators=[DataRequired()])
    email = EmailField("Email", validators=[InputRequired("Введите свой email."), Email("Введите свой email.")])
    submit = SubmitField('Готово')


class AddTaskForm(FlaskForm):
    title = StringField('Заголовок', validators=[DataRequired()])
    cat = SelectField(label='State')
    text = TextAreaField('Текст задания')
    # picture = FileField()
    sentence = TextAreaField('Предложения', validators=[DataRequired()])
    choice = TextAreaField('Выбор ответа (разделите варианты ответа знаком //.'
                           ' \n Варианты ответа для каждого предложения пишутся с новой строки.)')
    correct = TextAreaField('Правильный ответ')
    hints = TextAreaField('Подсказки. \n '
                          'Сюда вы прикрепляете ссылки страниц,'
                          ' на которые перенаправляется пользователь в случае неправильного ответа')
    links = TextAreaField('Дополнительные файлы. (аудио, видео с youtube и др.)')
