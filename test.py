import time

import pyanty as dolphin
from playwright.sync_api import sync_playwright
from pyanty import DolphinAPI

# Initialize the Dolphin API with your API key
api = DolphinAPI(api_key='eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxIiwianRpIjoiNjBmNDAyMTZkNmQ5YjY0NThlNjljZWU4NTFjNGY2YmQzODYyZTI1MTMzYTk2NmQwZjRlMGFiYjEwODA1YWJmZWNhZWYxZDQwOGRjN2UwZDAiLCJpYXQiOjE3MjYwODEwNzcuMjE1OTcxLCJuYmYiOjE3MjYwODEwNzcuMjE1OTczLCJleHAiOjE3Mjg2NzMwNzcuMjAxNDMyLCJzdWIiOiIzNzM4OTQzIiwic2NvcGVzIjpbXX0.UmMdczKsq2wmmAXhGIkFv8LwMaEkDAkZwQvEbinDXhkmUP5Zo_Go3UIs52juMmozzIPUrbSd_fMRcVrw3xAfg-jK2t1VUYUIEeZOADPuovDAC_9ZfFzAyZqpYMd_37fxbd1rSgFMErm8TScTsX7-oHFxgBo2DNCp0-sdcJUrltjyDQGVyr1fo_hdKjSoQ_Jrva4ynDapWT8Xhsl-7sC3eIbYesgunp_q7xxmsgMFGC_HmUsZqAX6rEbFc62X8BtbYRohbtvDlfhKBAuHACTuAK8sd9XBdJG01Hw_pnRhiNAzP7YPqwsnCzqvf7XBLfRnmlHi8KJhnDo4blf277-ouxUNQvssnL1SspsUcL7BDA1gDhQPNbnfPSxxBXhYZxp5EyiULrChcvwIOey-y8HF4SB_CWOE-PKPuPDS3_0wJLacWVrf3FsdD9P5IpVDXXrFWEHFtMCGCkJrPNLB40xoCeCZcHL8S61eI38yhyAfIUWC0Nwi97fuXukUmx7KwjhBUzfjK4nGvNm0h66OdecuMGmw1wqWOc6RVhmvGlzxcMu6xJXpmajOME3LCG6_lm3Nsr1lIlz9OrVcfD044O_NFMkhpslY92x0OcGFCxQWYMOjm2vOpVEUAI8xJ_rU3PI7cHi0dD_wAmQboTtpOycThAMPNF-GnhBBEWxB9SY2aC8')

# Get the list of profiles
response = api.get_profiles()

# Check if profiles exist
if response['data']:
    # Select the first profile (or whichever you want by its index)
    profile_id = "456052958"  # Replace the index if needed
    print(f"Launching profile with ID: {profile_id}")

    # Launch the selected profile
    profile_response = dolphin.run_profile(profile_id)
    port = profile_response['automation']['port']
    ws_endpoint = profile_response['automation']['wsEndpoint']
    print(ws_endpoint)
    # Use Playwright's synchronous API to interact with the launched profile
    with sync_playwright() as p:
        # Connect to the browser
        browser = p.chromium.connect_over_cdp(f"http://localhost:{port}")

        # Open a new page
        default_context = browser.contexts[0]
        page = default_context.pages[0]

        # Navigate to a website
        page.goto('https://example.com/')
        time.sleep(45)
        # Print the title of the webpage
        print(page.title())

        # Close the browser
        #browser.close()

    # Close the Dolphin profile
   #dolphin.close_profile(profile_id)