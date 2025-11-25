from flask import Flask, request
import hmac
import hashlib
import json
import database
import os

IPN_SECRET = os.getenv("IPN_SECRET")

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():

    data = request.json
    received_hmac = request.headers.get("x-nowpayments-sig", "")

    # Validate signature
    digest = hmac.new(
        IPN_SECRET.encode(),
        msg=json.dumps(data, separators=(",", ":"), sort_keys=True).encode(),
        digestmod=hashlib.sha512
    ).hexdigest()

    if digest != received_hmac:
        return "Invalid signature", 400

    # Process payment
    if data.get("payment_status") == "finished":
        user_id = int(data["order_id"])
        database.add_credit(user_id)

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
