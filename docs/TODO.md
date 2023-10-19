# Planned Improvements to RPBC2

1. Store less data in data/*.json files
2. Try to replace multiple calls to `updateCustomField` with one call (both fields) or stop idempotent calls
3. Make pulling product data from bigcommerce and ECM happen in parallel
4. Make `main.py` < 100 lines (extract methods)
5. Disallow each instance of the Invoice class from storing its own copy of `read_pickle("fromECM.pkl")`
