{
    'name': 'Hospital Management System',
    'version': '1.0',
    'category': 'Healthcare',
    'summary': 'Manage patients, doctors, and departments',
    'description': 'A complete hospital management system',
    'depends': ['base'],
    'data': [
        'views/patient_views.xml',
        'views/department_views.xml',
        'views/doctor_views.xml',
    ],
    'installable': True,
    'application': True,
}
