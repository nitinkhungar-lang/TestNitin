"""Person domain entity for NFP.

Single-user system: only one Person exists.
PAN is stored encrypted (Constitution C10).
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from uuid import UUID

from nfp.core.exceptions import InvalidPanError

_PAN_PATTERN = re.compile(r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$')


@dataclass
class Person:
    """The individual whose finances are tracked.

    Single-user system: exactly one Person exists.
    PAN is stored as Fernet-encrypted bytes (Constitution C10).
    The API exposes only pan_masked, never plaintext PAN.

    Attributes:
        id: Unique identifier.
        name: Full name.
        pan_encrypted: Fernet-encrypted PAN bytes. None if not set.
        date_of_birth: Optional date of birth.
        country_code: ISO 3166-1 alpha-2 country code. Default 'IN'.
        created_at: UTC creation timestamp.
        updated_at: UTC last-update timestamp.
        schema_version: Schema version for evolution tracking.
    """

    id: UUID
    name: str
    pan_encrypted: bytes | None
    date_of_birth: date | None
    country_code: str
    created_at: datetime
    updated_at: datetime
    schema_version: int = 1

    def pan_masked(self, decrypted_pan: str) -> str:
        """Return masked PAN for display.

        Args:
            decrypted_pan: Plaintext PAN (decrypted externally by PanEncryptor).

        Returns:
            Masked string, e.g. 'ABCDE1234F' -> 'ABCDE****F'.
        """
        return decrypted_pan[:5] + "****" + decrypted_pan[-1]

    @staticmethod
    def validate_pan_format(pan: str) -> None:
        """Validate PAN format before encryption.

        Args:
            pan: Plaintext PAN to validate.

        Raises:
            InvalidPanError: If format does not match [A-Z]{5}[0-9]{4}[A-Z].
        """
        if not _PAN_PATTERN.match(pan):
            raise InvalidPanError(f"Invalid PAN format: {pan!r}. Expected [A-Z]{{5}}[0-9]{{4}}[A-Z]")
