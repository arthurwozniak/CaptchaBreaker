from .classificators import blueprint as classificators_blueprint
from .datasets import blueprint as datasets_blueprint
from .overview import blueprint as overview_blueprint


def admin_blueprints():
    return [overview_blueprint,
            datasets_blueprint,
            classificators_blueprint]
