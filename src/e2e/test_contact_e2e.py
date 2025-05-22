import re
from playwright.sync_api import Page, expect

def test_contact_crud(page: Page):
    # Go to home page
    page.goto("http://web:5000")
    
    # Click on Contacts link in the navigation
    # Find the link by its text content within the navigation
    page.locator('.navbar-nav a:has-text("Contacts")').click()
    expect(page).to_have_url("http://web:5000/contact/")
    
    # Create a new contact - find the New Contact button by role and content
    page.locator('a.btn:has-text("New Contact")').click()
    expect(page).to_have_url("http://web:5000/contact/create")
    
    # Fill contact form - identify inputs by their associated labels
    page.locator('label:has-text("Name") + input').fill("Jane Smith")
    page.locator('label:has-text("Email") + input').fill("jane@example.com")
    page.locator('label:has-text("Phone") + input').fill("555-123-4567")
    page.locator('label:has-text("Rating") + input').fill("4")
    page.locator('button[type="submit"]:has-text("Save")').click()
    
    # Verify contact was added to list
    expect(page).to_have_url("http://web:5000/contact/")
    # Look for the contact in the table by its text content
    expect(page.locator('table')).to_contain_text("Jane Smith")
    expect(page.locator('table')).to_contain_text("jane@example.com")
    
    # Edit the contact - find the row and the Edit button within it
    edit_button = page.locator('tr:has-text("Jane Smith") a:has-text("Edit")')
    edit_button.click()
    
    # Update the contact information
    page.locator('label:has-text("Name") + input').fill("Jane Smith Updated")
    page.locator('label:has-text("Phone") + input').fill("555-987-6543")
    page.locator('button[type="submit"]:has-text("Save")').click()
    
    # Verify contact was updated in list
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator('table')).to_contain_text("Jane Smith Updated")
    
    # Edit again to delete
    edit_button = page.locator('tr:has-text("Jane Smith Updated") a:has-text("Edit")')
    edit_button.click()
    
    # Delete the contact - find delete button by its text
    page.locator('button:has-text("Delete")').click()
    page.once("dialog", lambda dialog: dialog.accept())
    
    # Verify contact was deleted
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator('body')).not_to_contain_text("Jane Smith Updated")