
# Web SKUs and Retail Pro ALUs

In Retail Pro, a style class is defined by a group of products sharing the same values for
 - Vendor Code (Brand)
 - DCS (Category)
 - Description 1 (Name)
 - Description 2 (Year, e.g. 22-23 or 2023)

This is different from the website, where what makes a product "class" is just its Name and Year


## Chapstick products

Web SKs prefixed with `2-` indicate that the product was alone in style class.  
For instance, a tube of unflavored chapstick with ALU of `1234` would have a Web SKU of 

```
2-1234  # unflavored chapstick
```

## T-Shirt products

If another product enters the style class though creation by a Buyer, the product becomes _configurable,_ 
which means that people can choose a specific colorway or size of the item when they go to purchase it.

The Say another tube of chapstick is created in Retail Pro, and that it shares the same 4 values for 
Brand, Category, Name and Year of the original tube, but its flavor is `cherry` instead of `unflavored`.

The website needs to create three products to represent this information to an online customer. 
The first product is called the _class representative._  Its Web SKU is prefixed with a `0-` and its numeric 
values is taken from the ALU with the _smallest integer value_ out of all ALUs of the class it represents. 
The other two products each represent the purchasable variants of the configurable class representative. a

🚨 this  will create a whole new item on the website, leaving the original, unflavored chapstick 
(and its sock level (or quantity)) dangling online, without any possibility of being updated by the software. 🚨

```
0-1234  # chapstick class representative
1-1234	# unflavored
1-9999  # cherry
```

## Potential Problems

Because BigCommerce can interpret a specific product from Retail Pro as a chapstick product on one iteration, 
and then as a t-shirt product on the next, significant problems can occur that sever the data relationship of 
a particular product in Retail Pro and the same product in BigCommerce. 

### Carrying Over into a Style Class

The case when a chapstick product becomes a t-shirt product is outlined above.  Consider the same chapstick 
scenario, but say that many years ago Hillcrest used to sell `licorice` flavored chapstick.  If a buyer chooses 
to replenish stock of this flavor, they might do so by finding the old record of the chapstick when its Year 
or (Description 2) was set to 2008, and change just that field to 2023.

This is called **Carrying Over**, and if it is not done with great care, severe problems can occur.  Since the 
licorice chapstick was created so long ago, it may have a tiny ALU in Retail Pro, say `10`. Well, 
since `10 < 1234`, 10 will overtake 1234 as the numeric value for the 0-prefixed class representative Web SKU. 
Thus, 🚨 this carry over will create a whole new item on the website, leaving the original pair of chapsticks
(and their sock levels (or quantities)) dangling online, without any possibility of being updated by the software. 🚨

```
0-10    # new chapstick class representative
1-1234  # unflavored
1-9999  # cherry
1-10    # licorice
```

### Carrying Over out of a Style Class

Say the cherry flavor gets carried over next year (Description 2 goes from 2023 -> 2024), but the other flavors don't
Then, a new style class will be created in Retail Pro, but with only one item. 

```
2-9999  # cherry chapstick
```