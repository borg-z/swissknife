from app import app
from werkzeug.contrib.fixers import ProxyFix

app.config['DEBUG'] = True
app.wsgi_app = ProxyFix(app.wsgi_app)
if __name__ == '__main__':
    app.run()

