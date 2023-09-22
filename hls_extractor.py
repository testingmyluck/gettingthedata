import os
from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import re
import json
import requests
from flask_cors import CORS
import random

app = Flask(__name__)

# Get the port number from the PORT environment variable, or use a default value (5000)
port = int(os.environ.get("PORT", 5000))

# Configure CORS to allow requests from multiple websites
CORS(app, resources={
    r"/extract_hls": {
        "origins": ["https://hdxxx-videoz.blogspot.com", "https://www.hotnippy.com"]
    }
})

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

            hls_url = ""
            video_url_high = ""
            mobile_show_inline = ""

            for script_tag in script_tags:
                script_text = script_tag.get_text()
                if 'html5player.setVideoHLS' in script_text:
                    match = re.search(r"html5player\.setVideoHLS\('([^']+)'\)", script_text)
                    if match:
                        hls_url = match.group(1)
                
                # Extract 'html5player.setVideoUrlHigh' argument
                if 'html5player.setVideoUrlHigh' in script_text:
                    match = re.search(r"html5player\.setVideoUrlHigh\('([^']+)'\)", script_text)
                    if match:
                        video_url_high = match.group(1)

            # Find the <div> with id="v-views"
            v_views_div = video_page.find('div', {'id': 'v-views'})
            if v_views_div:
                # Extract mobile_show_inline within <strong class="mobile-show-inline">
                mobile_show_inline_element = v_views_div.find('strong', {'class': 'mobile-show-inline'})
                if mobile_show_inline_element:
                    mobile_show_inline = mobile_show_inline_element.get_text().strip()

            # Generate a random rating in the range of 70% to 100%
            rating_good_perc = str(random.randint(70, 100)) + '%'

            video_info = {
                "hls_url": hls_url,
                "video_url_high": video_url_high,
                "mobile_show_inline": mobile_show_inline,
                "rating_good_perc": rating_good_perc,
            }

            return jsonify(video_info), 200

        else:
            return jsonify({"error": "Failed to retrieve the video page."}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Run the app on the specified port
    app.run(host='0.0.0.0', port=port)
