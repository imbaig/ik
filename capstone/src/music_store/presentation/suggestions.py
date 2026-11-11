"""Pure next-question suggestions from observed facts; never actions or identity authority."""

STARTERS = (
    "Show albums by AC/DC",
    "Show my latest invoice",
    "What music preferences have I saved?",
)
DISCOVERY = (
    "Show albums by Queen",
    "Find songs with love in the title",
    "Show songs in the Jazz genre",
)


def _label(value):
    if not isinstance(value, str) or not value.strip() or len(value) > 80:
        return None
    if any(ch in value for ch in "<>\n\r\t"):
        return None
    return value.strip()


def _identifier(value):
    text = str(value)
    if len(text) > 10:
        return None
    return text if text.isascii() and text.isdigit() and 0 < int(text) < 2**31 else None


def next_questions(state):
    """Three editable prompts. Returned IDs are references, never authorization."""
    if not state.messages:
        return STARTERS
    facts = state.result.facts if state.result is not None else ()
    catalog_tools = {
        "get_albums_by_artist",
        "get_tracks_by_artist",
        "get_songs_by_genre",
        "search_songs_by_title",
        "get_track_details",
    }
    for fact in facts:
        if not state.verified and fact.tool not in catalog_tools:
            continue
        envelope = fact.envelope
        if envelope["status"] != "ok":
            continue
        for row in envelope["data"]:
            invoice = _identifier(row.get("InvoiceId"))
            track = _identifier(row.get("TrackId"))
            artist = _label(row.get("Artist"))
            name = _label(row.get("Name"))
            track_question = (
                "Tell me about " + name + " (track " + track + ")"
                if name and track
                else "Show details for track " + str(track)
            )
            if state.verified and invoice:
                first = track_question if track else "Show the items on invoice " + invoice
                return (
                    first,
                    "Who can help with invoice " + invoice + "?",
                    "What tracks have I purchased?",
                )
            if track:
                return (
                    track_question,
                    "Show albums by " + artist if artist else DISCOVERY[0],
                    "Show my latest invoice",
                )
            if artist:
                return ("Show tracks by " + artist, DISCOVERY[1], "Show my latest invoice")
    if facts and all(not fact.envelope["data"] for fact in facts):
        if all(
            fact.tool
            in {
                "get_albums_by_artist",
                "get_tracks_by_artist",
                "get_songs_by_genre",
                "search_songs_by_title",
                "get_track_details",
            }
            for fact in facts
        ):
            return DISCOVERY
    if state.verified:
        return (
            "Show my latest invoice",
            "What tracks have I purchased?",
            "What music preferences have I saved?",
        )
    return STARTERS
