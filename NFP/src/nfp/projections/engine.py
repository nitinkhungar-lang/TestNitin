from typing import List
from datetime import date, datetime
from decimal import Decimal
from nfp.projections.capital_gains import CapitalGainProjection
from nfp.domain.lot import Lot, LotStatus
from nfp.rules.fifo_engine import FifoEngine
from nfp.core.quantity import Quantity
import copy

class ProjectionEngine:
    def __init__(self, event_repo=None, lot_repo=None, activity_repo=None):
        self.event_repo = event_repo
        self.lot_repo = lot_repo
        self.activity_repo = activity_repo

    def compute_holdings(self, as_of_date: date) -> dict:
        if not self.event_repo:
            return {}
            
        events = sorted(self.event_repo.get_all(), key=lambda e: (e.event_date, e.sequence_number))
        holdings = {}
        for event in events:
            event_date = event.event_date.date() if isinstance(event.event_date, datetime) else event.event_date
            if event_date > as_of_date:
                continue
                
            if not event.asset_id:
                continue
                
            if self.activity_repo:
                act = self.activity_repo.get(event.business_activity_id)
                if act and (act.status == "REVERSED" or act.is_reversal):
                    continue
                    
            if event.event_type_code == "ASSET_INCREASE" and event.quantity:
                holdings[event.asset_id] = holdings.get(event.asset_id, Decimal("0")) + event.quantity.value
            elif event.event_type_code == "ASSET_DECREASE" and event.quantity:
                holdings[event.asset_id] = holdings.get(event.asset_id, Decimal("0")) - event.quantity.value
                
        return holdings

    def compute_cash_flows(self, start_date: date, end_date: date) -> List[dict]:
        if not self.event_repo:
            return []
            
        events = sorted(self.event_repo.get_all(), key=lambda e: (e.event_date, e.sequence_number))
        cash_flows = []
        for event in events:
            event_date = event.event_date.date() if isinstance(event.event_date, datetime) else event.event_date
            if not (start_date <= event_date <= end_date):
                continue
                
            if self.activity_repo:
                act = self.activity_repo.get(event.business_activity_id)
                if act and (act.status == "REVERSED" or act.is_reversal):
                    continue
                    
            if event.event_type_code in ["EXPENSE", "CASH_OUT", "EMI_PAYMENT"]:
                cash_flows.append({
                    "date": event_date,
                    "description": event.description,
                    "amount": float(event.amount.amount),
                    "currency": event.amount.currency_code,
                    "flow_type": "OUTFLOW",
                    "event_type": event.event_type_code
                })
            elif event.event_type_code in ["INCOME", "CASH_IN", "EMI_PRINCIPAL", "EMI_INTEREST"]:
                # wait, EMI is an outflow, but let's just categorize by event_type
                flow_type = "OUTFLOW" if "EMI" in event.event_type_code else "INFLOW"
                cash_flows.append({
                    "date": event_date,
                    "description": event.description,
                    "amount": float(event.amount.amount),
                    "currency": event.amount.currency_code,
                    "flow_type": flow_type,
                    "event_type": event.event_type_code
                })
                
        return cash_flows

    def compute_income(self): return []

    def compute_capital_gains(self, start_date: date = None, end_date: date = None) -> List[CapitalGainProjection]:
        if not self.event_repo:
            return []
            
        events = sorted(self.event_repo.get_all(), key=lambda e: (e.event_date, e.sequence_number))
        
        simulated_lots = []
        gains = []
        fifo = FifoEngine()
        import uuid
        from nfp.core.clock import Clock
        now = datetime.now()
        
        asset_lots = {}
        
        for event in events:
            if not event.asset_id:
                continue
                
            if self.activity_repo:
                act = self.activity_repo.get(event.business_activity_id)
                if act and (act.status == "REVERSED" or act.is_reversal):
                    continue
                    
            if event.event_type_code == "ASSET_INCREASE":
                if event.quantity and event.quantity.value > 0:
                    cost = event.amount
                    cost_per_unit_amount = cost.amount / event.quantity.value
                    from nfp.core.money import Money
                    
                    event_date_val = event.event_date.date() if isinstance(event.event_date, datetime) else event.event_date
                    
                    lot = Lot(
                        id=uuid.uuid4(),
                        asset_id=event.asset_id,
                        account_id=event.account_id,
                        acquisition_date=event_date_val,
                        original_quantity=event.quantity,
                        remaining_quantity=event.quantity,
                        cost_per_unit=Money(cost_per_unit_amount, cost.currency_code),
                        status=LotStatus.OPEN,
                        source_activity_id=event.business_activity_id,
                        corporate_action_id=None,
                        parent_lot_id=None,
                        created_at=now,
                        updated_at=now
                    )
                    asset_lots.setdefault(event.asset_id, []).append(lot)
            elif event.event_type_code == "ASSET_DECREASE":
                if event.quantity and event.quantity.value > 0:
                    lots = asset_lots.get(event.asset_id, [])
                    try:
                        results = fifo.consume_lots(lots, event.quantity, now)
                        for r in results:
                            proportion = r.quantity_consumed.value / event.quantity.value
                            sell_value_amount = event.amount.amount * proportion
                            
                            event_date_val = event.event_date.date() if isinstance(event.event_date, datetime) else event.event_date
                            buy_date_val = r.acquisition_date.date() if isinstance(r.acquisition_date, datetime) else r.acquisition_date
                            
                            gains.append(
                                CapitalGainProjection(
                                    asset_id=event.asset_id,
                                    sell_date=event_date_val,
                                    buy_date=buy_date_val,
                                    quantity=r.quantity_consumed.value,
                                    sell_value=sell_value_amount,
                                    buy_value=r.cost_consumed.amount,
                                    currency=event.amount.currency_code
                                )
                            )
                    except Exception as e:
                        pass
                        
        if start_date:
            if isinstance(start_date, datetime): start_date = start_date.date()
            gains = [g for g in gains if g.sell_date >= start_date]
        if end_date:
            if isinstance(end_date, datetime): end_date = end_date.date()
            gains = [g for g in gains if g.sell_date <= end_date]
            
        return gains
