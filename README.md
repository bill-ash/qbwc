## QBWC: Quickbooks Desktop Webconnector 

**Experimental**

Django package for syncing data between django application and 
QuickBooks Desktop via the Quickbooks Webconnector (QBWC). 

Implementation includes transfer services (push, pull, re-sync) for: 

- gl accounts  
- other name list
- expenses (credit card charges)
- customers 
- credit cards 
- vendors

Road map: 

- vendor bills
- journal entries
- QuickBooks Reports 

## Installation 

Install the latest development version from github using: 

```
pip install git+https://github.com/bill-ash/qbwc
```

or from pypi: 

```
pip install qbwc
```


## Example 

Example directory includes application with sample apps for each of the entites mentioned above. 

Repeated patterns will be abstracted in the `BaseObjectMixin` model and are likely to change.




