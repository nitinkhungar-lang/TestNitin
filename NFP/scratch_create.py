import os

base_path = "src/nfp/repositories"
os.makedirs(base_path, exist_ok=True)

repos = [
    "base", "ledger_repo", "event_repo", "activity_repo", 
    "evidence_repo", "asset_repo", "account_repo", 
    "institution_repo", "lot_repo", "corporate_action_repo", 
    "exchange_rate_repo", "market_price_repo"
]

for repo in repos:
    with open(f"{base_path}/{repo}.py", "w") as f:
        pass

db_path = "src/nfp/infrastructure/database/sqlite"
os.makedirs(db_path, exist_ok=True)
for repo in repos:
    if repo == "base":
        continue
    with open(f"{db_path}/sqlite_{repo}.py", "w") as f:
        pass
        
print("Directories and files created.")
