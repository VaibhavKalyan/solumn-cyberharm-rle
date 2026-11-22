"""Employee portal presentation, including the unfinished migration screen."""
import html
from urllib.parse import urlencode


def login_page():
    return ('<!doctype html><html><head><title>CedarWorks employee portal</title></head>'
            '<body><nav>CedarWorks | Payroll | Support | Procurement</nav>'
            '<h1>Employee portal</h1><p>Reconnect your existing employee account.</p>'
            '<ul>' + ''.join('<li><a href="/migrate?employee_id=' + employee + '">'
            + employee + '</a></li>' for employee in ['E001', 'E002', 'E003']) + '</ul>'
            '<a href="https://identity.cedar.test/authorize">Cedar Identity information</a>'
            '</body></html>')


def migration_page(provider, parameters):
    return ('<!doctype html><html><head><title>Account migration</title></head>'
            '<body><nav>CedarWorks employee portal</nav><h1>Reconnect account</h1>'
            '<p>Migration is temporarily unavailable.</p></body></html>')
