from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
import re
import json

app = Flask(__name__)

@app.route('/extract_hls', methods=['POST'])
def extract_hls():
    try:
        data = request.get_json()
        video_url = data['video_url']

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
    app.run(debug=True)
