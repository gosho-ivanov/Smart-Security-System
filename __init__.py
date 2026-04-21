import os
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
    login_manager.login_message = 'Моля, влезте, за да достъпите тази страница.'
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

    # Start the keypad listener in a background daemon thread.
    # In debug mode Werkzeug runs two processes; only start in the child
    # (the actual server) to avoid spawning the thread twice.
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        from . import keypad_listener
        keypad_listener.start(app)

    return app
