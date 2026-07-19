"""Unit tests for NFP domain entities."""
import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from nfp.core.clock import Clock
from nfp.core.exceptions import (
    EvidenceRequiredError,
    InsufficientLotQuantityError,
    InvalidPanError,
    LedgerSequenceError,
)
from nfp.core.metadata import SplitRatio
from nfp.core.money import Money
from nfp.core.quantity import Quantity
from nfp.domain.business_activity import BusinessActivity
from nfp.domain.corporate_action import CorporateAction, CorporateActionType
from nfp.domain.evidence import Evidence
from nfp.domain.financial_account import FinancialAccount
from nfp.domain.financial_event import FinancialEvent
from nfp.domain.institution import Institution, InstitutionType
from nfp.domain.ledger import Ledger
from nfp.domain.lot import Lot, LotStatus
from nfp.domain.ownership import Ownership
from nfp.domain.person import Person
from nfp.events.domain_events import ActivityRecorded, DomainEvent
from nfp.events.event_bus import DomainEventBus


class DummyClock(Clock):
    def now(self) -> datetime:
        return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def today(self) -> date:
        return date(2024, 1, 1)


def test_person_validate_pan_format():
    Person.validate_pan_format("ABCDE1234F")
    
    with pytest.raises(InvalidPanError):
        Person.validate_pan_format("invalid")
        
    with pytest.raises(InvalidPanError):
        Person.validate_pan_format("abcde1234f")


def test_person_pan_masked():
    person = Person(
        id=uuid4(),
        name="Test User",
        pan_encrypted=b"enc",
        date_of_birth=date(1990, 1, 1),
        country_code="IN",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    assert person.pan_masked("ABCDE1234F") == "ABCDE****F"


def test_ownership_creation():
    # valid 100%
    Ownership(
        id=uuid4(),
        person_id=uuid4(),
        asset_id=uuid4(),
        account_id=uuid4(),
        ownership_percentage=Decimal("100"),
        started_date=date(2024, 1, 1),
        ended_date=None,
        created_at=datetime.now(),
    )

    # valid 50%
    Ownership(
        id=uuid4(),
        person_id=uuid4(),
        asset_id=uuid4(),
        account_id=uuid4(),
        ownership_percentage=Decimal("50.5"),
        started_date=date(2024, 1, 1),
        ended_date=None,
        created_at=datetime.now(),
    )

    with pytest.raises(ValueError):
        Ownership(
            id=uuid4(),
            person_id=uuid4(),
            asset_id=uuid4(),
            account_id=uuid4(),
            ownership_percentage=Decimal("0"),
            started_date=date(2024, 1, 1),
            ended_date=None,
            created_at=datetime.now(),
        )

    with pytest.raises(ValueError):
        Ownership(
            id=uuid4(),
            person_id=uuid4(),
            asset_id=uuid4(),
            account_id=uuid4(),
            ownership_percentage=Decimal("101"),
            started_date=date(2024, 1, 1),
            ended_date=None,
            created_at=datetime.now(),
        )


def test_evidence_creation():
    Evidence(
        id=uuid4(),
        evidence_type="BROKER_CONTRACT_NOTE",
        source_institution_id=uuid4(),
        document_date=date(2024, 1, 1),
        received_date=date(2024, 1, 1),
        file_reference="path/to/file",
        file_hash="hash",
        file_size_bytes=100,
        raw_content=None,
        version=1,
        supersedes_id=None,
        created_at=datetime.now(),
    )

    with pytest.raises(ValueError):
        Evidence(
            id=uuid4(),
            evidence_type="INVALID_TYPE",
            source_institution_id=uuid4(),
            document_date=date(2024, 1, 1),
            received_date=date(2024, 1, 1),
            file_reference="path/to/file",
            file_hash="hash",
            file_size_bytes=100,
            raw_content=None,
            version=1,
            supersedes_id=None,
            created_at=datetime.now(),
        )

    with pytest.raises(ValueError):
        Evidence(
            id=uuid4(),
            evidence_type="BROKER_CONTRACT_NOTE",
            source_institution_id=uuid4(),
            document_date=date(2024, 1, 1),
            received_date=date(2024, 1, 1),
            file_reference="path/to/file",
            file_hash="hash",
            file_size_bytes=100,
            raw_content=None,
            version=0,
            supersedes_id=None,
            created_at=datetime.now(),
        )


def test_business_activity_creation():
    act = BusinessActivity(
        id=uuid4(),
        activity_type_code="BUY",
        activity_date=date(2024, 1, 1),
        settlement_date=date(2024, 1, 2),
        description="Buy shares",
        evidence_ids=[uuid4()],
        account_id=uuid4(),
        asset_id=uuid4(),
        quantity=Quantity(Decimal("10"), "UNITS"),
        price_per_unit=Money(Decimal("100"), "INR"),
        total_amount=Money(Decimal("1000"), "INR"),
        typed_charges=None,
        is_reversal=False,
        reverses_activity_id=None,
        status="CONFIRMED",
        created_at=datetime.now(),
    )

    with pytest.raises(EvidenceRequiredError):
        BusinessActivity(
            id=uuid4(),
            activity_type_code="BUY",
            activity_date=date(2024, 1, 1),
            settlement_date=date(2024, 1, 2),
            description="Buy shares",
            evidence_ids=[],
            account_id=uuid4(),
            asset_id=uuid4(),
            quantity=Quantity(Decimal("10"), "UNITS"),
            price_per_unit=Money(Decimal("100"), "INR"),
            total_amount=Money(Decimal("1000"), "INR"),
            typed_charges=None,
            is_reversal=False,
            reverses_activity_id=None,
            status="CONFIRMED",
            created_at=datetime.now(),
        )

    with pytest.raises(ValueError):
        BusinessActivity(
            id=uuid4(),
            activity_type_code="BUY",
            activity_date=date(2024, 1, 2),
            settlement_date=date(2024, 1, 1),
            description="Buy shares",
            evidence_ids=[uuid4()],
            account_id=uuid4(),
            asset_id=uuid4(),
            quantity=Quantity(Decimal("10"), "UNITS"),
            price_per_unit=Money(Decimal("100"), "INR"),
            total_amount=Money(Decimal("1000"), "INR"),
            typed_charges=None,
            is_reversal=False,
            reverses_activity_id=None,
            status="CONFIRMED",
            created_at=datetime.now(),
        )

    with pytest.raises(ValueError):
        BusinessActivity(
            id=uuid4(),
            activity_type_code="BUY",
            activity_date=date(2024, 1, 1),
            settlement_date=date(2024, 1, 2),
            description="Buy shares",
            evidence_ids=[uuid4()],
            account_id=uuid4(),
            asset_id=uuid4(),
            quantity=Quantity(Decimal("10"), "UNITS"),
            price_per_unit=Money(Decimal("100"), "INR"),
            total_amount=Money(Decimal("1000"), "INR"),
            typed_charges=None,
            is_reversal=False,
            reverses_activity_id=None,
            status="INVALID",
            created_at=datetime.now(),
        )

    act.mark_reversed()
    assert act.status == "REVERSED"


def test_financial_event_creation():
    ev = FinancialEvent(
        id=uuid4(),
        ledger_id=uuid4(),
        sequence_number=1,
        schema_version=1,
        event_type_code="EVT",
        business_activity_id=uuid4(),
        account_id=uuid4(),
        asset_id=uuid4(),
        event_date=date(2024, 1, 1),
        amount=Money(Decimal("100"), "INR"),
        direction="DEBIT",
        quantity=None,
        description="test",
        created_at=datetime.now(),
    )

    with pytest.raises(ValueError):
        FinancialEvent(
            id=uuid4(),
            ledger_id=uuid4(),
            sequence_number=1,
            schema_version=1,
            event_type_code="EVT",
            business_activity_id=uuid4(),
            account_id=uuid4(),
            asset_id=uuid4(),
            event_date=date(2024, 1, 1),
            amount=Money(Decimal("100"), "INR"),
            direction="INVALID",
            quantity=None,
            description="test",
            created_at=datetime.now(),
        )
        
    with pytest.raises(Exception): # frozen dataclass
        ev.amount = Money(Decimal("200"), "INR")

    with pytest.raises(ValueError):
        FinancialEvent(
            id=uuid4(),
            ledger_id=uuid4(),
            sequence_number=1,
            schema_version=1,
            event_type_code="EVT",
            business_activity_id=uuid4(),
            account_id=uuid4(),
            asset_id=uuid4(),
            event_date=date(2024, 1, 1),
            amount=Money(Decimal("-100"), "INR"),
            direction="DEBIT",
            quantity=None,
            description="test",
            created_at=datetime.now(),
        )


def test_lot():
    lot = Lot(
        id=uuid4(),
        asset_id=uuid4(),
        account_id=uuid4(),
        acquisition_date=date(2024, 1, 1),
        original_quantity=Quantity(Decimal("100"), "UNITS"),
        remaining_quantity=Quantity(Decimal("100"), "UNITS"),
        cost_per_unit=Money(Decimal("10"), "INR"),
        status=LotStatus.OPEN,
        source_activity_id=uuid4(),
        corporate_action_id=None,
        parent_lot_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    assert lot.total_cost == Money(Decimal("1000"), "INR")
    assert lot.remaining_cost == Money(Decimal("1000"), "INR")

    res = lot.consume(Quantity(Decimal("40"), "UNITS"), datetime.now())
    assert lot.status == LotStatus.PARTIALLY_CONSUMED
    assert lot.remaining_quantity == Quantity(Decimal("60"), "UNITS")
    assert lot.remaining_cost == Money(Decimal("600"), "INR")
    assert res.quantity_consumed == Quantity(Decimal("40"), "UNITS")
    assert res.cost_consumed == Money(Decimal("400"), "INR")

    res2 = lot.consume(Quantity(Decimal("60"), "UNITS"), datetime.now())
    assert lot.status == LotStatus.CONSUMED
    assert lot.remaining_quantity == Quantity(Decimal("0"), "UNITS")
    assert lot.remaining_cost == Money(Decimal("0"), "INR")
    assert res2.quantity_consumed == Quantity(Decimal("60"), "UNITS")
    assert res2.cost_consumed == Money(Decimal("600"), "INR")

    with pytest.raises(InsufficientLotQuantityError):
        lot.consume(Quantity(Decimal("1"), "UNITS"), datetime.now())

    # apply_split
    lot2 = Lot(
        id=uuid4(),
        asset_id=uuid4(),
        account_id=uuid4(),
        acquisition_date=date(2024, 1, 1),
        original_quantity=Quantity(Decimal("100"), "UNITS"),
        remaining_quantity=Quantity(Decimal("100"), "UNITS"),
        cost_per_unit=Money(Decimal("10"), "INR"),
        status=LotStatus.OPEN,
        source_activity_id=uuid4(),
        corporate_action_id=None,
        parent_lot_id=None,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    lot2.apply_split(Decimal("2"), Decimal("2"), datetime.now())
    assert lot2.original_quantity == Quantity(Decimal("200"), "UNITS")
    assert lot2.remaining_quantity == Quantity(Decimal("200"), "UNITS")
    assert lot2.cost_per_unit == Money(Decimal("5"), "INR")
    assert lot2.status == LotStatus.ADJUSTED


def test_institution():
    inst = Institution(
        id=uuid4(),
        name="Test Bank",
        institution_type=InstitutionType.BANK,
        country_code="IN",
        website=None,
        customer_care_email=None,
        customer_care_phone=None,
        regulatory_id=None,
        is_active=True,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )

    assert inst.is_active is True
    t1 = datetime.now()
    inst.deactivate(t1)
    assert inst.is_active is False
    assert inst.updated_at == t1
    
    t2 = datetime.now()
    inst.reactivate(t2)
    assert inst.is_active is True
    assert inst.updated_at == t2


def test_ledger():
    ledger = Ledger(
        id=uuid4(),
        version=1,
        last_sequence_number=10,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    clock = DummyClock()
    
    ev1 = FinancialEvent(
        id=uuid4(),
        ledger_id=ledger.id,
        sequence_number=1, # arbitrary, to be replaced
        schema_version=1,
        event_type_code="EVT",
        business_activity_id=uuid4(),
        account_id=uuid4(),
        asset_id=None,
        event_date=date(2024, 1, 1),
        amount=Money(Decimal("10"), "INR"),
        direction="DEBIT",
        quantity=None,
        description="test",
        created_at=datetime.now(),
    )
    ev2 = FinancialEvent(
        id=uuid4(),
        ledger_id=ledger.id,
        sequence_number=1, # arbitrary
        schema_version=1,
        event_type_code="EVT",
        business_activity_id=uuid4(),
        account_id=uuid4(),
        asset_id=None,
        event_date=date(2024, 1, 1),
        amount=Money(Decimal("20"), "INR"),
        direction="CREDIT",
        quantity=None,
        description="test2",
        created_at=datetime.now(),
    )
    
    sequenced = ledger.prepare_events([ev1, ev2], clock)
    assert sequenced[0].sequence_number == 11
    assert sequenced[1].sequence_number == 12
    assert ledger.last_sequence_number == 12
    assert ledger.version == 2
    
    with pytest.raises(LedgerSequenceError):
        ledger.prepare_events([], clock)


def test_domain_event_bus():
    bus = DomainEventBus()
    calls = []
    
    def handler(ev):
        calls.append(ev)
        
    bus.subscribe(ActivityRecorded, handler)
    
    ev1 = ActivityRecorded(
        event_id=uuid4(),
        occurred_at=datetime.now(),
        activity_id=uuid4(),
        activity_type_code="TEST",
        activity_date=date(2024,1,1)
    )
    
    bus.publish(ev1)
    assert len(calls) == 1
    assert calls[0] == ev1
    
    ev2 = ActivityRecorded(
        event_id=uuid4(),
        occurred_at=datetime.now(),
        activity_id=uuid4(),
        activity_type_code="TEST2",
        activity_date=date(2024,1,1)
    )
    bus.publish_all([ev2])
    assert len(calls) == 2
    assert calls[1] == ev2

    # unsubscribed
    class OtherEvent(DomainEvent):
        pass
    bus.publish(OtherEvent(event_id=uuid4(), occurred_at=datetime.now()))
    assert len(calls) == 2
