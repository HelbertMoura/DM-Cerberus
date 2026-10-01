import sys
import urllib.request
import urllib.parse
import json

BOT_TOKEN = "8509721003:AAGPSJgnGiR95kG07GMQqPTFIGqQEqWtM50"
CHAT_ID = "6495506547"

def send_notification(message: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception as e:
        print(f"Error sending telegram notification: {e}", file=sys.stderr)
        return False

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else "🔔 [Maestro]: Notificação de teste."
    success = send_notification(msg)
    sys.exit(0 if success else 1)
