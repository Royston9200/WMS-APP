from contextlib import contextmanager
from modules.db import get_connection


@contextmanager
def db_cursor(dict_rows=True):
    """Contextmanager voor DB-verbindingen met automatische commit/rollback."""
    conn = get_connection()
    cur = conn.cursor(dictionary=dict_rows)
    try:
        yield conn, cur
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_link(barcode: str, location: str, user_id: int) -> bool:
    """
    Maakt een koppeling tussen barcode en locatie aan in linked_items.
    Retourneert True als het een nieuwe koppeling was, False als ze al bestond.
    """
    with db_cursor() as (conn, cur):
        cur.execute(
            "SELECT 1 FROM linked_items WHERE barcode=%s AND location=%s LIMIT 1",
            (barcode, location),
        )
        if cur.fetchone():
            return False
        cur.execute(
            """
            INSERT INTO linked_items (barcode, location, user_id)
            VALUES (%s, %s, %s)
            """,
            (barcode, location, user_id),
        )
        return True


def list_links(location: str | None = None, limit: int = 500):
    """Geeft de laatste gekoppelde items terug, optioneel gefilterd op locatie."""
    sql = """
        SELECT li.id, li.barcode, li.location, li.linked_at, u.username
        FROM linked_items li
        LEFT JOIN sec_users u ON u.user_id = li.user_id
    """
    args = []
    if location:
        sql += " WHERE li.location=%s"
        args.append(location)
    sql += " ORDER BY li.linked_at DESC, li.id DESC LIMIT %s"
    args.append(limit)

    with db_cursor() as (conn, cur):
        cur.execute(sql, tuple(args))
        return cur.fetchall()


def remove_link(id: int = None, barcode: str = None, location: str = None):
    """Verwijdert een koppeling uit linked_items."""
    with db_cursor() as (conn, cur):
        if id:
            cur.execute("DELETE FROM linked_items WHERE id=%s", (id,))
        elif barcode and location:
            cur.execute(
                "DELETE FROM linked_items WHERE barcode=%s AND location=%s",
                (barcode, location),
            )
        elif barcode:
            cur.execute("DELETE FROM linked_items WHERE barcode=%s", (barcode,))
