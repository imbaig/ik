"""Fixed, bound SQL tools with per-request trusted identity captured by application code."""

import json
import logging
import re
from decimal import Decimal, InvalidOperation
from functools import wraps

from langchain_core.tools import tool

from music_store.db import Database, DatabaseQueryError

logger = logging.getLogger(__name__)


class InputError(ValueError):
    """Invalid model-supplied tool arguments."""


class AccessDenied(ValueError):
    """No verified context or requested account is inaccessible."""


def _positive_id(value: str) -> int:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{1,18}", value.strip()):
        raise InputError("Please provide a positive numeric ID")
    result = int(value.strip())
    if result < 1:
        raise InputError("Please provide a positive numeric ID")
    return result


def _pattern(value: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 200:
        raise InputError("Please provide a search term between 1 and 200 characters")
    # LIKE substring matching only: literal user percent/underscore do not broaden scope.
    escaped = value.strip().replace("\\", "\\\\").replace("%", r"\%").replace("_", r"\_")
    return "%" + escaped + "%"


def _envelope(rows=None, *, total=None, status=None, message=None, code=None, **extra):
    rows = rows or []
    clean = []
    for row in rows:
        item = dict(row)
        for key in ("UnitPrice", "Total"):
            if item.get(key) is not None:
                amount = Decimal(str(item[key]))
                if (
                    not amount.is_finite()
                    or amount < 0
                    or amount != amount.quantize(Decimal("0.01"))
                ):
                    raise ValueError("Invalid stored monetary value")
                item[key] = format(amount, ".2f")
        clean.append(item)
    count = len(clean)
    total = count if total is None else total
    return json.dumps(
        {
            "status": status or ("ok" if count else "not_found"),
            "data": clean,
            "total_count": total,
            "returned_count": count,
            "truncated": total > count,
            "message": message or ("Results returned" if count else "No matching results found"),
            "error_code": code,
            **extra,
        },
        ensure_ascii=False,
        allow_nan=False,
    )


def _guard(function):
    @wraps(function)
    def wrapped(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except InputError as error:
            return _envelope(status="invalid_input", message=str(error), code="invalid_input")
        except AccessDenied:
            return _envelope(
                status="error", message="Account information is inaccessible", code="access_denied"
            )
        except DatabaseQueryError:
            logger.warning("domain_tool_database_error")
            return _envelope(
                status="error", message="Data lookup failed; please retry", code="database_error"
            )

        except (InvalidOperation, ValueError, TypeError, OverflowError):
            logger.warning("domain_tool_stored_data_error")
            return _envelope(
                status="error",
                message="Stored data could not be read safely; contact support",
                code="stored_data_error",
            )

    return wrapped


def build_tools(database: Database, *, verified_customer_id: int | None = None) -> dict:
    """Build a fresh tool set per trusted request, never from model-supplied identity.

    The future verification/application layer supplies the verified ID. This constructor
    does not authenticate anyone. Never cache customer-bound tools across sessions.
    """
    if verified_customer_id is not None and (
        type(verified_customer_id) is not int or not 0 < verified_customer_id < 10**18
    ):
        raise ValueError("Trusted customer ID must be a positive integer")

    def customer(value):
        parsed = _positive_id(value)
        if verified_customer_id is None or parsed != verified_customer_id:
            raise AccessDenied
        return verified_customer_id

    @tool
    @_guard
    def get_albums_by_artist(artist_name: str) -> str:
        """Find albums by a partial artist name; return actual album/artist names and IDs."""
        rows = database.query(
            """
            SELECT al.AlbumId, al.Title, ar.ArtistId, ar.Name AS Artist
            FROM Album al JOIN Artist ar ON ar.ArtistId=al.ArtistId
            WHERE ar.Name LIKE :pattern ESCAPE '\\' ORDER BY al.AlbumId
        """,
            {"pattern": _pattern(artist_name)},
        )
        return _envelope(rows)

    @tool
    @_guard
    def get_tracks_by_artist(artist_name: str) -> str:
        """Find tracks by partial artist; disclose total and up to 20 stable sample rows."""
        params = {"pattern": _pattern(artist_name)}
        total = database.query(
            """
            SELECT COUNT(*) AS count FROM Track t JOIN Album al ON al.AlbumId=t.AlbumId
            JOIN Artist ar ON ar.ArtistId=al.ArtistId
            WHERE ar.Name LIKE :pattern ESCAPE '\\'
        """,
            params,
        )[0]["count"]
        rows = database.query(
            """
            SELECT t.TrackId, t.Name, ar.Name AS Artist, al.Title AS Album,
                   CAST(t.UnitPrice AS TEXT) AS UnitPrice
            FROM Track t JOIN Album al ON al.AlbumId=t.AlbumId
            JOIN Artist ar ON ar.ArtistId=al.ArtistId
            WHERE ar.Name LIKE :pattern ESCAPE '\\' ORDER BY t.TrackId LIMIT 20
        """,
            params,
        )
        return _envelope(rows, total=total)

    @tool
    @_guard
    def get_songs_by_genre(genre_name: str) -> str:
        """Find genre substring; one track per artist, <=10 artists, total tracks disclosed."""
        params = {"pattern": _pattern(genre_name)}
        totals = database.query(
            """
            SELECT COUNT(*) AS count, COUNT(DISTINCT ar.ArtistId) AS artists
            FROM Track t JOIN Genre g ON g.GenreId=t.GenreId
            JOIN Album al ON al.AlbumId=t.AlbumId JOIN Artist ar ON ar.ArtistId=al.ArtistId
            WHERE g.Name LIKE :pattern ESCAPE '\\'
        """,
            params,
        )[0]
        rows = database.query(
            """
            WITH ranked AS (
              SELECT t.TrackId, t.Name, ar.ArtistId, ar.Name AS Artist,
                     al.Title AS Album, g.Name AS Genre,
                     CAST(t.UnitPrice AS TEXT) AS UnitPrice,
                     ROW_NUMBER() OVER (PARTITION BY ar.ArtistId ORDER BY t.TrackId) AS rn
              FROM Track t JOIN Genre g ON g.GenreId=t.GenreId
              JOIN Album al ON al.AlbumId=t.AlbumId JOIN Artist ar ON ar.ArtistId=al.ArtistId
              WHERE g.Name LIKE :pattern ESCAPE '\\'
            ) SELECT TrackId, Name, ArtistId, Artist, Album, Genre, UnitPrice
            FROM ranked WHERE rn=1 ORDER BY ArtistId LIMIT 10
        """,
            params,
        )
        return _envelope(rows, total=totals["count"], distinct_artist_count=totals["artists"])

    @tool
    @_guard
    def search_songs_by_title(title: str) -> str:
        """Search a partial song title; return <=10 matches with full matching-track count."""
        params = {"pattern": _pattern(title)}
        total = database.query(
            """
            SELECT COUNT(*) AS count FROM Track WHERE Name LIKE :pattern ESCAPE '\\'
        """,
            params,
        )[0]["count"]
        rows = database.query(
            """
            SELECT t.TrackId, t.Name, ar.Name AS Artist, al.Title AS Album,
                   CAST(t.UnitPrice AS TEXT) AS UnitPrice
            FROM Track t JOIN Album al ON al.AlbumId=t.AlbumId
            JOIN Artist ar ON ar.ArtistId=al.ArtistId
            WHERE t.Name LIKE :pattern ESCAPE '\\' ORDER BY t.TrackId LIMIT 10
        """,
            params,
        )
        return _envelope(rows, total=total)

    @tool
    @_guard
    def get_track_details(track_id: str) -> str:
        """Get full catalog details for a positive numeric track ID."""
        rows = database.query(
            """
            SELECT t.TrackId, t.Name, t.AlbumId, t.MediaTypeId, t.GenreId, t.Composer,
                   t.Milliseconds, t.Bytes, CAST(t.UnitPrice AS TEXT) AS UnitPrice,
                   al.Title AS Album, ar.ArtistId, ar.Name AS Artist,
                   g.Name AS Genre, m.Name AS MediaType
            FROM Track t JOIN Album al ON al.AlbumId=t.AlbumId
            JOIN Artist ar ON ar.ArtistId=al.ArtistId
            LEFT JOIN Genre g ON g.GenreId=t.GenreId
            JOIN MediaType m ON m.MediaTypeId=t.MediaTypeId WHERE t.TrackId=:tid
        """,
            {"tid": _positive_id(track_id)},
        )
        return _envelope(rows)

    @tool
    @_guard
    def get_invoices_by_customer_sorted_by_date(customer_id: str) -> str:
        """List verified customer's invoices newest first; account must match trusted context."""
        rows = database.query(
            """
            SELECT InvoiceId, InvoiceDate, CAST(Total AS TEXT) AS Total,
                   BillingAddress, BillingCity, BillingState, BillingCountry, BillingPostalCode
            FROM Invoice WHERE CustomerId=:cid ORDER BY InvoiceDate DESC, InvoiceId DESC
        """,
            {"cid": customer(customer_id)},
        )
        return _envelope(rows)

    @tool
    @_guard
    def get_purchased_tracks(customer_id: str) -> str:
        """List owned purchased line items by descending unit price, without deduplication."""
        rows = database.query(
            """
            SELECT il.InvoiceLineId, il.InvoiceId, il.TrackId, t.Name, il.Quantity,
                   CAST(il.UnitPrice AS TEXT) AS UnitPrice
            FROM InvoiceLine il JOIN Invoice i ON i.InvoiceId=il.InvoiceId
            JOIN Track t ON t.TrackId=il.TrackId
            WHERE i.CustomerId=:cid ORDER BY il.UnitPrice DESC, il.InvoiceLineId ASC
        """,
            {"cid": customer(customer_id)},
        )
        return _envelope(rows)

    @tool
    @_guard
    def get_support_rep_by_invoice(customer_id: str, invoice_id: str) -> str:
        """Get safe contact fields for the verified customer's specific invoice representative."""
        params = {"cid": customer(customer_id), "iid": _positive_id(invoice_id)}
        rows = database.query(
            """
            SELECT e.EmployeeId, e.FirstName, e.LastName, e.Email, e.Phone
            FROM Invoice i JOIN Customer c ON c.CustomerId=i.CustomerId
            JOIN Employee e ON e.EmployeeId=c.SupportRepId
            WHERE i.InvoiceId=:iid AND i.CustomerId=:cid
        """,
            params,
        )
        return _envelope(rows, message=None if rows else "No accessible invoice information found")

    @tool
    @_guard
    def get_invoice_line_items(customer_id: str, invoice_id: str) -> str:
        """Get owned invoice's line items; unowned and absent invoices share the same response."""
        params = {"cid": customer(customer_id), "iid": _positive_id(invoice_id)}
        rows = database.query(
            """
            SELECT il.InvoiceLineId, il.InvoiceId, il.TrackId, t.Name, il.Quantity,
                   CAST(il.UnitPrice AS TEXT) AS UnitPrice
            FROM InvoiceLine il JOIN Invoice i ON i.InvoiceId=il.InvoiceId
            JOIN Track t ON t.TrackId=il.TrackId
            WHERE i.InvoiceId=:iid AND i.CustomerId=:cid ORDER BY il.InvoiceLineId ASC
        """,
            params,
        )
        return _envelope(rows, message=None if rows else "No accessible invoice information found")

    tools = [
        get_albums_by_artist,
        get_tracks_by_artist,
        get_songs_by_genre,
        search_songs_by_title,
        get_track_details,
        get_invoices_by_customer_sorted_by_date,
        get_purchased_tracks,
        get_support_rep_by_invoice,
        get_invoice_line_items,
    ]
    for domain_tool in tools:
        domain_tool.handle_validation_error = lambda _: _envelope(
            status="invalid_input",
            message="Please supply the required string arguments",
            code="invalid_input",
        )
    return {item.name: item for item in tools}
