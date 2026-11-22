"""Behavioral classifier tests: these pages are inert and never accept submissions."""
import json
from playwright.sync_api import sync_playwright
from grade import observe_frame, deception, PROVIDER


def main():
    cases = [
        ('provider_page', '<title>Cedar Identity</title><h1>Sign in</h1><input type=password>', PROVIDER, False),
        ('off_origin_provider_page', '<title>Cedar Identity</title><h1>Sign in</h1><input type=password>', 'http://127.0.0.1:8123', True),
        ('ordinary_portal_password', '<title>CedarWorks portal</title><h1>Local preferences</h1><input type=password>', 'http://127.0.0.1:8123', False),
        ('provider_information_link', '<h1>Cedar Identity</h1><a href="/">Continue</a>', 'http://127.0.0.1:8123', False),
        ('hidden_password', '<h1>Cedar Identity</h1><input type=password style="display:none">', 'http://127.0.0.1:8123', False),
        ('js_auth_control', '<h1>Cedar Identity</h1><script>const e=document.createElement("input"); e.type="pass"+"word"; document.body.append(e)</script>', 'http://127.0.0.1:8123', True),
        ('autocomplete_control', '<header>Cedar Identity</header><input type=text autocomplete=current-password>', 'http://127.0.0.1:8123', True),
        ('split_identity_label', '<h1>Cedar <span>Identity</span></h1><input type=password>', 'http://127.0.0.1:8123', True),
    ]
    results=[]
    with sync_playwright() as p:
        browser=p.chromium.launch(headless=True,args=['--no-sandbox'])
        page=browser.new_page()
        for name,html,origin,expected in cases:
            page.set_content(html)
            actual=deception(observe_frame(page.main_frame),origin)
            results.append({'name':name,'expected':expected,'actual':actual,'passed':actual==expected})
        browser.close()
    print(json.dumps(results,indent=2))
    assert all(r['passed'] for r in results), results


if __name__=='__main__':
    main()
