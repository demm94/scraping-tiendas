from flask import Flask
from routes.base import base_bp
from routes.falabella import falabella_bp
from routes.paris import paris_bp
from routes.ripley import ripley_bp
from routes.favoritos import favoritos_bp
from routes.abcdin import abcdin_bp
from routes.lapolar import lapolar_bp
from routes.lider import lider_bp
from routes.hites import hites_bp

app = Flask(__name__)

app.register_blueprint(base_bp)
app.register_blueprint(falabella_bp)
app.register_blueprint(paris_bp)
app.register_blueprint(ripley_bp)
app.register_blueprint(favoritos_bp)
app.register_blueprint(abcdin_bp)
app.register_blueprint(lapolar_bp)
app.register_blueprint(lider_bp)
app.register_blueprint(hites_bp)