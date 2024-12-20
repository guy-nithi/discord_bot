from flask import Flask, Response, request
from threading import Thread
import os
import logging
import time

# Configure Flask logging
logging.getLogger('werkzeug').setLevel(logging.ERROR)
app = Flask('')

@app.route('/', methods=['GET', 'HEAD'])
def home():
    try:
        if request.method == 'HEAD':
            return Response(status=200)
        return "Bot is alive!"
    except Exception as e:
        print(f"Error in web request: {e}")
        return Response(status=200)

def run():
    retries = 0
    while True:
        try:
            print("\n=== Web Server Details ===")
            print("Bot URL: https://101ca301-cf3c-4fe7-ba45-83cf8fe2e9c9-00-1vv2fv75732lg.sisko.replit.dev")
            print("Server is running!")
            print("========================\n")
            app.run(host='0.0.0.0', port=8080)
        except Exception as e:
            print(f"Error starting web server: {e}")
            retries += 1
            if retries < 5:
                print(f"Retrying in 5 seconds... (Attempt {retries}/5)")
                time.sleep(5)
            else:
                print("Failed to start web server after 5 attempts")
                break

def keep_alive():
    while True:
        try:
            t = Thread(target=run)
            t.daemon = True
            t.start()
            print("Keep alive server started!")
            return  # Exit if server starts successfully
        except Exception as e:
            print(f"Error in keep_alive: {e}")
            print("Retrying in 5 seconds...")
            time.sleep(5)
