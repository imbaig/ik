"""Deterministic readable projections of observed facts, never model-authored store claims."""

import html
import re

TITLES = {
    "get_albums_by_artist": "Albums",
    "get_tracks_by_artist": "Tracks by artist",
    "get_songs_by_genre": "Explore a genre",
    "search_songs_by_title": "Matching tracks",
    "get_track_details": "Track details",
    "get_invoices_by_customer_sorted_by_date": "Your invoices · newest first",
    "get_purchased_tracks": "Your purchased tracks · highest unit price first",
    "get_support_rep_by_invoice": "Your invoice support contact",
    "get_invoice_line_items": "Your invoice items",
}
LABELS = {
    "AlbumId": "Album ID",
    "Title": "Album",
    "ArtistId": "Artist ID",
    "Artist": "Artist",
    "TrackId": "Track ID",
    "Name": "Track",
    "Album": "Album",
    "UnitPrice": "Unit price",
    "Genre": "Genre",
    "GenreId": "Genre ID",
    "MediaTypeId": "Media type ID",
    "MediaType": "Media type",
    "Composer": "Composer",
    "Milliseconds": "Duration (milliseconds)",
    "Bytes": "Size (bytes)",
    "InvoiceId": "Invoice ID",
    "InvoiceDate": "Invoice date",
    "Total": "Recorded total",
    "BillingAddress": "Billing address",
    "BillingCity": "City",
    "BillingState": "State",
    "BillingCountry": "Country",
    "BillingPostalCode": "Postal code",
    "InvoiceLineId": "Line item ID",
    "Quantity": "Quantity",
    "EmployeeId": "Representative ID",
    "FirstName": "First name",
    "LastName": "Last name",
    "Email": "Email",
    "Phone": "Phone",
}


def safe_text(value):
    """Escape HTML and Markdown syntax, including autolink delimiters; never emit links."""
    text = "Not provided" if value is None else str(value)
    # Markdown parsers normalize both CRLF and bare CR before block parsing.
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = html.escape(text, quote=False)
    text = re.sub(r"([\\`*_{}\[\]()#+.!|~:=\-])", r"\\\1", text)
    # Prevent indented code blocks without discarding the original whitespace.
    text = re.sub(
        r"(?m)^[ \t]+",
        lambda match: "".join("&#32;" if ch == " " else "&#9;" for ch in match[0]),
        text,
    )
    return text.replace("\n", "  \n")


def render_fact(section):
    envelope = section.envelope
    title = TITLES.get(section.tool, "Results")
    lines = ["### " + title]
    # Counts, ordering and genre sampling metadata are not recalculated from display rows.
    lines.append(f"Showing {envelope['returned_count']} of {envelope['total_count']} results.")
    if "distinct_artist_count" in envelope:
        lines.append(
            f"{envelope['total_count']} matching tracks across "
            f"{envelope['distinct_artist_count']} artists; at most one track per artist is shown."
        )
    if envelope["truncated"]:
        lines.append("This is a sample; more matching results exist. Try a narrower question.")
    if envelope["status"] != "ok":
        lines.append(safe_text(envelope["message"]))
        if envelope["status"] == "not_found":
            lines.append(
                "Try a different catalog term or check the invoice number for your account."
            )
        else:
            lines.append("Please retry. No additional account information is available here.")
    rows = envelope["data"]
    if rows:
        # Preserve every field, including sparse/future fields, without inferring values.
        keys = list(dict.fromkeys(key for row in rows for key in row))

        def cell(value):
            # Raw HTML cells are data, never Markdown. Escaping once also preserves
            # apostrophes that previously became visible entities after Markdown escaping.
            return (
                html.escape("Not provided" if value is None else str(value), quote=True)
                .replace("\r", "&#13;")
                .replace("\n", "&#10;")
                .replace("\t", "&#9;")
            )

        table = (
            '<div class="result-table" role="region" aria-label="' + cell(title) + '" tabindex="0">'
        )
        table += "<table><caption>" + cell(title) + "</caption><thead><tr>"
        table += "".join('<th scope="col">' + cell(LABELS.get(key, key)) + "</th>" for key in keys)
        table += "</tr></thead><tbody>"
        for row in rows:
            table += (
                "<tr>" + "".join("<td>" + cell(row.get(key)) + "</td>" for key in keys) + "</tr>"
            )
        table += "</tbody></table></div>"
        if len(rows) > 5:
            table = (
                '<details class="result-disclosure"><summary>Show/hide '
                + str(envelope["returned_count"])
                + " results</summary>"
                + table
                + "</details>"
            )
        lines.append(table)
    return "\n\n".join(lines)


def render_result(result):
    if not result.facts:
        return safe_text(result.text)
    sections = [safe_text(notice) for notice in result.notices]
    if (
        not result.notices
        and result.status == "complete"
        and any(section.envelope["data"] for section in result.facts)
    ):
        sections.append("Here’s what I found.")
    sections.extend(render_fact(section) for section in result.facts)
    if result.status != "complete":
        sections.append(
            "**This request did not fully complete.** You can retry the unfinished part."
        )
    return "\n\n".join(sections)
