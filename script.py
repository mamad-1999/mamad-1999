import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
BADGE_URL = "https://tryhackme.com/api/v2/badges/public-profile?userPublicId=3153096"
STREAK_FILE = "streak.txt"
TELEGRAM_API = f"https://api.telegram.org/bot{os.getenv('BOT_TOKEN')}/sendMessage"


def get_current_streak():
    try:
        response = requests.get(BADGE_URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        fire_icon = soup.find('i', class_='fa-fire')
        streak_element = fire_icon.find_next_sibling(
            'span', class_='details-text')

        if streak_element:
            return int(streak_element.text.split()[0])
        return None
    except Exception as e:
        print(f"Error getting streak: {e}")
        return None


def send_telegram_alert(message):
    params = {
        'chat_id': os.getenv('CHANNEL_ID'),
        'text': message,
        'parse_mode': 'HTML'
    }
    try:
        response = requests.post(TELEGRAM_API, params=params)
        response.raise_for_status()
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")


def main():
    current_streak = get_current_streak()
    if current_streak is None:
        return

    try:
        with open(STREAK_FILE, 'r') as f:
            previous_streak = int(f.read().strip())
    except (FileNotFoundError, ValueError):
        previous_streak = 0

    if current_streak > previous_streak:
        with open(STREAK_FILE, 'w') as f:
            f.write(str(current_streak))
        print(f"Streak updated to {current_streak}")
    else:
        message = f"🚨 TryHackMe Streak Alert! 🚨\nCurrent streak: {current_streak} days\nStreak has not increased!"
        send_telegram_alert(message)
        print("Streak alert sent")


if __name__ == "__main__":
    main()
