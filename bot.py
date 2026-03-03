import requests
from bs4 import BeautifulSoup
import os
import hashlib
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================
# CONFIG
# ==========================

BOT_TOKEN = "8783548415:AAGKEbrcrvhnN-Ma4_AuECcCyO_yKLpgut0"
CHAT_ID = "556401310"

strict_keywords = [
    "trainee eto",
    "eto cadet"
]

# ==========================
# TARGETED CAREER PAGES
# (Focused serious employers)
# ==========================

career_pages = {
    # Ship Management
    "Anglo Eastern": "https://www.angloeastern.com/careers/",
    "V.Group": "https://www.vships.com/careers/",
    "Synergy Marine": "https://synergymarinegroup.com/careers/",
    "Fleet Management": "https://www.fleetship.com/careers/",
    "Bernhard Schulte (BSM)": "https://www.bs-shipmanagement.com/careers/",
    "Thome Group": "https://www.thome.com/careers/",
    "OSM Thome": "https://www.osmthome.com/careers/",

    # Offshore
    "Tidewater": "https://www.tdw.com/careers/",
    "Bourbon Offshore": "https://www.bourbonoffshore.com/careers/",
    "DOF": "https://www.dof.com/careers/",
    "Seadrill": "https://www.seadrill.com/careers/",
    "Subsea7": "https://careers.subsea7.com/",

    # Indian Employers
    "Great Eastern Shipping": "https://www.greatship.com/careers/",
    "Shipping Corporation of India": "https://www.shipindia.com/careers",
    "Seven Islands Shipping": "https://www.sevenislands.co.in/careers/"
}

# ==========================
# MEMORY SYSTEM
# ==========================

history_file = "sent_jobs.txt"

if not os.path.exists(history_file):
    open(history_file, "w").close()

with open(history_file, "r") as f:
    sent_hashes = set(f.read().splitlines())

new_results = []

# ==========================
# SCRAPE LOGIC
# ==========================

for company, url in career_pages.items():
    try:
        response = requests.get(url, timeout=15, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract only link texts (likely job titles)
        links = soup.find_all("a")

        for link in links:
            text = link.get_text(strip=True).lower()

            if not text:
                continue

            # STRICT MATCH
            if any(keyword in text for keyword in strict_keywords):

                job_url = link.get("href")

                if job_url and not job_url.startswith("http"):
                    job_url = url.rstrip("/") + "/" + job_url.lstrip("/")

                unique_id = hashlib.md5((company + text).encode()).hexdigest()

                if unique_id not in sent_hashes:
                    new_results.append(
                        f"🚢 {company}\nPosition: {text.title()}\nLink: {job_url}\n"
                    )
                    sent_hashes.add(unique_id)

    except Exception as e:
        print(f"Error checking {company}: {e}")

# ==========================
# SEND ALERT
# ==========================

if new_results:
    message = "🔥 TRAINEE ETO / ETO CADET VACANCIES FOUND:\n\n" + "\n".join(new_results[:5])

    telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    data = {
        "chat_id": CHAT_ID,
        "text": message
    }

    requests.post(telegram_url, data=data)

    with open(history_file, "w") as f:
        for h in sent_hashes:
            f.write(h + "\n")

    print("Trainee ETO vacancy alert sent.")
else:
    print("No Trainee ETO / ETO Cadet vacancies detected.")