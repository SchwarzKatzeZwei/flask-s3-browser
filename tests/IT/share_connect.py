from playwright.sync_api import Page


def top_screen(page: Page) -> bool:
    page.goto("http://localhost:8001/")
    return True
