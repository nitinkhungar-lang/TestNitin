"""Local file storage implementation."""
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
        
    def retrieve(self, file_path: str, expected_hash: str) -> bytes:
        """Retrieve file and verify SHA-256."""
        target = self.root_dir / file_path
        with open(target, "rb") as f:
            data = f.read()
        sha = hashlib.sha256(data).hexdigest()
        if sha != expected_hash:
            raise ValueError(f"Hash mismatch: expected {expected_hash}, got {sha}")
        return data
