import sys, os, utils, steamgriddb, json, re, zipfile
from urllib.parse import quote

ENABLED = os.getenv("PC_ENABLED", "0") == "1" or os.getenv("PC_ENABLED", "0").lower() == "true"
PC_DIR = os.getenv("PC_DIR", "./pc")

class PcGame:
    def __init__(self, filename : str):
        self.filename = filename
        self.path = os.path.join(PC_DIR, filename)
        with zipfile.ZipFile(self.path, 'r') as archive:
            data = json.loads(archive.read('game.json'))
            self.game_id = utils.squash_name(data["game_name"])
            self.game_name = data["game_name"]
            self.game_size = 0
            self.download_size = os.path.getsize(self.path)
            self.version = data["version"] if "version" in data else "unk"
            self.img = steamgriddb.load_img_for_game(self.game_name, self.game_id)
            self.url = f"{utils.BASE_URL}/pc/{quote(self.filename)}"

            for info in archive.infolist():
                if not info.is_dir():
                    self.game_size += info.file_size

    def to_dict(self) -> dict:
        return {
            "game_id": self.game_id,
            "game_name": self.game_name,
            "img": self.img,
            "files": [
                {
                    "type": utils.GAME_BASE,
                    "ext": "zip",
                    "version": self.version,
                    "name": self.filename,
                    "download_size": self.download_size,
                    "game_size": self.game_size,
                    "url": self.url,
                }
            ],
            "platform": "Pc",
            "total_size": utils.convert_size(self.game_size),

            # Should be removed in a later version
            "download_size": self.download_size,
            "game_size": self.game_size,
            "version": self.version,
            "url": self.url,
        }
        
def load() -> list[PcGame]:
    if not ENABLED:
        utils.info("PC module is disabled")
        return []

    if not os.path.exists(PC_DIR):
        utils.error(f"PC directory {PC_DIR} does not exist")
        return []
    
    pc_games = []
    for file in [f for f in os.listdir(PC_DIR) if f.endswith('.zip') and os.path.isfile(os.path.join(PC_DIR, f))]:
        try:
            pc_games.append(PcGame(file))
        except Exception as e:
            utils.error(f"Failed loading PC game {file}: {str(e)}")

    utils.info(f"Loaded {len(pc_games)} pc games")
    return pc_games