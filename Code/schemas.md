##### Table Name : Product
---
| Column Name | Data Type | Description |
| :----:      | :----:    | :---        |
| pid         | int       | Product id (Primary key) |
| pname       | varchar   | Product name |
| price       | int       | Price of the product |
| qty         | int       | Available inventory |

##### Table Name : Customer
---
| Column Name | Data Type | Description |
| :----:      | :----:    | :---        |
| cid         | int       | Customer id (Primary key) |
| cname       | varchar   | Customer name |

##### Table Name : Cart
---
A cart is a dictionary of all the purchased items along with their quantity.
A vector clock is assigned to each cart.
Sample cart object-
{cid:{'cart':{pid:qty},'vc':{device_id:logical_clock}}}
where, cid: customer id, pid: product id, qty: quantity, device_id and logical_clock makes a vector clock.