"""FIFO Engine to consume Lots."""
from typing import List
from datetime import datetime
from nfp.domain.lot import Lot, LotConsumptionResult
from nfp.core.quantity import Quantity
from nfp.core.exceptions import InsufficientLotQuantityError

class FifoEngine:
    def consume_lots(self, lots: List[Lot], quantity: Quantity, updated_at: datetime) -> List[LotConsumptionResult]:
        lots = sorted(lots, key=lambda l: l.acquisition_date)
        results = []
        remaining = quantity
        for lot in lots:
            if remaining.is_zero():
                break
            if lot.remaining_quantity.is_zero():
                continue
            to_consume = min(lot.remaining_quantity, remaining)
            result = lot.consume(to_consume, updated_at)
            results.append(result)
            remaining -= to_consume
        if not remaining.is_zero():
            raise InsufficientLotQuantityError(str(remaining), "not enough lots")
        return results
