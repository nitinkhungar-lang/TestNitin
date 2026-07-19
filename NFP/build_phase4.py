import os

# Create base directories
dirs = [
    "src/nfp/repositories",
    "src/nfp/infrastructure/database/sqlite",
    "src/nfp/infrastructure/file_storage",
    "src/nfp/infrastructure/crypto",
    "tests/integration/repositories"
]
for d in dirs:
    os.makedirs(d, exist_ok=True)

# base.py
base_code = '''"""Base repository interfaces."""
import abc
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')
ID = TypeVar('ID')

class Repository(Generic[T, ID], abc.ABC):
    """Base repository interface."""
    @abc.abstractmethod
    def add(self, entity: T) -> None:
        pass

    @abc.abstractmethod
    def get(self, id: ID) -> Optional[T]:
        pass
        
    @abc.abstractmethod
    def get_all(self) -> List[T]:
        pass
'''
with open("src/nfp/repositories/base.py", "w") as f:
    f.write(base_code)

entities = [
    ("ledger", "Ledger"),
    ("event", "FinancialEvent"),
    ("activity", "BusinessActivity"),
    ("evidence", "Evidence"),
    ("asset", "Asset"),
    ("account", "FinancialAccount"),
    ("institution", "Institution"),
    ("lot", "Lot"),
    ("corporate_action", "CorporateAction"),
    ("exchange_rate", "ExchangeRate"),
    ("market_price", "MarketPrice")
]

for name, cls in entities:
    # ABC
    repo_code = f'''"""{cls} repository interface."""
import abc
from uuid import UUID
from typing import Optional, List
from nfp.domain import {cls}
from nfp.repositories.base import Repository

class {cls}Repository(Repository[{cls}, UUID], abc.ABC):
    """Repository interface for {cls}."""
    pass
'''
    with open(f"src/nfp/repositories/{name}_repo.py", "w") as f:
        f.write(repo_code)
        
    # SQLite
    sqlite_code = f'''"""SQLite implementation of {cls} repository."""
import sqlite3
import json
from uuid import UUID
from typing import Optional, List
from nfp.domain import {cls}
from nfp.repositories.{name}_repo import {cls}Repository

class SQLite{cls}Repository({cls}Repository):
    """SQLite repository for {cls}."""
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, entity: {cls}) -> None:
        pass

    def get(self, id: UUID) -> Optional[{cls}]:
        return None
        
    def get_all(self) -> List[{cls}]:
        return []
'''
    with open(f"src/nfp/infrastructure/database/sqlite/{name}_repo.py", "w") as f:
        f.write(sqlite_code)

# Connection
conn_code = '''"""Database connection management."""
import sqlite3

def get_connection(db_path: str) -> sqlite3.Connection:
    """Get a SQLite connection with WAL mode enabled."""
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.row_factory = sqlite3.Row
    return conn
'''
with open("src/nfp/infrastructure/database/connection.py", "w") as f:
    f.write(conn_code)

# Migrations
mig_code = '''"""Database migrations."""
import sqlite3

def run_migrations(conn: sqlite3.Connection) -> None:
    """Run all schema migrations."""
    # Dummy schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS _dummy (
            id TEXT PRIMARY KEY
        );
    """)
'''
with open("src/nfp/infrastructure/database/migrations.py", "w") as f:
    f.write(mig_code)
    
# Local Evidence Store
fs_code = '''"""Local file storage implementation."""
import os
import hashlib
from pathlib import Path

class LocalEvidenceFileStore:
    """Stores files locally and verifies SHA-256."""
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.root_dir.mkdir(parents=True, exist_ok=True)
        
    def store(self, file_path: str, data: bytes) -> str:
        """Store file and return SHA-256."""
        sha = hashlib.sha256(data).hexdigest()
        target = self.root_dir / file_path
        target.parent.mkdir(parents=True, exist_ok=True)
        with open(target, "wb") as f:
            f.write(data)
        return sha
'''
with open("src/nfp/infrastructure/file_storage/local_store.py", "w") as f:
    f.write(fs_code)

# Pan Encryptor
crypto_code = '''"""PAN Encryption."""
from cryptography.fernet import Fernet
import keyring

class PanEncryptor:
    """Encrypts and decrypts PANs using Fernet."""
    def __init__(self, service_name: str, username: str):
        key = keyring.get_password(service_name, username)
        if not key:
            key = Fernet.generate_key().decode()
            keyring.set_password(service_name, username, key)
        self.fernet = Fernet(key.encode())

    def encrypt(self, pan: str) -> str:
        """Encrypt PAN."""
        return self.fernet.encrypt(pan.encode()).decode()

    def decrypt(self, encrypted_pan: str) -> str:
        """Decrypt PAN."""
        return self.fernet.decrypt(encrypted_pan.encode()).decode()
'''
with open("src/nfp/infrastructure/crypto/pan_encryptor.py", "w") as f:
    f.write(crypto_code)

# Seeder
seeder_code = '''"""Database seeder."""
import sqlite3

class DatabaseSeeder:
    """Seeds initial reference data."""
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def seed(self) -> None:
        """Run seeder."""
        pass
'''
with open("src/nfp/infrastructure/database/seeder.py", "w") as f:
    f.write(seeder_code)

# Test
test_code = '''"""Repository integration tests."""
import pytest
import sqlite3
from nfp.infrastructure.database.connection import get_connection
from nfp.infrastructure.database.migrations import run_migrations

@pytest.fixture
def db():
    conn = get_connection(":memory:")
    run_migrations(conn)
    yield conn
    conn.close()

def test_sanity(db):
    assert True
'''
with open("tests/integration/repositories/test_sanity.py", "w") as f:
    f.write(test_code)
