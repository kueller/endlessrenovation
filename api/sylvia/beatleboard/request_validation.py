BEATLEBOARD_ADD_TEMPLATE = {
    "type": "object",
    "properties": {
        "song-id": {"type": "integer"},
        "score": {"type": "integer"},
        "proof": {"type": "string"},
        "uploader-id": {"type": "string"},
        "uploader-name": {"type": "string"},
        "date": {"type": "string"},
        "instruments": {
            "type": "object",
            "properties": {
                "gtr": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "username": {"type": "string"},
                    },
                    "required": ["username"],
                },
                "drums": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "username": {"type": "string"},
                    },
                    "required": ["username"],
                },
                "bass": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "username": {"type": "string"},
                    },
                    "required": ["username"],
                },
                "vox": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "username": {"type": "string"},
                    },
                    "required": ["username"],
                },
                "harms": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "username": {"type": "string"},
                    },
                    "required": ["username"],
                },
            },
            "additionalProperties": False,
        },
    },
    "required": [
        "song-id",
        "score",
        "proof",
        "uploader-id",
        "uploader-name",
        "date",
        "instruments",
    ],
}

BEATLEBOARD_SONG_ADD_TEMPLATE = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "name": {"type": "string"},
        "album": {"type": "string"},
        "artist": {"type": "string"},
        "released": {"type": "string"},
    },
    "required": ["id", "name", "album", "artist", "released"],
}

BEATLEBOARD_SEARCH_SONGS_TEMPLATE = {
    "type": "object",
    "properties": {"query": {"type": "string"}},
    "required": ["query"],
}
