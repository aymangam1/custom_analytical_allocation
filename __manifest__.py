# -*- coding: utf-8 -*-
{
    'name': "custom_analytical_allocation",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "ahmed diap",
    'website': "https://www.yourcompany.com",
    'category': 'Uncategorized',
    'version': '0.1',
    'depends': ['base','account'],

    'data': [
        # 'security/ir.model.access.csv',
        'views/account_move.xml',
    ],
}
