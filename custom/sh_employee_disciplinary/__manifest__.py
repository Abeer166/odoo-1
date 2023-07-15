# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name": "Employee Disciplinary Management | Employee Disciplinary Tracking",

    "author": "Softhealer Technologies",

    "license": "OPL-1",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "16.0.1",

    "category": "Human Resources",

    "summary": "Employee Disciplinary Employee Warning Notice Employees Disciplinary Management Employees Disciplinary Employees Warning Notices Offence Management Disciplinary Track Employee Complaint Management Organization Disciplinary Management In Organization Odoo Offences Management Disciplinary Against Employee PIP Management System Performance Improvement Plan Odoo Employee Performance Management",

    "description": """A well-structured employee disciplinary system is crucial for maintaining a healthy work environment in an organization. Do you want to manage Disciplinary action against your employees? Do you want to allow your employee to explain their point against disciplinary action on them? This module will allow you to manage disciplinary action in your organization. Managers can assign disciplinary to the employees. Employees can give explanations against the disciplinary and submit them.""",

    "depends": [

            'hr_contract',
    ],

    "data": [

        'security/ir.model.access.csv',
        'security/sh_disciplinary_security.xml',
        'data/sh_disciplinary_sequence.xml',
        'views/sh_disciplinary_views.xml',
        'views/sh_disciplinary_categories_views.xml',
        'views/hr_employee_views.xml',


    ],
    "images": ["static/description/background.png", ],
    "installable": True,
    "auto_install": False,
    "application": True,
    "price": "30",
    "currency": "EUR"
}
