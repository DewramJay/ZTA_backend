from flask import Blueprint, Flask

def create_app():
    app = Flask(__name__)
    
    # from .evaluation import evaluation
    # app.register_blueprint(evaluation)

    from .device import device
    from .urlAlerts import urlAlert
    from .evaluation import evaluation
    from .scoreWeights import scoreWeights
    from .illegalConnection import illegalConnection
    from .trustScore import trustScore
    from .accessControl import accessControl

    app.register_blueprint(device)
    app.register_blueprint(urlAlert)
    app.register_blueprint(evaluation)
    app.register_blueprint(scoreWeights)
    app.register_blueprint(illegalConnection)
    app.register_blueprint(trustScore)
    app.register_blueprint(accessControl)
    
    # Other app configuration and initialization
    
    return app
