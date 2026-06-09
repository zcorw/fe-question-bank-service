import sqlite3
from pathlib import Path


def open_sqlite_connection(database_path: Path | str, *, read_only: bool) -> sqlite3.Connection:
    path = Path(database_path)
    if read_only:
        uri = f"file:{path.resolve().as_posix()}?mode=ro"
        connection = sqlite3.connect(uri, uri=True)
    else:
        connection = sqlite3.connect(path)

    connection.row_factory = sqlite3.Row
    return connection
