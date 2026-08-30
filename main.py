import os
import requests

def send_telegram(message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, json={"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})

def run_bot():
    print("Agent is starting...")
    
    # This is a simple test to see if it works
    topic = "How to choose a mechanical keyboard"
    
    try:
        # 1. The Bot logic would go here
        # (For now, we are testing the notification)
        
        status_report = f"🚀 *Agent Bot is Active!*\n\n📝 *Last Topic:* {topic}\n✅ *Status:* Successfully ran."
        send_telegram(status_report)
        print("Success! Message sent to Telegram.")
        
    except Exception as e:
        error_msg = f"❌ *Bot Error:*\n{str(e)}"
        send_telegram(error_msg)
        print(f"Error: {e}")

if __name__ == "__main__":
    run_bot()
