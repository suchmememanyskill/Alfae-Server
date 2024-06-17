import os, math

def log(msg : str, severity : str = "info") -> None:
    print(f"[{severity}] {msg}")

def info(msg : str) -> None:
    log(msg)

def warn(msg : str) -> None:
    log(msg, "warn")

def error(msg : str) -> None:
    log(msg, "error")

def fatal(msg : str) -> None:
    log(msg, "fatal")

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

def squash_name(name : str) -> str:
    return ''.join([e for e in name.lower() if e.isalnum() or e == ' ']).replace(" ", "_")

if "BASE_URL" not in os.environ:
    fatal("BASE_URL environment variable not set")
    exit(1)

BASE_URL = os.environ["BASE_URL"]

GAME_BASE = "base"
GAME_UPDATE = "update"
GAME_DLC = "dlc"
GAME_EXTRA = "extra"

GAME_TYPES = [GAME_BASE, GAME_UPDATE, GAME_DLC, GAME_EXTRA]