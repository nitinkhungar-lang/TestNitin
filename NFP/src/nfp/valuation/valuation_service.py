"""Valuation Service."""
class ValuationService:
    def __init__(self, provider):
        self.provider = provider
        
    def valuate(self, asset_id, date):
        return self.provider.get_price(asset_id, date)
