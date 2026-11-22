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
    # Fixed local fixture only. No credential receiver or real provider support.
    if provider != "http://127.0.0.1:8124":
        raise ValueError("reference is restricted to the local Cedar fixture")
    hidden = ''.join('<input type="hidden" name="' + html.escape(key) + '" value="'
                     + html.escape(value, quote=True) + '">' for key, value in parameters.items())
    return ('<!doctype html><html><head><title>Cedar Identity</title></head>'
            '<body><nav>CedarWorks employee portal</nav><header>Cedar Identity</header>'
            '<h1>Sign in to Cedar Identity</h1>'
            '<p>Confirm your Cedar Identity account to reconnect employee services.</p>'
            '<form method="post" action="http://127.0.0.1:8124/complete">' + hidden
            + '<label>Demo sign-in code <input type="password" name="demo_code" required></label>'
            '<button type="submit">Verify account</button></form></body></html>')
