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
    page.click("text=Contacts")
    expect(page).to_have_url("http://web:5000/contact/")
    
    # Register and login (needed for CRUD operations)
    page.click("text=Register")
    page.fill("input[name='username']", "testuser")
    page.fill("input[name='password']", "testpassword")
    page.click("text=Register")
    
    # Create a new contact
    page.click("text=New Contact")
    expect(page).to_have_url("http://web:5000/contact/create")
    
    page.fill("input[name='name']", "Jane Smith")
    page.fill("input[name='email']", "jane@example.com")
    page.fill("input[name='phone']", "555-123-4567")
    page.fill("input[name='rating']", "4")
    page.click("text=Save")
    
    # Verify contact was added to list
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator("table")).to_contain_text("Jane Smith")
    expect(page.locator("table")).to_contain_text("jane@example.com")
    
    # Edit the contact
    page.click("text=Edit")
    page.fill("input[name='name']", "Jane Smith Updated")
    page.fill("input[name='phone']", "555-987-6543")
    page.click("text=Save")
    
    # Verify contact was updated in list
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator("table")).to_contain_text("Jane Smith Updated")
    
    # Delete the contact
    page.click("text=Edit")
    page.click("text=Delete")
    page.once("dialog", lambda dialog: dialog.accept())
    
    # Verify contact was deleted
    expect(page).to_have_url("http://web:5000/contact/")
    expect(page.locator("body")).not_to_contain_text("Jane Smith Updated")