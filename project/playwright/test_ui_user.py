import os
import uuid
import pytest
from playwright.sync_api import Page, Dialog

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")


def test_docs_page(page: Page):
    page.goto(f"{BASE_URL}/docs")
    assert "Swagger" in page.content() or "FastAPI" in page.title()


def handle_dialog(dialog: Dialog):
    assert "Login failed" in dialog.message
    assert "password must be longer than 8 characters" in dialog.message
    dialog.accept()


def generate_user():
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    password = "12345678"
    return unique_username, password


def navigate_to_register(page: Page):
    page.goto(f"{BASE_URL}/")
    page.get_by_role("link", name="Register").click()
    page.wait_for_url(f"{BASE_URL}/register", timeout=3000)


def register_user(page: Page, username: str, password: str):
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill(password)
    page.locator("input[name='repeat_password']").fill(password)
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Register Now!").click()
    page.wait_for_url(f"{BASE_URL}/login", timeout=5000)
    assert "/login" in page.url


def test_homepage_loads(page: Page):
    page.goto(f"{BASE_URL}/")
    assert page.title() != ""
    assert "DexQuiz" in page.title() or "Quiz" in page.content()


def test_registration_validation_errors(page: Page):
    navigate_to_register(page)

    # Short password
    page.locator("input[name='username']").fill("inv")
    page.locator("input[name='password']").fill("123")
    page.locator("input[name='repeat_password']").fill("123")
    page.once("dialog", handle_dialog)
    page.get_by_role("button", name="Register Now!").click()

    # Mismatched passwords
    page.locator("input[name='password']").fill("123")
    page.locator("input[name='repeat_password']").fill("456")
    page.once("dialog", handle_dialog)
    page.get_by_role("button", name="Register Now!").click()


def test_successful_registration_redirects_to_login(page: Page):
    username, password = generate_user()
    navigate_to_register(page)
    register_user(page, username, password)

    assert page.locator("input[name='username']").is_visible()


def test_successful_login(page: Page):
    username, password = generate_user()

    # First register the user
    navigate_to_register(page)
    register_user(page, username, password)

    # Now log in
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill(password)
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Log in").click()
    page.wait_for_timeout(1000)

    # Verify login
    assert page.get_by_role("button", name="Logout").is_visible()
    assert "Welcome" in page.content() or "Score" in page.content()


def test_logout_functionality(page: Page):
    username, password = generate_user()

    # Register and login
    navigate_to_register(page)
    register_user(page, username, password)
    page.locator("input[name='username']").fill(username)
    page.locator("input[name='password']").fill(password)
    page.once("dialog", lambda dialog: dialog.accept())
    page.get_by_role("button", name="Log in").click()
    page.wait_for_timeout(500)

    # Log out
    page.get_by_role("button", name="Logout").click()
    page.wait_for_timeout(500)

    # Verify logged out state
    assert "Login" in page.content() or "Register" in page.content()
