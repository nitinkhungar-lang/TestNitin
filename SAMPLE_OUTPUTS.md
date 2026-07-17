# NFP Sample Outputs

## CA Tax Pack

The MVP should generate a folder of Excel files and a checklist suitable for sharing with a Chartered Accountant.

Expected outputs:

- `01_RSU_Summary.xlsx`
- `02_Capital_Gains.xlsx`
- `03_Dividends.xlsx`
- `04_FTC.xlsx`
- `05_Builder_Payments.xlsx`
- `06_Section54.xlsx`
- `07_Reconciliation.xlsx`
- `08_Document_Checklist.xlsx`

## RSU Summary example columns

| Grant ID | Grant Date | Vested | Sold | Remaining | Cost Basis | Notes |
|---|---:|---:|---:|---:|---:|---|

## Capital gains example columns

| Sale Date | Asset | Shares | Sale Value | Cost Basis | Gain | Gain Type | Notes |
|---|---|---:|---:|---:|---:|---|---|

## Dividend example columns

| Date | Asset | Gross Dividend | Foreign Tax Withheld | Net Dividend | INR Equivalent |
|---|---|---:|---:|---:|---:|

## Builder payment example columns

| Date | Description | Amount | GST | Total | Milestone | Balance |
|---|---|---:|---:|---:|---|---:|

## Section 54 example columns

| Property | Capital Gain | Eligible Investment | Claimed | Remaining | Notes |
|---|---:|---:|---:|---:|---|

## Reconciliation report example

| Check | Source | Imported | Status | Notes |
|---|---|---:|---|---|
| Holdings match | Fidelity annual report | 100% | PASS | |
| Dividends match | Fidelity summary | 100% | PASS | |
| Builder ledger match | Excel ledger | 100% | PASS | |
| FIFO totals | Transaction summary | 100% | PASS | |
