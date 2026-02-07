import sqlite3
import json

def update_ship(id, ship_data):
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        db_cursor.execute(
            """
            UPDATE Ship
                SET
                    name = ?,
                    hauler_id = ?
            WHERE id = ?
            """,
            (ship_data['name'], ship_data['hauler_id'], id)
        )

        rows_affected = db_cursor.rowcount

    return True if rows_affected > 0 else False

def delete_ship(pk):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        DELETE FROM Ship WHERE id = ?
        """, (pk,)
        )
        number_of_rows_deleted = db_cursor.rowcount

    return True if number_of_rows_deleted > 0 else False


def list_ships(url):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        # Check if "_expand" exists in the query parameters
        if "_expand" in url['query_params']:
            db_cursor.execute("""
            SELECT
                s.id,
                s.name,
                s.hauler_id,
                h.id haulerId,
                h.name haulerName,
                h.dock_id
            FROM Ship s
            JOIN Hauler h
                ON h.id = s.hauler_id
            """)
            query_results = db_cursor.fetchall()

            ships = []
            for row in query_results:
                # 1. Build the nested hauler dictionary
                hauler = {
                    "id": row['haulerId'],
                    "name": row['haulerName'],
                    "dock_id": row["dock_id"]
                }
                # 2. Build the ship dictionary including the hauler
                ship = {
                    "id": row['id'],
                    "name": row['name'],
                    "hauler_id": row["hauler_id"],
                    "hauler": hauler
                }
                ships.append(ship)
        else:
            # Existing simple logic for unexpanded ships
            db_cursor.execute("""
            SELECT s.id, s.name, s.hauler_id FROM Ship s
            """)
            query_results = db_cursor.fetchall()
            ships = [dict(row) for row in query_results]

        return json.dumps(ships)

def retrieve_ship(pk, url):
    with sqlite3.connect("./shipping.db") as conn:
        conn.row_factory = sqlite3.Row
        db_cursor = conn.cursor()

        if "_expand" in url['query_params']:
            db_cursor.execute("""
            SELECT
                s.id, s.name, s.hauler_id,
                h.id haulerId, h.name haulerName, h.dock_id
            FROM Ship s
            JOIN Hauler h ON h.id = s.hauler_id
            WHERE s.id = ?
            """, (pk,))
            row = db_cursor.fetchone()

            hauler = {
                "id": row['haulerId'],
                "name": row['haulerName'],
                "dock_id": row["dock_id"]
            }
            ship = {
                "id": row['id'],
                "name": row['name'],
                "hauler_id": row["hauler_id"],
                "hauler": hauler
            }
            return json.dumps(ship)
        else:
            db_cursor.execute("SELECT id, name, hauler_id FROM Ship WHERE id = ?", (pk,))
            row = db_cursor.fetchone()
            return json.dumps(dict(row))

def create_ship(ship_data):
    # Open a connection to the database
    with sqlite3.connect("./shipping.db") as conn:
        db_cursor = conn.cursor()

        # Write the SQL query to get the information you want
        db_cursor.execute("""
        INSERT INTO Ship (name, hauler_id)
        VALUES (?, ?)
        """, (ship_data['name'], ship_data['hauler_id']))

        # Get the ID of the newly created row
        new_id = db_cursor.lastrowid

        # Serialize Python dictionary to JSON encoded string
        serialized_id = json.dumps({"id": new_id})

    return serialized_id
