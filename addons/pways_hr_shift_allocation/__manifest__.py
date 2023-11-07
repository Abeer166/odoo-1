# -*- coding: utf-8 -*-
{
    'name': "Employee Shift Allocation",
    'version': '16.0.0',
    'category': "Generic Modules/Human Resources",
    'summary': """Define multiple work shifts and create bulk shift allocation for multiple employees and link weekoff and allocation with employee master.
                Employee Shift Allocation
                Employee Shift 
                Shift Management
                Bulk Shift Creation
                Multiple Shift
                Multiple work shifts
                Work Shifts
                Shifts Request
        """,
    'author':'Preciseways',
    'description':  "1: Define multiple work shifts"
                    "2: Flexible hour wise shift" 
                    "3: Assign bulk shift with help of wizard"
                    "4: calender view with filter of type and shift",
    'website': "http://www.preciseways.com",
    'depends': ['hr'],
    'data': [
                'security/ir.model.access.csv',
                'data/data.xml',
                'views/sub_type_view.xml',             
                'views/hr_employee.xml',                  
                'views/hr_shift.xml',
                'views/shift_allocation_view.xml',
                'wizard/bulk_allocation.xml',            
            ],
    'installable': True,
    'application': True,
    'price': 15.0,
    'currency': 'EUR',
    'images':['static/description/banner.png'],
    'license': 'OPL-1',
}   