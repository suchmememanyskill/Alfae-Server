import pc, emu, extras, utils, time
from flask import Flask, request, send_from_directory, send_file, render_template

app = Flask(__name__)
CONTENT_CACHE = {}

def create_content():
    global CONTENT_CACHE

    utils.info("Loading content...")
    start = time.time()

    pc_entries = [x.to_dict() for x in pc.load()]
    emu_entries = [x.to_dict() for x in emu.load()]
    extra_entries = [x.to_dict() for x in extras.load()]

    game_entries = pc_entries + emu_entries
    game_entries.sort(key=lambda x: x["game_name"].lower())

    CONTENT_CACHE = {
        "games": game_entries,
        "extras": extra_entries,
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
        return render_template("template.html", games=CONTENT_CACHE["games"], extras=CONTENT_CACHE["extras"])

    return CONTENT_CACHE

app.run(host='0.0.0.0', port=5000)