import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_cors import CORS
from config.config import DevelopmentConfig, TestingConfig, ProductionConfig

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = '请先登录!'

def create_app(config_name=None):
    """
    创建Flask应用实例
    
    @param {string} config_name - 配置名称，默认为环境变量中的FLASK_CONFIG或'development'
    @return {Flask} - Flask应用实例
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')
    
    app = Flask(__name__)
    
    config_mapping = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': DevelopmentConfig
    }
    
    app.config.from_object(config_mapping[config_name])
    config_mapping[config_name].init_app(app)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    CORS(app)
    Migrate(app, db)
    
    # 注册蓝图
    from app.views.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    
    from app.views.main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    
    from app.views.client import client as client_blueprint
    app.register_blueprint(client_blueprint, url_prefix='/client')
    
    from app.views.consultant import consultant as consultant_blueprint
    app.register_blueprint(consultant_blueprint, url_prefix='/consultant')
    
    return app 