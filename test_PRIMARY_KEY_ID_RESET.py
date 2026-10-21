from database.database import get_connection

with get_connection() as connection:
    connection.execute("DELETE FROM sqlite_sequence")