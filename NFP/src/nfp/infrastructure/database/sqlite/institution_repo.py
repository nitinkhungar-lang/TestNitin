"""SQLite implementation of Institution repository."""
import sqlite3
import json
import uuid
from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, get_type_hints, Any
from enum import Enum
import dataclasses

from nfp.domain import Institution
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.domain.institution import InstitutionType
from nfp.repositories.institution_repo import InstitutionRepository

def to_db(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, Money):
        return f"{value.amount} {value.currency_code}"
    if isinstance(value, Quantity):
        return f"{value.value} {value.unit}"
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, (list, dict)):
        return json.dumps(value, default=str)
    if dataclasses.is_dataclass(value):
        return json.dumps(dataclasses.asdict(value), default=str)
    return value

def from_db(value: Any, field_type: Any) -> Any:
    if value is None:
        return None
        
    type_str = str(field_type)
    
    if "list" in type_str or "dict" in type_str:
        parsed = json.loads(value)
        if "UUID" in type_str and isinstance(parsed, list):
            return [UUID(x) for x in parsed]
        return parsed
        
    if "UUID" in type_str:
        return UUID(value)
    if "datetime" in type_str:
        return datetime.fromisoformat(value)
    if "date" in type_str:
        return date.fromisoformat(value.split("T")[0])
    if "Money" in type_str:
        amt, cur = value.split(" ")
        return Money(Decimal(amt), cur)
    if "Quantity" in type_str:
        amt, unit = value.split(" ")
        return Quantity(Decimal(amt), unit)
    if "Decimal" in type_str:
        return Decimal(value)
    if "bool" in type_str:
        return bool(value)
        
    origin = getattr(field_type, "__origin__", field_type)
    
    if "Union" in type_str or "Optional" in type_str or "|" in type_str:
        args = getattr(field_type, "__args__", [])
        if args:
            for t in args:
                if type(None) == t:
                    continue
                try:
                    return from_db(value, t)
                except:
                    pass

    try:
        if issubclass(origin, Enum):
            return origin(value)
    except:
        pass
        
    try:
        if origin in (int, str, float):
            return origin(value)
    except:
        pass

    return value

class SQLiteInstitutionRepository(InstitutionRepository):
    """SQLite repository for Institution."""
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn

    def add(self, entity: Institution) -> None:
        fields = [f.name for f in dataclasses.fields(Institution) if not f.name.startswith('_')]
        cols = ", ".join(fields)
        placeholders = ", ".join(["?"] * len(fields))
        values = [to_db(getattr(entity, f)) for f in fields]
        
        # If it doesn't have an ID, we might have an auto-increment or just composite key
        if "id" not in fields:
            # Check if our DB expects an ID
            try:
                self.conn.execute(
                    f"INSERT OR REPLACE INTO institution (id, {cols}) VALUES (?, {placeholders})",
                    [str(uuid.uuid4())] + values
                )
            except sqlite3.OperationalError:
                # No id column
                self.conn.execute(
                    f"INSERT OR REPLACE INTO institution ({cols}) VALUES ({placeholders})",
                    values
                )
        else:
            self.conn.execute(
                f"INSERT OR REPLACE INTO institution ({cols}) VALUES ({placeholders})",
                values
            )
        self.conn.commit()

    def get(self, id: UUID) -> Optional[Institution]:
        fields = [f.name for f in dataclasses.fields(Institution) if not f.name.startswith('_')]
        if "id" not in fields:
            return None # Cannot get by ID
            
        cursor = self.conn.execute(f"SELECT * FROM institution WHERE id = ?", (str(id),))
        row = cursor.fetchone()
        if not row:
            return None
            
        hints = get_type_hints(Institution)
        kwargs = {}
        for field in dataclasses.fields(Institution):
            if field.name.startswith('_'): continue
            val = row[field.name]
            kwargs[field.name] = from_db(val, hints.get(field.name, field.type))
            
        return Institution(**kwargs)
        
    def get_all(self) -> List[Institution]:
        cursor = self.conn.execute(f"SELECT * FROM institution")
        rows = cursor.fetchall()
        hints = get_type_hints(Institution)
        
        results = []
        for row in rows:
            kwargs = {}
            for field in dataclasses.fields(Institution):
                if field.name.startswith('_'): continue
                val = row[field.name]
                kwargs[field.name] = from_db(val, hints.get(field.name, field.type))
            results.append(Institution(**kwargs))
        return results
