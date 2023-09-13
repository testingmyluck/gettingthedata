import os
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import re
import json
import requests
from flask_cors import CORS  # Import Flask-CORS

app = Flask(__name__)

# Get the port number from the PORT environment variable, or use a default value (5000)
port = int(os.environ.get("PORT", 5000))

# Configure CORS to allow requests from your Blogger site
CORS(app, resources={r"/extract_hls": {"origins": "https://testingforwidget.blogspot.com"}})

@app.route('/extract_hls', methods=['GET'])
def extract_hls():
    try:
        video_url = request.args.get('video_url')

        if not video_url:
            return jsonify({"error": "Video URL parameter is missing."}), 400

        response = requests.get(video_url)

        if response.status_code == 200:
            video_page = BeautifulSoup(response.text, 'html.parser')

            script_tags = video_page.find_all('script')

            for script_tag in script_tags:
                script_text = script_tag.get_text()
                if 'html5player.setVideoHLS' in script_text:
                    match = re.search(r"html5player\.setVideoHLS\('([^']+)'\)", script_text)
                    if match:
                        hls_url = match.group(1)

                        video_info = {
                            "hls_url": hls_url,
                        }

                        return jsonify(video_info), 200

            return jsonify({"error": "No 'html5player.setVideoHLS' script found on the page."}), 404

        else:
            return jsonify({"error": "Failed to retrieve the video page."}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the app on the specified port
    app.run(host='0.0.0.0', port=port)
