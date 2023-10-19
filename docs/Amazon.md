# Listing on Amazon


1. As of 9/25, everything in our Amazon catalog has a qty level that has not been updated with store diffs.
2. Before we turn off vacation mode, we should take the entire Amazon Catalog qty to zero, then enable just Ski Poles 

Because we sell 1/2 a day and usually have 5+ ea


Exclude Vendors

Filter for empty UPCs

UPC, qty(OH at HC1), p4(Amazon), ALU

Amazon has a loader template 

	- Condition: New
	- ID type (1 or something)
	- Shipping Template
		<= 19.99 'standard' ($6.99)
		>= 20 gets 'prime' ($free.99)

AMTU runs every 15 minutes
The AMTU software never created brand-new listings from scratch
Instead, items would be added to our catalog if their ASIN already existed in Amazon
The AMTU also would not create new listings in our catalog,m even if the ASIN did exist, unless we first manually added those ASINs to our catalog
All the AMTU did was update price and quantity of items already in our Catalog, based on lastEditDate
The AMTU would also download an "order file" at the end of execution

A separate program, RDIce would consume the order file and PROC in receipts to Retail Pro
RDIce would then also filter for all items with a last_edit_date <= 15 minutes ago, generate a .ttd file containing:
sku, Amazon price, quantity

Now, Quantity, UPC, SKU and Price will all be managed by Codisto
