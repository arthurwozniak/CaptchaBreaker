from .classificators import blueprint as classificators_blueprint
from .datasets import blueprint as datasets_blueprint
from .overview import blueprint as overview_blueprint
from .general import blueprint as general_blueprint
from .demo import blueprint as demo_blueprint


def blueprints():
    return [classificators_blueprint,
            datasets_blueprint,
            demo_blueprint,
            overview_blueprint,
            general_blueprint]
