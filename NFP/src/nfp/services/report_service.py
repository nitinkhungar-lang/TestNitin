from typing import List, Optional, Dict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from nfp.services.tax_service import TaxService, CapitalGainReportItem
from nfp.projections.engine import ProjectionEngine
from nfp.valuation.valuation_service import ValuationService

@dataclass
class NetWorthReportItem:
    asset_id: UUID
    asset_type: str
    quantity: float
    current_price: float
    value_inr: float

@dataclass
class NetWorthReport:
    date: date
    items: List[NetWorthReportItem]
    total_net_worth_inr: float

@dataclass
class CashFlowReportItem:
    date: date
    description: str
    amount: float
    currency: str
    flow_type: str # INFLOW or OUTFLOW

@dataclass
class CashFlowReport:
    start_date: date
    end_date: date
    items: List[CashFlowReportItem]
    net_cash_flow: float

class ReportService:
    def __init__(
        self,
        tax_service: TaxService,
        projection_engine: ProjectionEngine,
        valuation_service: ValuationService,
        asset_repo=None
    ):
        self.tax_service = tax_service
        self.projection_engine = projection_engine
        self.valuation_service = valuation_service
        self.asset_repo = asset_repo

    def generate_capital_gains_report(self, start_date: date, end_date: date) -> List[CapitalGainReportItem]:
        return self.tax_service.generate_capital_gains_report(start_date, end_date)

    def generate_net_worth_report(self, as_of_date: date) -> NetWorthReport:
        holdings = self.projection_engine.compute_holdings(as_of_date)
        items = []
        total = 0.0
        
        for asset_id, quantity in holdings.items():
            if quantity == 0:
                continue
                
            asset = self.asset_repo.get(asset_id) if self.asset_repo else None
            asset_type = asset.asset_type_code if asset else "UNKNOWN"
            
            # Use valuation service
            price = self.valuation_service.valuate(asset_id, as_of_date) if self.valuation_service else 0.0
            
            # Loans might be represented with a negative quantity or price, but here
            # we will assume negative price or something. For simplicity, we just multiply.
            # But wait, typically for a loan, the quantity is 1 and value is -ve, or quantity is +ve and we treat it as liability if asset_type == 'LOAN'
            value = float(quantity) * float(price)
            if asset_type == "LOAN":
                # ensure liability reduces net worth
                value = -abs(value)
                
            items.append(NetWorthReportItem(
                asset_id=asset_id,
                asset_type=asset_type,
                quantity=float(quantity),
                current_price=float(price),
                value_inr=value
            ))
            total += value
            
        return NetWorthReport(date=as_of_date, items=items, total_net_worth_inr=total)

    def generate_cash_flow_report(self, start_date: date, end_date: date) -> CashFlowReport:
        cfs = self.projection_engine.compute_cash_flows(start_date, end_date)
        items = []
        net_cash_flow = 0.0
        for cf in cfs:
            items.append(CashFlowReportItem(
                date=cf["date"],
                description=cf["description"],
                amount=cf["amount"],
                currency=cf["currency"],
                flow_type=cf["flow_type"]
            ))
            if cf["flow_type"] == "INFLOW":
                net_cash_flow += cf["amount"]
            else:
                net_cash_flow -= cf["amount"]
                
        return CashFlowReport(start_date=start_date, end_date=end_date, items=items, net_cash_flow=net_cash_flow)
