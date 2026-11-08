# Tool contracts

All nine tools use LangChain @tool and return valid JSON strings on success, empty or
error. No raw SQL agent tool. All user arguments are strings; numeric fields parse to
positive integers or return invalid_input without executing SQL. Account tools accept
customer_id for course/tool test compatibility but runtime executor validates/overrides
from trusted identity; account mismatch and unowned invoice give generic inaccessible.
Catalog results use bound LIKE substring search (not phonetic similarity); escape literal
%/_ when used as user text. Stable ID tie-breakers on all limited/ordered outputs.

| Tool | Arguments | Behavior |
|---|---|---|
| get_albums_by_artist | artist_name | Artist substring; album/artist IDs and names, stable AlbumId order |
| get_tracks_by_artist | artist_name | Total matching tracks; <=20 sample with TrackId, title, artist, album, UnitPrice |
| get_songs_by_genre | genre_name | Genre substring; total matching tracks and distinct artist count; <=10, one lowest-TrackId representative per ArtistId, stable ArtistId order |
| search_songs_by_title | title | Title substring, <=10 stable TrackId results; total count |
| get_track_details | track_id | Full catalog track fields plus album/artist/genre/media names, or not_found |
| get_invoices_by_customer_sorted_by_date | customer_id | All owned invoices; InvoiceDate DESC, InvoiceId DESC |
| get_purchased_tracks | customer_id | One row per purchased InvoiceLine; UnitPrice DESC, InvoiceLineId ASC; quantity separate; no unrequested deduplication |
| get_support_rep_by_invoice | customer_id, invoice_id | Ownership join Invoice→Customer→Employee; safe rep contact fields or not_found |
| get_invoice_line_items | customer_id, invoice_id | Owned invoice's track/quantity/unit price; InvoiceLineId ASC |

JSON envelope: status (ok/not_found/invalid_input/error), data (array), total_count,
returned_count, truncated (bool), message (string), error_code (nullable). Preserve exact
monetary values with decimal strings. Not-found/error message lives inside JSON. Query
utility run_query_safe(sql, params) returns JSON row array, including [] for empty;
it is internal, not model-exposed. Tools wrap utility outcomes in the envelope. Exceptions
are sanitized, logged without raw input and not passed as SQL internals to the customer.
Invalid ownership cannot reveal another invoice's existence. Stored-data and connection
faults are distinguishable in internal error codes, not fabricated zero-result successes.
