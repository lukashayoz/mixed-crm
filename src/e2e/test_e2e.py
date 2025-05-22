import re
from playwright.sync_api import Page, expect

def test_index(page: Page):
    page.goto("http://web:5000")
    expect(page.locator(".navbar .navbar-brand")).to_be_visible()
    expect(page.locator(".navbar .navbar-brand")).to_have_text("Flaskr")