HYPHENATOR_REQUEST_VALIDATION = {
    "type": "object",
    "properties": {
        "words": {
            "type": "array",
            "items": {"word": {"type": "string"}, "hyphenation": {"type": "string"}},
        },
        "language": {"type": "string"},
    },
    "required": ["words", "language"],
}
