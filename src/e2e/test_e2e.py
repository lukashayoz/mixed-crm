import re
from playwright.sync_api import Page, expect
import os

def get_base_url():
    return os.environ.get("BASE_URL", "http://localhost:5000")

def test_has_title(page: Page):
    page.goto("https://playwright.dev/")

    # Expect a title "to contain" a substring.
    expect(page).to_have_title(re.compile("Playwright"))

def test_get_started_link(page: Page):
    page.goto("https://playwright.dev/")

    # Click the get started link.
    page.get_by_role("link", name="Get started").click()

    # Expects page to have a heading with the name of Installation.
    expect(page.get_by_role("heading", name="Installation")).to_be_visible()

def test_index(page: Page):
    base_url = get_base_url()
    page.goto(f"{base_url}/")
    expect(page.get_by_role("heading", name="Flaskr")).to_be_visible()