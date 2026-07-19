"""Database seeder."""
import sqlite3

class DatabaseSeeder:
    """Seeds initial reference data."""
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def seed(self) -> None:
        """Run seeder."""
        pass
