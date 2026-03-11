from flask import Flask
from .extensions import db, login_manager
from .config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    # Register blueprints
    from .routes.auth  import auth_bp
    from .routes.main  import main_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)

    # Error handlers
    from flask import render_template

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('error/403.html'), 403

    @app.errorhandler(404)
    def not_found(e):
        return render_template('error/403.html'), 404

    return app
