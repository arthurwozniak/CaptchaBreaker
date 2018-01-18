from flask import Flask, render_template
from flask import redirect, url_for, request

import flask

import modifier

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
    operations = ["grayscale", "treshold", "filter", "unmask"]
    result = {}

    print(request.json)
    print(request.json.keys())
    encoded_image = request.json.get("image")

    last_img = modifier.blob_to_img(encoded_image)
    todo = request.json.get("operations")
    print(todo)

    if "grayscale" in todo.keys():
        last_img = modifier.img_grayscale(last_img)
        result["grayscale"] = modifier.img_to_base64(last_img)

    if "filter" in todo.keys():
        last_img = modifier.img_filter(last_img, todo["filter"]["lower"], todo["filter"]["upper"])
        result["filter"] = modifier.img_to_base64(last_img)

    if "treshold" in todo.keys():
        last_img = modifier.img_treshhold(last_img)
        result["treshold"] = modifier.img_to_base64(last_img)

    if "unmask" in todo.keys():
        last_img = modifier.img_unmask(last_img, todo["unmask"]["count"])
        result["unmask"] = modifier.img_to_base64(last_img)

    print(result.keys())
    for i in result.keys():
        print(result[i][:30])
    #print(response)
    return flask.jsonify(result)


if __name__ == '__main__':
    app.run()
