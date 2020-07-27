
from frontend import app
from flask_debugtoolbar import DebugToolbarExtension

toolbar = DebugToolbarExtension(app)

@app.route('/')
def index():
    logging.warning("See this message in Flask Debug Toolbar!")
    return "<html><body></body></html>"

# app.run(debug=True)
app.run(debug = True)