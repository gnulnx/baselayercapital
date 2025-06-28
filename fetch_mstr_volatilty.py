from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from PIL import Image
import pytesseract
import time


def fetch_volatility_via_ocr():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")  # important for rendering
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.90 Safari/537.36"
    )
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd(
        "Page.addScriptToEvaluateOnNewDocument",
        {
            "source": """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
    """
        },
    )
    try:
        driver.get("https://strategy.com")
        time.sleep(8)  # give React enough time to render

        screenshot_path = "strategy_fullpage.png"
        driver.save_screenshot(screenshot_path)

        # print(f"🖼️ Screenshot saved to {screenshot_path}")

        image = Image.open(screenshot_path)
        text = pytesseract.image_to_string(image)

        # print("🧠 OCR Text Output:")
        # print(text)

        return text

    finally:
        driver.quit()


if __name__ == "__main__":
    text = fetch_volatility_via_ocr()

    # Optional: parse for volatility numbers
    import re

    # Normalize the OCR text
    normalized = text.replace("\n", " ").replace("  ", " ")

    iv_match = re.search(r"Implied Volatility\s+(\d+)%", normalized, re.IGNORECASE)
    hv_match = re.search(r"Historic Volatility.*?(\d+)%", normalized, re.IGNORECASE)

    if iv_match and hv_match:
        print(f"📊 Implied Volatility: {iv_match.group(1)}%")
        print(f"📊 Historic Volatility: {hv_match.group(1)}%")
    else:
        print("⚠️ Could not extract volatility values from OCR.")
