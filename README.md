This is my code for Goldman Sachs Codesprint 2018.
I have made an Equity Order Match Engine, which matches equity Market and Limit
orders. First it takes buy and sell orders.
Then it matches any outstanding orders with the following criteria: The
highest priced buy order is matched with the lowest priced sell order.

The Engine is also able to make ammends to the orders and also reject invalid new orders
or invalid ammend orders with wrong information or ammend orders to already
completed orders.

The Engine supports adding new orders and making matches as requested.
