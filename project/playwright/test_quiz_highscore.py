import os
import uuid
import pytest
from playwright.sync_api import Page, Dialog, sync_playwright


BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")

def generate_user():
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    return unique_username

def test_quiz_flow_mocked():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        
        print(os.getenv("USE_TEST_POKEMON")=="1")
        username = generate_user()
        # ---- Register ----
        page.goto(f"{BASE_URL}/register")
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", "supersecure123")
        page.fill("input[name='repeat_password']", "supersecure123")
        page.get_by_role("button", name="Register Now!").click()

        # ---- Login ----
        page.goto(f"{BASE_URL}/login")
        page.fill("input[name='username']", username)
        page.fill("input[name='password']", "supersecure123")
        page.get_by_role("button", name="Log in").click()

        # ---- Quiz ----
        page.goto(f"{BASE_URL}/quiz", wait_until="domcontentloaded")
        print("======")
        print(page.content())
        print("======")
        assert "TEST" in page.content()
        page.fill("input[name='guess']", "Pikachu")
        page.click("button[type='submit']")
        assert "incorrect" in page.content()
        
        page.fill("input[name='guess']", "bulbasaur")
        page.click("button[type='submit']")
        assert "incorrect" in page.content()
        assert "Ding" in page.content()

        # ---- Assertions ----
        page.wait_for_selector("text=Ding Ding Ding! We have a winner!")
        assert "Ding Ding Ding!" in page.content()
        
        browser.close()
