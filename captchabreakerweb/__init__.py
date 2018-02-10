from flask import abort, Flask, g, render_template, request
from captchabreakerweb.utils import get_instance_folder_path
from captchabreakerweb.admin.controllers import admin


app = Flask(__name__,
            instance_path=get_instance_folder_path(),
            instance_relative_config=True,
            template_folder='templates')

app.config['DEBUG'] = True


# @app.errorhandler(404)
# def page_not_found(error):
#     app.logger.error('Page not found: %s', (request.path, error))
#     return render_template('404.htm'), 404
#
# @app.errorhandler(500)
# def internal_server_error(error):
#     app.logger.error('Server Error: %s', (error))
#     return render_template('500.htm'), 500
#
# @app.errorhandler(Exception)
# def unhandled_exception(error):
#     app.logger.error('Unhandled Exception: %s', (error))
#     return render_template('500.htm'), 500


@app.route('/')
def home(lang_code=None):
    print("home")
    return render_template('index.html')


app.register_blueprint(admin, url_prefix='/admin')
