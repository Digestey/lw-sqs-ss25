from playwright.sync_api import sync_playwright
import os

def test_docs_page():
    base_url = os.getenv("BASE_URL", "http://localhost:8000")

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"{base_url}/docs")
        assert "Swagger" in page.content() or "FastAPI" in page.title()
        browser.close()
