import os
import requests

def notify_telegram(topic, status="Success"):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id:
        print("Telegram info missing.")
        return

    message = f"🤖 *Agent Bot Update*\n\n✅ Status: {status}\n📝 Topic: {topic}\n🔗 View: github.com/{os.getenv('GITHUB_REPOSITORY')}"
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    try:
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
    except Exception as e:
        print(f"Error: {e}")

# IMPORTANT: Call this function inside your run_once function
# Example: 
# notify_telegram(topic)
