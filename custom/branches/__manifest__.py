{
    'name': 'Branch Unit Operation with Advanced features',
    'version': '0.6',
    'category': 'Sales',
    "author": 'Zero Systems',
    "company": 'Zero for Information Systems',
    "website": "https://www.erpzero.com",
    "email": "sales@erpzero.com",
    "sequence": 0,
    'license': 'OPL-1',
    'live_test_url': 'https://www.youtube.com/playlist?list=PLXFpENL3b6WU9TzMdawrHJsUBqMDXkcbn',
    'summary': 'All In One Business Area and Branches management',
    "description": """Branch management system
You can monitor, organize and manage branches according to multiple hierarchies
by group of branches,
Branch business type,
Branch Tag,
 Multi Company Support.
 Community and Enterprise Support.
Branches Hierarchical By Branch Group, Branch Business Type.
Support Branches Tags
All Trees Grouped By (Branch Group , Branch Business Type and Branch State Also).
Option To Create Stock Warehouse Automatic When Create Branch
 Up to Now Arabic and English Language Support.
 Accounting Between Different Stock Location when Approve Stock Transfer.
 Group Security For Branch(Admin-Manager-User-Accounting Between Branches).
 Branches Security Roles for All Windows Actions.
 Partners , products , Accounts Allowed for (All Branches, one Branch Only, Multi Branches).
 Journal Allowed for(All Branches ,One Branch only and Multi Branches) except Cash or Bank journals Allowed only for one Branch or All Branches.
 Register Payment Automatic Select and  Grouping By Branch plus standard Grouping By .
 Cut-Off Auto Select Branch From Invoice.
Option To Create Custom Sequences Automatic When Create Branch for (Sales Order ,Purchase Order, Invoice, Credit Note, Bill, Refund).
Custom Sequence for each Branch for(Sales Order ,Purchase Order, Invoice, Credit Note, Bill, Refund).
General sequences For All Branches for (Sales Order ,Purchase Order, Invoice, Credit Note, Bill, Refund) if no custom sequence for any supported form then the System Automatic Select General sequence Settings.
Branches
business unit business unit business unit business unit business unit business unit business unit business unit business unit business unit business unit business unit 
business unit business unit business unit business unit business unit business unit 
business unit business unit business unit business unit business unit business unit 
business unit business unit business unit business unit business unit business unit 
business unit business unit business unit business unit business unit business unit 
Multiple Branch Unit Operation Setup for All Applications Odoo
Advanced Multi Branches


branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch

branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch
branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch branch

odoo
analyitic
hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch hierarchical Branch
Branch Group
Branch Group Parent
Branch state
accurate order by branch
bank statment by branch bank statment by branch bank statment by branch bank statment by branch bank statment by branch bank statment by branch
 
 

The state to which the branch belongs,
Multi companies, even if one or more companies do not have branches
You can not activate any branch if it stops working
Automatic creation of the serial Accounting journals , Invoice ,Bill,Credit Note,Payments,Stock,Sales orders and Purchase orders.
    """,
    'depends': ['base','contacts','sale_management','sale_margin','account','purchase','sale_stock','purchase_stock'],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/branch.xml',
        'views/users.xml',
        'views/product.xml',
        'views/sale.xml',
        'views/purchase.xml',
        'views/account.xml',
        'views/picking.xml',
        'views/stock_move.xml',
        'views/warehouse.xml',
        'views/location.xml',
        'views/inventory.xml',
        'views/user_rules.xml',

    ],
    "price": 150.0,
    "currency": 'EUR',
    'installable': True,
    'auto_install': False,
    "application": True,
    'images': ['static/description/branches.png'],
    'pre_init_check_vers': 'pre_init_check_vers',
}

