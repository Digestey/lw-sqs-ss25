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

        page.goto(f"{BASE_URL}/quiz",
                  wait_until="domcontentloaded", timeout=20000)

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
        page.wait_for_selector("#quiz-message", timeout=10000)
        assert page.locator("#quiz-message").is_visible()


        # Wait for winner message
        page.wait_for_selector(
            "text=Ding Ding Ding! We have a winner!", timeout=10000)
        assert "Ding Ding Ding!" in page.content(), "Winner message missing"

        browser.close()


def test_quiz_flow_highscore_submission():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        username = generate_user()
        password = "supersecure123"

        # REGISTER and LOGIN first
        register_user(page, username, password)
        login_user(page, username, password)

        page.goto(f"{BASE_URL}/quiz",
                  wait_until="domcontentloaded", timeout=20000)

        # Wait for quiz page to load (simplified)
        assert "TEST" in page.content(), "Expected TEST mode indicator missing"

        # Simulate a correct guess to complete the quiz (or just navigate to the final state)
        page.fill("input[name='guess']", "bulbasaur")
        page.click("button[type='submit']")
        page.wait_for_selector(
            "text=Ding Ding Ding! We have a winner!", timeout=10000)
        assert "Ding Ding Ding!" in page.content(), "Winner message missing"

        # --- Attempt to submit highscore while LOGGED IN ---

        # After finishing quiz and confirming winner message
        page.wait_for_selector(
            "text=Ding Ding Ding! We have a winner!", timeout=10000)
        assert "Ding Ding Ding!" in page.content(), "Winner message missing"

        # Wait for the submit score button to appear (visible)
        page.wait_for_selector("#submit-score-button",
                               state="visible", timeout=10000)

        # Listen for alert dialog on submission
        def on_dialog(dialog):
            assert dialog.message == "Highscore submitted!"
            dialog.dismiss()

        page.on("dialog", on_dialog)

        # Now click the button
        page.click("#submit-score-button")

        # --- Now test submitting highscore while NOT LOGGED IN ---

        # Close the logged-in context and create a fresh context (not logged in)
        context.close()
        context2 = browser.new_context()
        page2 = context2.new_page()

        page2.goto(f"{BASE_URL}/quiz",
                   wait_until="domcontentloaded", timeout=20000)

        # Listen for alert on failed submit due to not logged in
        def on_dialog_unauth(dialog):
            assert dialog.message == "You must be logged in to submit a score."
            dialog.dismiss()

        page2.on("dialog", on_dialog_unauth)

        # Click submit score button again in logged-out session
        page2.click("#submit-score-button")

        browser.close()
