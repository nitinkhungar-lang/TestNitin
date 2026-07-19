"""Tax Rule Registry."""
class TaxRuleRegistry:
    def __init__(self):
        self.providers = {}
        
    def register(self, jurisdiction: str, provider):
        self.providers[jurisdiction] = provider
        
    def get_provider(self, jurisdiction: str):
        return self.providers.get(jurisdiction)
