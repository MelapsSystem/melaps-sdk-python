"""Cursor pagination helper for list endpoints."""


def iter_all(fetch_page, limit=100):
    """Yield every item across pages.

    ``fetch_page`` is called as ``fetch_page(limit, starting_after)`` and must
    return ``(items, next_cursor_or_None)``.
    """
    cursor = None
    while True:
        items, cursor = fetch_page(limit, cursor)
        yield from items
        if not cursor:
            return
