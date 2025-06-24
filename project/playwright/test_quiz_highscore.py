import os
import uuid
import pytest
from playwright.sync_api import sync_playwright

BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def generate_user():
    return f"testuser_{uuid.uuid4().hex[:8]}"

def register_user(page, username, password):
    page.goto(f"{BASE_URL}/register")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.fill("input[name='repeat_password']", password)
    page.click("button:has-text('Register Now!')")
    page.wait_for_load_state("networkidle")

def login_user(page, username, password):
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name='username']", username)
    page.fill("input[name='password']", password)
    page.click("button:has-text('Log in')")
    page.wait_for_load_state("networkidle")

def test_quiz_flow_mocked():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        username = generate_user()
        password = "supersecure123"

        register_user(page, username, password)
        login_user(page, username, password)

        page.goto(f"{BASE_URL}/quiz", wait_until="domcontentloaded", timeout=20000)

        # Confirm test mode (assuming your app shows TEST in the UI)
        assert "TEST" in page.content(), "Expected TEST mode indicator missing"

        # Make incorrect guesses with explicit waits for feedback
        page.fill("input[name='guess']", "Pikachu")
        page.click("button[type='submit']")
        page.wait_for_selector("text=incorrect", timeout=5000)
        assert "incorrect" in page.content(), "Expected incorrect guess message not found"

        page.fill("input[name='guess']", "bulbasaur")
        page.click("button[type='submit']")
        page.wait_for_selector("text=incorrect", timeout=5000)
        page.wait_for_selector("text=Ding", timeout=5000)
        assert "Ding" in page.content(), "Expected Ding feedback missing"

        # Wait for winner message
        page.wait_for_selector("text=Ding Ding Ding! We have a winner!", timeout=10000)
        assert "Ding Ding Ding!" in page.content(), "Winner message missing"

        browser.close()
