import steamgrid, os, requests, utils

STEAMGRIDDB_API_KEY = os.getenv("STEAMGRIDDB_API_KEY", "")
IMG_DIR = os.getenv("IMG_DIR", "./images")
IMG_FILES = ["verticalcover", "background", "horizontalcover", "logo", "icon"]

SGDB = None

if STEAMGRIDDB_API_KEY != "":
    SGDB = steamgrid.SteamGridDB(STEAMGRIDDB_API_KEY)

def __download_steamgriddb_img(sgdb_id : str, game_id : str, func, allowed_dimensions : list[tuple[int, int]], img_type : str) -> bool:
    try:
        result = func([sgdb_id])
        for x in result:
            if (len(allowed_dimensions) <= 0 or (x.width, x.height) in allowed_dimensions) and (x.mime == "image/jpeg" or x.mime == "image/png"):
                img_data = requests.get(x.url).content

                with open(os.path.join(IMG_DIR, game_id, f"{img_type}.{'png' if x.mime == 'image/png' else 'jpg'}"), 'wb') as img_file:
                    img_file.write(img_data)

                return True
        
        return False
    except Exception as e:
        print(f"Error downloading image for {game_id}: {e}")
        return False

def get_game_name(filename : str) -> str|None:
    ext = filename.split(".")[-1]
    results = SGDB.search_game(filename[:-(len(ext) + 1)])
    if results != None and len(results) > 0:
        return results[0].name
    
    return None

def load_img_for_game(game_name : str, game_id : str) -> dict:
    if SGDB is None:
        utils.warn("No SteamGridDB API key provided")
        return {}

    local_path = os.path.join(IMG_DIR, game_id)
    if not os.path.exists(local_path):
        try:
            utils.info(f"Downloading images for game '{game_id}'")
            entries = SGDB.search_game(game_name)
            os.mkdir(local_path)
            if len(entries) > 0:
                entry = entries[0]
                __download_steamgriddb_img(entry.id, game_id, SGDB.get_grids_by_gameid, [(600, 900)], "verticalcover")
                __download_steamgriddb_img(entry.id, game_id, SGDB.get_grids_by_gameid, [(460, 215), (920, 430)], "horizontalcover")
                __download_steamgriddb_img(entry.id, game_id, SGDB.get_heroes_by_gameid, [], "background")
                __download_steamgriddb_img(entry.id, game_id, SGDB.get_logos_by_gameid, [], "logo")
                __download_steamgriddb_img(entry.id, game_id, SGDB.get_icons_by_gameid, [], "icon")
        except Exception as e:
            utils.error(f"Error while downloading images for game '{game_id}': {str(e)}")

    img = {}
    for x in IMG_FILES:
        if os.path.exists(os.path.join(local_path, x + ".png")):
            img[x] = utils.BASE_URL + "/img/" + game_id + "/" + x + ".png"
        elif os.path.exists(os.path.join(local_path, x + ".jpg")):
            img[x] = utils.BASE_URL + "/img/" + game_id + "/" + x + ".jpg"
    
    return img
