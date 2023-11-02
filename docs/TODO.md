# Planned Improvements to RPBC2

1. Store less data in data/*.json files (just need IDs to count and retrieve)
2. Make pulling product data from bigcommerce and ECM happen in parallel
3. Disallow each instance of the Invoice class from storing its own copy of `read_pickle("fromECM.pkl")`
