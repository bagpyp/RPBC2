# RioT and GTINS

RioT Runs Item Master Catalog Export and Item Master Quantity Export at 11:30pm every night.  
To issue a new GTIN to an item, the `Text10` field (UPC mirror) in Retail Pro has to be deleted, then  
running IMCE and IMQE will refill the field, and issue new GTIN.  If this happens to a product on the shelf, 
the product will have to be qurantined and retagged.  
  
Buyers have been trained specifically to carry over products by changing (eg) Desc2, and leave the UPC alone 
so that the GTIN stays with the item.  

For example, if a Burton Mission Binding (BLACK, L) 22-23 has a GTIN ending in `3ab` and the ALU is `111344`,
and we create a new item (23-24) with ALU `111345`, and we delete the UPC from the old one and issue it the new one, 
The GTIN will stay with `111345`, and the wand will count `111344` in inventory. 

All this to say that If a product is being carried over (keeping the same UPC) it needs to have its Desc 
changed if needed, and the UPC has be kept tied to the ALU, not transferred over to a "new" product with 
a reissued ALU.

# Support contact
The technician who set up our system is located in Johannesburg, South Africa  
You can create a support ticket [here](https://riotrfid.zohodesk.com/portal/en/signin) 
to meet with 

```
Jason Gewer
SMB Technical Director
m(sa) +27 82 773 5383
m(us) +1 678 743 3886
w www.riotinsight.com
```
