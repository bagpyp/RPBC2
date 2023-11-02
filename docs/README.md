# Retail Pro Big Commerce 2

AKA RPBC2, AKA "The Software"  
Written by Robbie Cunningham
 - (503) 803-4458
 - rtc@bagpyp.net 

## Overview

The script includes a series of imports and a `main` function that defines the workflow. It deals with processing order and return data, updating product information, handling product images, and synchronizing data with other systems such as BigCommerce and Quivers.

## Table of Contents 

1. [Web SKUs and Retail Pro ALUs](./SKUs and ALUs.md)  
2. [RioT and GTINs](./RioT.md)

## Dependencies

- `datetime`: For timestamping the process and calculating durations.
- `pandas`: For data manipulation and analysis.
- `config`: Custom module that likely contains configurations such as `update_window_hours`, `apply_changes`, and `sync_sideline_swap`.
- `scripts.quivers`: Custom module for sending data to Quivers.
- `src.download.orders`: Custom modules to download order and return data.
- `src.download.products`: Custom modules to download product data from BigCommerce, including brand and category IDs.
- `src.product_images`: Custom modules to handle product image locations and web media persistence.
- `src.server`: Custom modules to interact with ECM data.
- `src.transformations`: Custom modules for data cleaning, filtering, and preparation.
- `src.upload.create`: Custom modules to handle the creation of new product data payloads.
- `src.upload.update`: Custom modules to handle the updating of existing product data.
- `src.util`: Custom module that likely contains utility paths like `DATA_DIR` and `LOGS_DIR`.

## Script Flow

1. **Initialization**: It starts by logging the start time and the intention to process changes over the last `update_window_hours`.

2. **Conditional Loading or Downloading**:
   - If `apply_changes` is `False`, it loads existing pickled data from the data directory.
   - If `apply_changes` is `True`, it fetches new orders and returns, writes them to ECM, reads the ECM data into a DataFrame, and pulls the latest product data from BigCommerce.

3. **Data Processing**:
   - Cleans and filters the data from ECM.
   - Builds product group structures.
   - Deletes products from the DataFrame that have conflicts.
   - Attaches web data to products and collects images from product children.

4. **Media Persistence** (if `apply_changes` is `True`):
   - Persists web media and builds image locations from file structure.
   - If `apply_changes` is `False`, it loads pickled file structure data.

5. **Data Preparation for Upload**:
   - Joins the file structure data to the main DataFrame and prepares it for upload.

6. **Payload Building**:
   - Constructs payloads for updating existing products and creating new ones.

7. **Applying Changes** (if `apply_changes` is `True`):
   - Updates product groups and batch updates single products.
   - Creates new products in the system.
   - Sends data to Quivers.

8. **Finalization**:
   - Logs the end time and duration of the process.
   - Writes log information to a run log file.

## Execution

The script is intended to be run automatically every hour, likely through a cron job or similar scheduling mechanism on the server. It checks for updates and applies changes as per the configuration settings.

## Log File

The script writes to a log file each time it runs, recording the start time, end time, duration, and `update_window_hours`. This log helps in monitoring the script's execution over time.

## Configuration Settings

Some key behaviors of the script depend on the configuration settings, such as whether changes are applied and whether the sideline swap sync is enabled.

## Notes

- The script assumes the presence of a predefined directory structure (`DATA_DIR` and `LOGS_DIR`) and certain pickle files.
- Error handling is not explicitly documented, so any logging or exception management should be handled in the underlying modules or via external monitoring.

## Conclusion

This script is crucial for maintaining up-to-date information within the ski shop's retail and online systems, processing orders and returns efficiently, and ensuring that product data is synchronized across different platforms. Proper configuration and regular monitoring of its execution logs are necessary for smooth operation.
