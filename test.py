import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

# from selenium_stealth import stealth


options = uc.ChromeOptions()
options.binary_location = "/usr/bin/google-chrome"
# options.experimental_options["debuggerAddress"] = "localhost:9222 "
options.add_argument(r"--user-data-dir=/home/baonguyen/.config/google-chrome")
options.add_argument(
    "--profile-directory=Profile 3"
)  # if you want to use default profile, otherwise mention that specific profile's dir name here
options.add_argument("-fullscreen")
# options.add_argument("--disable-gpu")
# options.add_argument("--no-sandbox")

driver = uc.Chrome(options=options, service=Service("./chromedriver"))

# stealth(
#     driver,
#     languages=["en-US", "en"],
#     vendor="Google Inc.",
#     platform="Win32",
#     webgl_vendor="Intel Inc.",
#     renderer="Intel Iris OpenGL Engine",
#     fix_hairline=True,
# )

driver.get("https://x.com/")
input("Press Enter after scanning QR code")
