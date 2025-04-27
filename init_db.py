from tinydb import TinyDB
import uuid

db = TinyDB("./database/model_db.json")

tiny = {
    "model_id": 1,
    "name": "Whisper",
    "version": "tiny",
    "path": "./models/hubs/pho-whisper-tiny"
}

base = {
    "model_id": 2,
    "name": "Whisper",
    "version": "base",
    "path": "./models/hubs/pho-whisper-base"
}

db.insert(tiny)
db.insert(base)