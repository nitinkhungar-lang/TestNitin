"""Database migrations."""
import sqlite3

def run_migrations(conn: sqlite3.Connection) -> None:
    """Run all schema migrations."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            id TEXT PRIMARY KEY,
            
            
            
            
            version INTEGER,
            last_sequence_number INTEGER,
            created_at TEXT,
            updated_at TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_event (
            id TEXT PRIMARY KEY,
            ledger_id TEXT,
            sequence_number INTEGER,
            schema_version INTEGER,
            event_type_code TEXT,
            business_activity_id TEXT,
            account_id TEXT,
            asset_id TEXT,
            event_date TEXT,
            amount TEXT,
            direction TEXT,
            quantity TEXT,
            description TEXT,
            created_at TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_activity (
            id TEXT PRIMARY KEY,
            activity_type_code TEXT,
            activity_date TEXT,
            settlement_date TEXT,
            description TEXT,
            evidence_ids TEXT,
            account_id TEXT,
            asset_id TEXT,
            quantity TEXT,
            price_per_unit TEXT,
            total_amount TEXT,
            typed_charges TEXT,
            is_reversal INTEGER,
            reverses_activity_id TEXT,
            status TEXT,
            created_at TEXT,
            schema_version INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence (
            id TEXT PRIMARY KEY,
            evidence_type TEXT,
            source_institution_id TEXT,
            document_date TEXT,
            received_date TEXT,
            file_reference TEXT,
            file_hash TEXT,
            file_size_bytes INTEGER,
            raw_content TEXT,
            version INTEGER,
            supersedes_id TEXT,
            created_at TEXT,
            schema_version INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asset (
            id TEXT PRIMARY KEY,
            asset_type_code TEXT,
            exchange TEXT,
            typed_metadata TEXT,
            name TEXT,
            symbol TEXT,
            isin TEXT,
            currency_code TEXT,
            institution_id TEXT,
            is_active INTEGER,
            created_at TEXT,
            updated_at TEXT,
            schema_version INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS financial_account (
            id TEXT PRIMARY KEY,
            account_type_code TEXT,
            opened_date TEXT,
            closed_date TEXT,
            typed_metadata TEXT,
            name TEXT,
            institution_id TEXT,
            currency_code TEXT,
            account_number TEXT,
            is_active INTEGER,
            created_at TEXT,
            updated_at TEXT,
            schema_version INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS institution (
            id TEXT PRIMARY KEY,
            name TEXT,
            institution_type TEXT,
            country_code TEXT,
            website TEXT,
            customer_care_email TEXT,
            customer_care_phone TEXT,
            regulatory_id TEXT,
            is_active INTEGER,
            created_at TEXT,
            updated_at TEXT,
            schema_version INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lot (
            id TEXT PRIMARY KEY,
            asset_id TEXT,
            account_id TEXT,
            acquisition_date TEXT,
            original_quantity TEXT,
            remaining_quantity TEXT,
            cost_per_unit TEXT,
            status TEXT,
            source_activity_id TEXT,
            corporate_action_id TEXT,
            parent_lot_id TEXT,
            created_at TEXT,
            updated_at TEXT,
            schema_version INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS corporate_action (
            id TEXT PRIMARY KEY,
            asset_id TEXT,
            action_type TEXT,
            record_date TEXT,
            effective_date TEXT,
            split_ratio TEXT,
            new_asset_id TEXT,
            exchange_ratio TEXT,
            description TEXT,
            evidence_ids TEXT,
            created_at TEXT,
            schema_version INTEGER
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS exchange_rate (
            id TEXT PRIMARY KEY,
            from_currency TEXT,
            to_currency TEXT,
            rate TEXT,
            effective_date TEXT,
            source TEXT
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS market_price (
            id TEXT PRIMARY KEY,
            asset_id TEXT,
            date TEXT,
            price TEXT,
            source TEXT
        );
    """)
    conn.commit()
