# Alfae Remote Server

Host games remotely (Emulator or Pc) for use within Alfae.
Useful for cd rips, dumped game roms, etc that can be installed and uninstalled on the fly.

## Disk format:

#### Emulation
./emu is the base folder in this example. This is configurable via an environment variable.

emu.json:
```json
{
    "game_name": "Required",
    "files": [
        {
            "type": "Required. One of ['base', 'update', 'dlc', 'extra']",
            "version": "Optional. Default 'unk'. Can contain anything.",
            "file_name": "Required. Name of the relevant file in the same folder",
            "name": "Optional. Forces a public filename for the given file",
            "name_desc": "Optional. Is appended to the generated filename."
        }
    ]
}
```

```
./emu
    - console1
        - gamename1
            - emu.json
            - game.rom
        - gamename2
            - emu.json
            - game.rom
            - update.rom
```

The server can also generate this folder structure for you. If you create a console folder, you can place game roms inside of this folder. On next server boot, they will be re-organised. 

Updates, Dlcs and Extras can also be automatically matched to a base rom. All tags (), [], {} will be stripped from the filename, and the name of the remaining filename is compared to existing entries. If a match is found (remaining name is contained in filename of existing entry), the rom will be moved next to the base rom, and the emu.json will be updated accordingly.

To simplify documentation, when [] is used, you can also use () or {}.

- To organise updates, include [UPD] in the filename. 
- To organise dlc, include [DLC-TAG], [DLC_TAG], [DLC|TAG], [DLC=TAG]. TAG is used to name the dlc (Example: [DLC_CONTENT_PACK_1])
- To organise extras, include [EXTRA-TAG], [EXTRA_TAG], [EXTRA|TAG], [EXTRA=TAG]. TAG is used to name the extra content (Example: [EXTRA_CHEAT_1]) 

#### Pc
./pc is the base folder in this example. This is configurable via an environment variable.

game.json:
```json
{
    "game_name": "Required",
    "launch_exec": "Required. Path to executable inside zip. Starts relative from the root of the zip",
    "working_dir": "Required. Working directory of launch executable",
    "launch_args": ["Required, but can be empty. Arguments to pass into launch executable"],
    "version": "Optional. Defaults to 'unk'"
}
```

```
./pc
    - game1.zip
    - game2.zip
    - game3.zip
```

The zip should contain game.json at the root level. The zip should be compressed using deflate or deflate64. Zip downloads in Alfae are unpacked directly to disk while downloading.

#### Extras
./extras is the base folder in this examaple. This is configurable via an environment variable.
Extras are loose files without any organisation.

```
./extras
    - folder1
        - loosefile1
        - loosefile2
```

## Generated URL's

This server only provides an index to download files. A file server should be hosted seperately. The URL's by the indexer are generated as follows: 

Emulation: BASE_URL + /emu/ + PLATFORM + / + GAME_ID + / + FILENAME
Pc: BASE_URL + /pc/ + FILENAME
Extra: BASE_URL + /extra/ + FOLDERNAME + / + FILENAME
Image: BASE_URL + /img/ + GAME_ID + / + FILENAME

## Docker Compose

```yaml
version: "3.8"
services:
  file-server:
    image: joseluisq/static-web-server:latest
    restart: unless-stopped
    environment:
      - SERVER_ROOT=/data
      - SERVER_HTTPS_REDIRECT_HOST=${BASE_URL}
    volumes:
      - /path/to/data:/data:ro
    ports:
      - 2035:80
  indexer:
    stop_grace_period: 2s
    image: ghcr.io/suchmememanyskill/alfae-server:latest
    restart: unless-stopped
    volumes:
      - /path/to/data:/data
    environment:
      - EMU_ENABLED=true
      - PC_ENABLED=true
      - EXTRA_ENABLED=true
      - PC_DIR=/data/pc
      - EMU_DIR=/data/emu
      - EXTRA_DIR=/data/extra
      - BASE_URL=${PROTOCOL}://${BASE_URL}
      - IMG_DIR=/data/img
      - STEAMGRIDDB_API_KEY=${STEAMGRIDDB_API_KEY}
    ports:
      - 2036:5000
networks: {}
```


## API Format:

```json
{
    "games": [
        {
            "files": [
                {
                    "download_size": 1459978240,
                    "ext": "iso",
                    "installed_size": 1459978240,
                    "name": "super_smash_bros_melee_base_USA.iso",
                    "type": "base",
                    "url": "localhost:5000/emu/Gamecube/super_smash_bros_melee/Super%20Smash%20Bros.%20Melee%20%28USA%29%20%28En%2CJa%29%20%28v1.02%29.iso",
                    "version": "USA"
                }
            ],
            "id": "super_smash_bros_melee",
            "name": "Super Smash Bros. Melee",
            "images": {
                "background": "localhost:5000/img/super_smash_bros_melee/background.png",
                "horizontalcover": "localhost:5000/img/super_smash_bros_melee/horizontalcover.png",
                "icon": "localhost:5000/img/super_smash_bros_melee/icon.png",
                "logo": "localhost:5000/img/super_smash_bros_melee/logo.png",
                "verticalcover": "localhost:5000/img/super_smash_bros_melee/verticalcover.png"
            },
            "platform": "Gamecube",
            "size":	"1.36 GB"
        },
        {
            "files": [
                {
                    "download_size": 223438613,
                    "ext": "zip",
                    "installed_size": 323443297,
                    "name": "ashorthike.zip",
                    "type": "base",
                    "url": "localhost:5000/pc/ashorthike.zip",
                    "version": "unk"
                }
            ],
            "id": "a_short_hike",
            "name": "A Short Hike",
            "image": {
                "background": "localhost:5000/img/a_short_hike/background.jpg",
                "horizontalcover": "localhost:5000/img/a_short_hike/horizontalcover.jpg",
                "icon": "localhost:5000/img/a_short_hike/icon.png",
                "logo": "localhost:5000/img/a_short_hike/logo.png",
                "verticalcover": "localhost:5000/img/a_short_hike/verticalcover.png"
            },
            "platform": "Pc",
            "size":	"308.46 MB"
        }
    ],
    "extras": [
        {
            "files": [
                {
                    "download_size": 8,
                    "ext": "txt",
                    "installed_size": 8,
                    "name": "My Mega Cheats Collection.txt",
                    "type": "extra",
                    "url": "localhost:5000/extra/loose_pc/My%20Mega%20Cheats%20Collection.txt",
                    "version": "unk"
                }
            ],
            "id": "loosepc",
            "name": "loose_pc",
            "platform": "Extra",
            "size": "8.0 B"
        }
    ]
}
```
