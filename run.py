from flask import Flask, render_template
from flask import redirect, url_for, request

from modifier import blob_to_cv_img

app = Flask(__name__)
app.config['DEBUG'] = True

@app.route('/')
def home():
    return redirect(url_for('overview'))


@app.route('/overview')
def overview():
    return render_template('overview.html')


@app.route('/datasets')
def datasets():
    return render_template('datasets.html')


@app.route('/datasets/new')
def datasets_new():
    return render_template('datasets_new.html')


@app.route('/clasificators')
def clasificators():
    return render_template('clasificators.html')

@app.route('/foo', methods=['GET', 'POST'])
def up():
    print(request)
    print(request.data)
    blob_to_cv_img(request.data)
    return "foo"


if __name__ == '__main__':
    app.run()
