import flask
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextField
from wtforms.validators import DataRequired
import sqlite3
import os
from PIL import Image
from io import BytesIO


def deform_page(number):
    conn = sqlite3.connect('static/database/data.db')
    cursor = conn.cursor()
    req = f"SELECT * FROM pages WHERE id = {number}"
    cursor.execute(req)
    data = cursor.fetchall()[0]
    deformed = [data[0], data[1], [[i.split('&')[0], i.split('&')[1]] for i in data[2].split('|')], data[3]]
    return deformed

def deform_pages():
    conn = sqlite3.connect('static/database/data.db')
    cursor = conn.cursor()
    req = "SELECT * FROM pages"
    cursor.execute(req)
    data = cursor.fetchall()
    deformed = [[j[0], j[1], [{i.split('&')[0]: i.split('&')[1]} for i in j[2].split('|')]] for j in data]
    return deformed

def add_page(title, links, username):
    conn = sqlite3.connect('static/database/data.db')
    cursor = conn.cursor()
    req = f"INSERT INTO pages VALUES ({pages() + 1}, '{title}', '{links}', '{username}');"
    cursor.execute(req)
    cursor.fetchall()
    conn.commit()

def pages():
    conn = sqlite3.connect('static/database/data.db')
    cursor = conn.cursor()
    req = "SELECT MAX(id) FROM pages"
    cursor.execute(req)
    data = cursor.fetchall()[0][0]
    if data is None:
        data = -1
    return data

def deform_ads():
    conn = sqlite3.connect('static/database/data.db')
    cursor = conn.cursor()
    req = "SELECT * FROM ads"
    cursor.execute(req)
    data = cursor.fetchall()
    deformed = [{'img': i[2], 'link': i[1]} for i in data]
    return deformed

def editor(key):
    conn = sqlite3.connect('static/database/data.db')
    cursor = conn.cursor()
    req = f"SELECT username FROM editors WHERE pkey='{key}'"
    cursor.execute(req)
    data = cursor.fetchall()
    return data[0][0] if data != [] else False

class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    about_me = TextField('Резюме (ссылка)', validators=[DataRequired()])
    mail = StringField('e-mail', validators=[DataRequired()])
    agree = BooleanField('Даю согласие на всё', validators=[DataRequired()])
    submit = SubmitField('Зарегестрироваться')

app = flask.Flask(__name__)
app.config['SECRET_KEY'] = 'You_choose_the_wrong_house_fool'

@app.route('/')
def news():
    infos = [{'link': '/page/' + str(i[0]), 'title': i[1]} for i in deform_pages()][::-1]
    ads = deform_ads()
    return flask.render_template('index.html', ads=ads, infos=infos, page_title='global blog')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = LoginForm()
    if form.validate_on_submit():
        print('\n' * 5)
        for i in form.data.keys():
            if i == 'csrf_token':
                break
            print(f'{i}: {form.data[i]}')
        print('\n' * 5)
        return flask.redirect('/success/' + form.data['username'])
    return flask.render_template('registration.html', form=form, page_title='регистрация')

@app.route('/info')
def info():
    return flask.render_template('info.html', page_title='info')

@app.route('/success/<username>')
def success(username):
    return flask.render_template('success.html', username=username, page_title='ждите решения!')

@app.route('/enter', methods=['GET', 'POST'])
def enter():
    if flask.request.method == 'POST':
        username = editor(flask.request.form['key'])
        if username:
            file = flask.request.files['image']
            if file.filename.split('.')[-1] == 'jpg':
                img = Image.open(BytesIO(file.read()))
                if img.size == (1200, 2400):
                    img.save(f'static/img/{pages() + 1}.jpg')
                    links = ''
                    for i in range(1, 6):
                        title, link = flask.request.form[f't{i}'], flask.request.form[f'l{i}']
                        if title != '' and link != '':
                            links += f"{title}&{link}|"
                    if links != '':
                        links = links[:-1]
                    add_page(flask.request.form['title'], links, username)
                    return flask.redirect('/')
    return flask.render_template('enter.html', page_title='Создать статью')

@app.route('/page/<number>')
def page(number):
    data = deform_page(number)
    add = [{'text': i[0], 'link': i[1]} for i in data[2]]
    username = data[3]
    return flask.render_template('content.html', number=number, add=add, username=username, page_title=data[1])

if __name__ == '__main__':
    app.run(host='0.0.0.0')
