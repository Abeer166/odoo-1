# -*- coding: utf-8 -*-
#################################################################################
# Author      : Zero For Information Systems (<www.erpzero.com>)
# Copyright(c): 2016-Zero For Information Systems
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

{
    'name': 'Advanced Pos Multi Branch',
    'version': '1.16',
    'category': 'Sales/Point of Sale',
    "author": 'Zero Systems',
    "company": 'Zero for Information Systems',
    "website": "https://www.erpzero.com",
    "email": "sales@erpzero.com",
    'live_test_url': 'https://youtu.be/i3x9LXrdq2M',
    "sequence": 0,
    'license': 'OPL-1',
    'summary': 'point of sale Branches management',
    "description": """
    Advanced POS Controled By Branches Management.
    Many POS related one Branch or Branch With one POS only
    Allowed POS to point of sale user and manager
    Full Business Cycle for managment POS differant Operations by branch filter and Branch GroupBranch management system
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
Automatic creation of the serial Accounting journals , Invoice ,Bill,Credit Note,Payments,Stock,Sales orders and Purchase orders

    """,
    "price": 100.00,
    "currency": 'EUR',
    'depends': ['branches','point_of_sale','pos_sale'],
    'data': [
        'security/security.xml',
        'views/pos.xml',
        'views/branch.xml',
        'views/user.xml',


    ],
    'assets': {
        'point_of_sale.assets': [
            'branchpos/static/src/js/**/*',
        ],
        'web.assets_qweb': [
            'branchpos/static/src/xml/**/*',
        ],
    },
    'installable': True,
    'auto_install': False,
    "application": True,
    'images': ['static/description/special.png'],
    'pre_init_check_vers': 'pre_init_check_vers',
 }

