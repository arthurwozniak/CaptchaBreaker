import os

from flask import Blueprint, send_from_directory, render_template, request, current_app

blueprint = Blueprint('general', __name__, template_folder='templates', static_folder='static')


@blueprint.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join('.', 'static', 'images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@blueprint.app_errorhandler(404)
def page_not_found(error):
    current_app.logger.info('Page not found: %s', (request.path, error))
    return render_template('errors/404.html'), 404


@blueprint.app_errorhandler(500)
def internal_server_error(error):
    current_app.logger.error('Server Error: %s', (error))
    return render_template('errors/500.html'), 500


#@blueprint.app_errorhandler(Exception)
def unhandled_exception(error):
    current_app.logger.error('Unhandled Exception: %s', (error))
    return render_template('errors/500.html'), 500
