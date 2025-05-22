import re
from playwright.sync_api import Page, expect

def test_index(page: Page):
    page.goto("http://web:5000")
    expect(page.locator(".navbar .navbar-brand")).to_be_visible()
    expect(page.locator(".navbar .navbar-brand")).to_have_text("Flaskr")

def test_contact_crud(page: Page):
    # Go to home page
    page.goto("http://web:5000")
    
    # Click on Contacts link in the navigation
    page.locator('[data-testid="nav-contacts"]').click()
    expect(page).to_have_url("http://web:5000/contact/")
    
    # Create a new contact
    page.locator('[data-testid="new-contact-button"]').click()
    expect(page).to_have_url("http://web:5000/contact/create")
    
    page.locator('[data-testid="input-name"]').fill("Jane Smith")
    page.locator('[data-testid="input-email"]').fill("jane@example.com")
    page.locator('[data-testid="input-phone"]').fill("555-123-4567")
    page.locator('[data-testid="input-rating"]').fill("4")
    page.locator('[data-testid="save-button"]').click()
    
    # Verify contact was added to list
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator('[data-testid="contacts-table"]')).to_contain_text("Jane Smith")
    expect(page.locator('[data-testid="contacts-table"]')).to_contain_text("jane@example.com")
    
    # Edit the contact - first find the row containing our data and click its edit button
    # We're using CSS attribute selector to find the row containing "Jane Smith"
    edit_button = page.locator('tr:has-text("Jane Smith") [data-testid^="edit-contact-"]')
    edit_button.click()
    
    # Update the contact information
    page.locator('[data-testid="input-name"]').fill("Jane Smith Updated")
    page.locator('[data-testid="input-phone"]').fill("555-987-6543")
    page.locator('[data-testid="save-button"]').click()
    
    # Verify contact was updated in list
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator('[data-testid="contacts-table"]')).to_contain_text("Jane Smith Updated")
    
    # Edit again to delete
    edit_button = page.locator('tr:has-text("Jane Smith Updated") [data-testid^="edit-contact-"]')
    edit_button.click()
    
    # Delete the contact
    page.locator('[data-testid="delete-button"]').click()
    page.once("dialog", lambda dialog: dialog.accept())
    
    # Verify contact was deleted
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator('body')).not_to_contain_text("Jane Smith Updated")