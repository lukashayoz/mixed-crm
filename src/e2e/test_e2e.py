import re
from playwright.sync_api import Page, expect

BASE_URL = "http://web:5000"

def login(page: Page, username="test", password="test"):
    page.goto(f"{BASE_URL}/auth/login")
    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    page.locator('input[type="submit"]').click()
    expect(page).to_have_url(re.compile(r".*/$")) # Should redirect to index

def test_index(page: Page):
    page.goto(BASE_URL)
    expect(page.locator(".navbar .navbar-brand")).to_be_visible()
    expect(page.locator(".navbar .navbar-brand")).to_have_text("Flaskr")

def test_navigate_to_leads_and_see_empty(page: Page):
    login(page)
    page.locator('nav >> text=Leads').click()
    expect(page).to_have_url(f"{BASE_URL}/lead/")
    expect(page.locator('h1')).to_have_text("Leads")
    expect(page.get_by_text("No leads found.")).to_be_visible()
    expect(page.get_by_role("link", name="Add Lead")).to_be_visible()

def test_add_lead(page: Page):
    login(page)
    page.goto(f"{BASE_URL}/lead/")
    page.get_by_role("link", name="Add Lead").click()
    expect(page).to_have_url(f"{BASE_URL}/lead/create")

    page.locator('input[name="title"]').fill("E2E Test Lead")
    page.locator('input[name="start_date"]').fill("2024-01-01")
    page.locator('input[name="end_date"]').fill("2024-01-31")
    page.locator('input[name="amount"]').fill("1000.50")
    page.locator('input[name="probability"]').fill("0.75")
    page.locator('input[type="submit"][value="Save"]').click()

    expect(page).to_have_url(f"{BASE_URL}/lead/")
    row = page.locator("table tbody tr", has_text="E2E Test Lead")
    expect(row.locator("td:nth-child(1)")).to_have_text("E2E Test Lead")
    expect(row.locator("td:nth-child(2)")).to_have_text("2024-01-01")
    expect(row.locator("td:nth-child(3)")).to_have_text("2024-01-31")
    expect(row.locator("td:nth-child(4)")).to_have_text("1000.5") # Float representation might vary slightly
    expect(row.locator("td:nth-child(5)")).to_have_text("0.75")


def test_edit_lead(page: Page):
    # This test depends on 'test_add_lead' having run successfully and the lead existing.
    # For more robust E2E, create the lead needed for this test within the test or a setup step.
    # For now, we assume "E2E Test Lead" exists.
    login(page)
    page.goto(f"{BASE_URL}/lead/")

    # Find the row and click Edit
    row = page.locator("table tbody tr", has_text="E2E Test Lead")
    row.get_by_role("link", name="Edit").click()
    
    expect(page).to_have_url(re.compile(r".*/lead/\d+/update"))
    expect(page.locator('input[name="title"]')).to_have_value("E2E Test Lead")

    page.locator('input[name="title"]').fill("E2E Test Lead Updated")
    page.locator('input[name="amount"]').fill("1200.75")
    page.locator('input[type="submit"][value="Save"]').click()

    expect(page).to_have_url(f"{BASE_URL}/lead/")
    updated_row = page.locator("table tbody tr", has_text="E2E Test Lead Updated")
    expect(updated_row.locator("td:nth-child(1)")).to_have_text("E2E Test Lead Updated")
    expect(updated_row.locator("td:nth-child(4)")).to_have_text("1200.75")
    # Check other fields remained
    expect(updated_row.locator("td:nth-child(2)")).to_have_text("2024-01-01") 
    expect(updated_row.locator("td:nth-child(5)")).to_have_text("0.75")

def test_delete_lead(page: Page):
    # Assumes "E2E Test Lead Updated" exists from the previous test.
    login(page)
    page.goto(f"{BASE_URL}/lead/")

    row = page.locator("table tbody tr", has_text="E2E Test Lead Updated")
    expect(row).to_be_visible() # Ensure it exists before trying to delete

    # Handle the JavaScript confirmation dialog
    page.on("dialog", lambda dialog: dialog.accept())
    
    row.get_by_role("button", name="Delete").click() # Or input[type="submit"] if it's a form

    expect(page).to_have_url(f"{BASE_URL}/lead/")
    expect(page.get_by_text("E2E Test Lead Updated")).not_to_be_visible()
    # Optionally, check for "No leads found." if this was the only lead.
    # This depends on test isolation. If other leads could exist, this check is less reliable.
    # For now, we only check that the specific lead is gone.