from flask import Flask
from flask import redirect, render_template
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField
from wtforms.validators import  Required


app = Flask(__name__)
app.config['SECRET_KEY'] = 'xiaochaoqunkasdf'


class FileForm(FlaskForm):
    upd = FileField('上传')


@app.route('/', methods=['GET', 'POST'])
def index():
    form = FileForm()
    return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run(debug=True)