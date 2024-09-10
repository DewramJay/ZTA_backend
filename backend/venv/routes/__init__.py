from flask import Blueprint, Flask

def create_app():
    app = Flask(__name__)
    
    # from .evaluation import evaluation
    # app.register_blueprint(evaluation)

    from .device import device
    from .urlAlerts import urlAlert
    from .evaluation import evaluation

    app.register_blueprint(device)
    app.register_blueprint(urlAlert)
    app.register_blueprint(evaluation)
    
    # Other app configuration and initialization
    
    return app
