import pc, emu, extras, utils, time
from flask import Flask, request, send_from_directory, send_file, render_template

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

@app.template_filter('readable')
def readable_size(s):
    return utils.convert_size(int(s))

@app.route("/")
def fetch_game_data():
    html = request.args.get('html') == "true"

    if html:
        content = []
        content.extend(CONTENT_CACHE["emu"])
        content.extend(CONTENT_CACHE["pc"])
        content.sort(key=lambda x: x["game_name"].lower())
        print(content)
        return render_template("template.html", games=content, extras=CONTENT_CACHE["extras"])

    return CONTENT_CACHE

app.run(host='0.0.0.0', port=5000)