import sys, os, utils, steamgriddb, json, re
from urllib.parse import quote

ENABLED = os.getenv("EMU_ENABLED", "0") == "1" or os.getenv("EMU_ENABLED", "0").lower() == "true"
EMU_DIR = os.getenv("EMU_DIR", "./emu")

def extract_version(filename : str) -> str:
    options = re.findall(r"[\[{(](v.*?)[\])}]", filename)

    if len(options) <= 0:
        return "unk"
    else:
        return options[-1]

class EmuGameFile:
    def __init__(self, dir_path : str, data : dict, game_id : str, emu : str):
        self.filename : str = data["file_name"]
        self.ext = self.filename.split(".")[-1]
        self.type = data["type"] if "type" in data else utils.GAME_BASE
        self.version = data["version"] if "version" in data else "unk"
        self.filepath = os.path.join(dir_path, self.filename)
        self.download_size = os.path.getsize(self.filepath)
        self.url = f"{utils.BASE_URL}/emu/{emu}/{game_id}/{quote(self.filename)}"

        self.orig_name = data["name"] if "name" in data else None
        self.orig_name_desc = data["name_desc"] if "name_desc" in data else None
        
        if self.type not in utils.GAME_TYPES:
            raise Exception(f"Invalid download type {self.type}")

        if "name" in data:
            self.name = data["name"]
        else:
            self.name = f"{game_id}_{self.type}"
            if self.version != "unk":
                self.name += f"_{self.version}"

            if 'name_desc' in data:
                self.name += f"_{data['name_desc']}"

            self.name += f".{self.ext}"

    def to_storage(self) -> dict:
        data = {
            "type": self.type,
            "version": self.version,
            "file_name": self.filename,
        }

        if self.orig_name != None:
            data["name"] = self.orig_name
        
        if self.orig_name_desc != None:
            data["name_desc"] = self.orig_name_desc
        
        return data

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "ext": self.ext,
            "version": self.version,
            "name": self.name,
            "download_size": self.download_size,
            "installed_size": self.download_size,
            "url": self.url
        }

class EmuGame:
    def __init__(self, emu : str, game_id : str):
        self.dir_path = os.path.join(EMU_DIR, emu, game_id)
        self.data_path = os.path.join(self.dir_path, "emu.json")
        with open(self.data_path, 'r') as emu_file:
            data = json.load(emu_file)
        self.game_id = game_id
        self.game_name = data["game_name"]
        self.emu = emu
        self.img = steamgriddb.load_img_for_game(self.game_name, self.game_id)
        self.files = [EmuGameFile(self.dir_path, x, game_id, emu) for x in data["files"]]

    def base_files(self) -> list[EmuGameFile]:
        return [x for x in self.files if x.type == utils.GAME_BASE]
    
    def add_update(self, filename : str):
        path = os.path.join(EMU_DIR, self.emu)
        file_path = os.path.join(path, filename)
        os.rename(file_path, os.path.join(self.dir_path, filename))
        self.files.append(EmuGameFile(self.dir_path, {
            "file_name": filename,
            "type": utils.GAME_UPDATE,
            "version": extract_version(file_path)
        }, self.game_id, self.emu))

        for base in self.base_files():
            if base.version == "unk":
                base.version = "v0"

        self.update_storage()
    
    def add_dlc(self, filename : str, dlc_name : str):
        path = os.path.join(EMU_DIR, self.emu)
        file_path = os.path.join(path, filename)
        os.rename(file_path, os.path.join(self.dir_path, filename))
        self.files.append(EmuGameFile(self.dir_path, {
            "file_name": filename,
            "type": utils.GAME_DLC,
            "version": extract_version(file_path),
            "name_desc": dlc_name
        }, self.game_id, self.emu))
        self.update_storage()

    def add_extra(self, filename : str, extra_name : str):
        path = os.path.join(EMU_DIR, self.emu)
        file_path = os.path.join(path, filename)
        os.rename(file_path, os.path.join(self.dir_path, filename))
        self.files.append(EmuGameFile(self.dir_path, {
            "file_name": filename,
            "type": utils.GAME_EXTRA,
            "version": extract_version(file_path),
            "name_desc": extra_name
        }, self.game_id, self.emu))
        self.update_storage()

    def update_storage(self):
        with open(self.data_path, 'w') as emu_file:
            json.dump(self.to_storage(), emu_file)
    
    def to_storage(self) -> dict:
        return {
            "game_name": self.game_name,
            "files": [x.to_storage() for x in self.files],
        }

    def to_dict(self) -> dict:
        return {
            "id": self.game_id,
            "name": self.game_name,
            "images": self.img,
            "files": [x.to_dict() for x in self.files],
            "platform": self.emu,
            "size": utils.convert_size(sum([x.download_size for x in self.files])),
        }

def __search(emuGames : list[EmuGame], filename : str) -> EmuGame:
    ajusted_name : str = re.findall(r"(.*?)[\[{(].*?[\]})]", filename)[0].strip()

    for game in emuGames:
        for file in game.files:
            if ajusted_name in file.filename:
                return game
            
    return None


def load() -> list[EmuGame]:
    if not ENABLED:
        utils.info("Emu module is disabled")
        return []

    if not os.path.exists(EMU_DIR):
        utils.error(f"Emu directory {EMU_DIR} does not exist")
        return []

    emu_games = []
    for emu in os.listdir(EMU_DIR):
        full_path = os.path.join(EMU_DIR, emu)
        dirs = [f for f in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, f)) 
            and os.path.exists(os.path.join(full_path, f, "emu.json"))]

        for game_id in dirs:
            try:
                emu_games.append(EmuGame(emu, game_id))
            except Exception as e:
                utils.error(f"Failed loading emu game {game_id}: {str(e)}")

        files = [f for f in os.listdir(full_path) if os.path.isfile(os.path.join(full_path, f))]
        update_files = [f for f in files if re.search(r"[\[{(]UPD[\]})]", f) != None]
        dlc_files = [f for f in files if re.search(r"[\[{(]DLC[-|_=](.*?)[\]})]", f) != None]
        extra_files = [f for f in files if re.search(r"[\[{(]EXTRA[-|_=](.*?)[\]})]", f) != None]
        base_files = [f for f in files if f not in update_files and f not in dlc_files and f not in extra_files]

        for base in base_files:
            try:
                name = steamgriddb.get_game_name(base)
                if name != None:
                    game_id = utils.squash_name(name)
                else:
                    game_id = utils.squash_name(base)
                    name = game_id

                gen = {
                    "game_name": name,
                    "files": [{
                        "file_name": base,
                        "type": utils.GAME_BASE
                    }]
                }

                new_dir = os.path.join(full_path, game_id)
                os.mkdir(new_dir)
                os.rename(os.path.join(full_path, base), os.path.join(new_dir, base))

                with open(os.path.join(new_dir, "emu.json"), 'w') as emu_file:
                    json.dump(gen, emu_file)
                
                emu_games.append(EmuGame(emu, game_id))
            except Exception as e:
                utils.error(f"Failed generating emu base entry {base}: {str(e)}")

        for update in update_files:
            try:
                search = __search(emu_games, update)
                if search == None:
                    utils.warn(f"Could not find base game for update {update}")
                    continue

                search.add_update(update)
            except Exception as e:
                utils.error(f"Failed generating emu update entry {update}: {str(e)}")
            
        for dlc in dlc_files:
            try:
                search = __search(emu_games, dlc)
                if search == None:
                    utils.warn(f"Could not find base game for dlc {dlc}")
                    continue

                dlc_name = re.findall(r"[\[{(]DLC[-|_=](.*?)[\]})]", dlc)[0]
                search.add_dlc(dlc, dlc_name)
            except Exception as e:
                utils.error(f"Failed generating emu dlc entry {dlc}: {str(e)}")
        
        for extra in extra_files:
            try:
                search = __search(emu_games, extra)
                if search == None:
                    utils.warn(f"Could not find base game for extra {extra}")
                    continue

                extra_name = re.findall(r"[\[{(]EXTRA[-|_=](.*?)[\]})]", extra)[0]
                search.add_extra(extra, extra_name)
            except Exception as e:
                utils.error(f"Failed generating emu extra entry {extra}: {str(e)}")
    
    utils.info(f"Loaded {len(emu_games)} emu games")
    return emu_games