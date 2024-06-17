import pc, emu, extras, utils, time
from flask import Flask

app = Flask(__name__)
CONTENT_CACHE = {}

def create_content():
    global CONTENT_CACHE

    utils.info("Loading content...")
    start = time.time()

    CONTENT_CACHE = {
        "pc": [x.to_dict() for x in pc.load()],
        "emu": [x.to_dict() for x in emu.load()],
        "extras": [x.to_dict() for x in extras.load()],
    }

    utils.info(f"Done in {time.time() - start:.2f}s")

create_content()

@app.route("/")
def fetch_game_data():
    return CONTENT_CACHE

app.run(host='0.0.0.0', port=5000)