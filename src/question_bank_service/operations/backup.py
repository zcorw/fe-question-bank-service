import argparse
import shutil
from datetime import datetime
from pathlib import Path


def backup_database(
    database_path: Path,
    *,
    backup_dir: Path | None = None,
    timestamp: str | None = None,
) -> Path:
    if not database_path.is_file():
        raise FileNotFoundError(f"Database file was not found: {database_path}")

    effective_timestamp = timestamp or datetime.now().strftime("%Y%m%d%H%M%S")
    destination_dir = backup_dir or database_path.parent
    destination_dir.mkdir(parents=True, exist_ok=True)
    backup_path = destination_dir / f"{database_path.name}.{effective_timestamp}.bak"
    shutil.copy2(database_path, backup_path)
    return backup_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a timestamped SQLite backup.")
    parser.add_argument("--db-path", type=Path, default=Path("data/fe_siken_questions.sqlite"))
    parser.add_argument("--backup-dir", type=Path)
    args = parser.parse_args()

    backup_path = backup_database(args.db_path, backup_dir=args.backup_dir)
    print(backup_path)


if __name__ == "__main__":
    main()
