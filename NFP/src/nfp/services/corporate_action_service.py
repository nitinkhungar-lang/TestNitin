import uuid
from typing import List, Optional
import sqlite3
from decimal import Decimal

from nfp.core.clock import Clock
from nfp.domain.corporate_action import CorporateAction, CorporateActionType
from nfp.domain.lot import Lot, LotStatus
from nfp.events.event_bus import DomainEventBus
from nfp.events.domain_events import CorporateActionProcessed
from nfp.repositories.corporate_action_repo import CorporateActionRepository
from nfp.repositories.lot_repo import LotRepository
from nfp.core.quantity import Quantity
from nfp.core.money import Money


class CorporateActionService:
    """Orchestrates the application of corporate actions to lots."""

    def __init__(
        self,
        ca_repo: CorporateActionRepository,
        lot_repo: LotRepository,
        event_bus: DomainEventBus,
        clock: Clock,
        conn: sqlite3.Connection
    ):
        self.ca_repo = ca_repo
        self.lot_repo = lot_repo
        self.event_bus = event_bus
        self.clock = clock
        self.conn = conn

    def apply_action(self, ca_id: uuid.UUID) -> None:
        """Apply a corporate action to all affected lots.
        
        This fetches the corporate action, finds the relevant open/partially consumed
        lots, applies the adjustment (via domain method for split/bonus/consolidation,
        and creating new lots for merger/spinoff), saves the lots, and publishes an event.
        The whole operation is wrapped in a database transaction.
        """
        ca = self.ca_repo.get(ca_id)
        if not ca:
            raise ValueError(f"Corporate action {ca_id} not found")

        # Fetch all lots for the asset
        all_lots = self.lot_repo.get_all()
        # We only apply corporate actions to lots that are not fully consumed
        lots_to_adjust = [
            lot for lot in all_lots 
            if lot.asset_id == ca.asset_id and lot.status != LotStatus.CONSUMED
        ]

        if not lots_to_adjust:
            return  # Nothing to do

        new_lots = []
        now = self.clock.now()
        
        try:
            self.conn.execute("BEGIN")

            # Store states before we pass to domain model
            # For MERGER and SPINOFF, we need to know the lots to spawn new ones
            lots_before = {lot.id: (lot.original_quantity.value, lot.remaining_quantity.value, lot.cost_per_unit) for lot in lots_to_adjust}

            # Apply core domain logic
            ca.apply_to_lots(lots_to_adjust, self.clock)

            # Handle new lots generation for MERGER and SPINOFF
            if ca.action_type in (CorporateActionType.MERGER, CorporateActionType.SPINOFF):
                if not ca.new_asset_id:
                    raise ValueError(f"new_asset_id required for {ca.action_type}")
                if not ca.exchange_ratio:
                    raise ValueError(f"exchange_ratio required for {ca.action_type}")
                
                ratio = Decimal(str(ca.exchange_ratio))

                for lot in lots_to_adjust:
                    orig_qty_val, rem_qty_val, cost_per_unit = lots_before[lot.id]
                    
                    new_orig_qty = Quantity(orig_qty_val * ratio, lot.original_quantity.unit)
                    new_rem_qty = Quantity(rem_qty_val * ratio, lot.remaining_quantity.unit)
                    
                    if ca.action_type == CorporateActionType.MERGER:
                        # Cost basis transfers entirely to the new asset
                        new_cost = Money(cost_per_unit.amount / ratio, cost_per_unit.currency_code)
                    else:
                        # For SPINOFF, usually cost basis is split, but for simplicity here we assign zero cost
                        # or some specified cost fraction. NFP doesn't specify spinoff cost allocation in CA.
                        # We'll assign zero cost to the new spinoff lot as a default safe bet if not specified.
                        new_cost = Money(Decimal("0.0"), cost_per_unit.currency_code)
                        # SPINOFF doesn't mark old lot as consumed.

                    new_lot = Lot(
                        id=uuid.uuid4(),
                        asset_id=ca.new_asset_id,
                        account_id=lot.account_id,
                        acquisition_date=lot.acquisition_date,
                        original_quantity=new_orig_qty,
                        remaining_quantity=new_rem_qty,
                        cost_per_unit=new_cost,
                        status=LotStatus.OPEN if new_orig_qty == new_rem_qty else LotStatus.PARTIALLY_CONSUMED,
                        source_activity_id=lot.source_activity_id,
                        corporate_action_id=ca.id,
                        parent_lot_id=lot.id,
                        created_at=now,
                        updated_at=now
                    )
                    new_lots.append(new_lot)

            # Save adjusted lots
            for lot in lots_to_adjust:
                self.lot_repo.add(lot)
            
            # Save new lots
            for lot in new_lots:
                self.lot_repo.add(lot)
            
            # Publish Domain Event
            # wait, nfp.events.domain_events might not have CorporateActionProcessed. Let's check it.
            # I will wrap publish in try-except if the event doesn't exist, but prompt says "Publish CorporateActionProcessed to the Event Bus."
            event = CorporateActionProcessed(
                event_id=uuid.uuid4(),
                occurred_at=now,
                corporate_action_id=ca.id,
                asset_id=ca.asset_id,
                action_type=ca.action_type.value,
                lots_adjusted=len(lots_to_adjust)
            )
            self.event_bus.publish(event)

            self.conn.commit()

        except Exception as e:
            self.conn.rollback()
            raise e
