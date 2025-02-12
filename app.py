from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import datetime
import json
import os

app = Flask(__name__)

# Configurations
UPLOAD_FOLDER = 'static/uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
WINNERS_FILE = 'winners.json'

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



WINNERS_FILE = 'winners.json'  # Ensure this file exists

import json
import os

WINNERS_FILE = 'winners.json'  # Ensure this file exists

# Load winners from JSON with Debugging
def load_winners():
    print("🔍 DEBUG: Checking if winners.json exists...")  # Debugging step

    if os.path.exists(WINNERS_FILE):
        print(f"✅ DEBUG: {WINNERS_FILE} found! Attempting to read file...")
        try:
            with open(WINNERS_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                print(f"📜 DEBUG: Successfully loaded data: {data}")  # Print loaded data
                return data
        except json.JSONDecodeError as e:
            print(f"❌ ERROR: Failed to parse {WINNERS_FILE}: {e}")  # Log parsing error
            return []  # Return empty list if JSON is invalid
    else:
        print(f"⚠️ WARNING: {WINNERS_FILE} not found! Returning empty list.")
        return []  # Return empty list if file is missing


# Save Winners to JSON
def save_winners(winners):
    with open(WINNERS_FILE, "w") as file:
        json.dump(winners, file, indent=4)

# 🏏 **API Configuration**
LIVE_SCORE_API_URL = "https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/matches/live"
MATCHES_API_URL = "https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/matches/upcoming"

HEADERS = {
    'x-apihub-key': 'LkMjsGJlwnsHOGfarmx3-iYvcCaF7-PPIj1FWb578LHp4osTdS',
    'x-apihub-host': 'Cricbuzz-Official-Cricket-API.allthingsdev.co',
    'x-apihub-endpoint': 'e0cb5c72-38e1-435e-8bf0-6b38fbe923b7'
}

# 📌 **Fetch Live Scores**
def fetch_live_scores():
    print("🔍 DEBUG: Fetching live scores from API...")

    try:
        response = requests.get(LIVE_SCORE_API_URL, headers=HEADERS)
        response.raise_for_status()
        raw_data = response.json()

        print(f"📜 DEBUG: Raw API Response: {json.dumps(raw_data, indent=2)}")

        live_scores = []

        if "typeMatches" not in raw_data:
            print("⚠️ DEBUG: 'typeMatches' key not found in response!")
            return []

        for match_type in raw_data.get("typeMatches", []):
            print(f"🎯 DEBUG: Processing match type: {match_type.get('matchType', 'Unknown')}")

            for series in match_type.get("seriesMatches", []):
                series_data = series.get("seriesAdWrapper", {})
                
                if "matches" not in series_data:
                    print("⚠️ DEBUG: 'matches' key not found in series data!")
                    continue

                for match in series_data.get("matches", []):
                    match_info = match.get("matchInfo", {})

                    print(f"🏏 DEBUG: Found match: {match_info.get('matchDesc', 'Unknown Match')}")
                    print(f"🟢 DEBUG: Match state: {match_info.get('state', 'No State')}")

                    if match_info.get("state", "").lower() in ["live", "in progress", "playing"]:
                        live_details = {
                            "team1": match_info.get("team1", {}).get("teamName", "Unknown"),
                            "team2": match_info.get("team2", {}).get("teamName", "Unknown"),
                            "matchDesc": match_info.get("matchDesc", ""),
                            "venue": match_info.get("venueInfo", {}).get("ground", "Unknown"),
                            "city": match_info.get("venueInfo", {}).get("city", ""),
                            "score": match.get("matchScore", {}).get("team1Score", {}).get("inngs1", {}).get("runs", "N/A"),
                            "wickets": match.get("matchScore", {}).get("team1Score", {}).get("inngs1", {}).get("wickets", "N/A"),
                            "overs": match.get("matchScore", {}).get("team1Score", {}).get("inngs1", {}).get("overs", "N/A")
                        }

                        print(f"✅ DEBUG: Live match added: {live_details}")
                        live_scores.append(live_details)

        print(f"🎉 DEBUG: Total live matches found: {len(live_scores)}")
        return live_scores[:5]  # Show only 5 live matches max

    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Failed to fetch live scores: {e}")
        return []



def fetch_matches():
    try:
        response = requests.get(MATCHES_API_URL, headers=HEADERS)
        response.raise_for_status()
        raw_data = json.loads(response.text)

        today = datetime.datetime.now().date()
        today_matches = []
        upcoming_matches = []

        for match_type in raw_data.get("typeMatches", []):
            for series in match_type.get("seriesMatches", []):
                series_data = series.get("seriesAdWrapper", {})

                for match in series_data.get("matches", []):
                    match_info = match.get("matchInfo", {})
                    start_time = int(match_info.get("startDate", 0)) / 1000
                    match_date = datetime.datetime.fromtimestamp(start_time).date()

                    match_details = {
                        "team1": match_info.get("team1", {}).get("teamName", "Unknown"),
                        "team2": match_info.get("team2", {}).get("teamName", "Unknown"),
                        "matchDesc": match_info.get("matchDesc", ""),
                        "matchFormat": match_info.get("matchFormat", ""),
                        "venue": match_info.get("venueInfo", {}).get("ground", "Unknown"),
                        "city": match_info.get("venueInfo", {}).get("city", ""),
                        "start_time": datetime.datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
                    }

                    if match_date == today:
                        today_matches.append(match_details)
                    elif match_date > today:
                        upcoming_matches.append(match_details)

        return today_matches[:10], upcoming_matches[:10]

    except requests.exceptions.RequestException as e:
        print(f"Error fetching matches: {e}")
        return [], []

@app.route("/livescores")
def show_live_scores():
    print("🚀 DEBUG: Loading Live Scores Page...")

    # Fetch live scores
    live_scores = fetch_live_scores()

    if live_scores is None:
        print("⚠ DEBUG: No live scores found. Setting an empty list.")
        live_scores = []

    print(f"📡 DEBUG: Live Scores Sent to livescores.html: {live_scores}")

    return render_template("livescores.html", live_scores=live_scores)

@app.route("/")
def home_page():
    winners = load_winners()
    print(f"🎯 DEBUG: Winners passed to index.html: {winners}")  # Log data before rendering
    return render_template("index.html", winners=winners[:3])  # Show only latest 3 winners

# ✅ **Admin Panel**
@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        amount = request.form["amount"]
        image = request.files["image"]

        if image:
            image_filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_filename)

            new_winner = {
                "name": name,
                "age": age,
                "amount": amount,
                "image": image_filename
            }

            winners = load_winners()
            winners.insert(0, new_winner)
            winners = winners[:3]
            save_winners(winners)

            return redirect(url_for("home_page"))

    return render_template("admin.html")

# ✅ **Other Routes**
@app.route("/users")
def users():
    return render_template("users.html")

@app.route("/Loginrequired")
def login_required():
    return render_template("Loginrequired.html")

@app.route("/submit", methods=['POST'])
def submit():
    name = request.form.get('name')
    phone = request.form.get('phone')

    if len(name) < 3 or len(phone) != 10 or not phone.isdigit():
        return "Invalid input. Please go back and enter correct details."

    return redirect(url_for("guarantee_letter", name=name, phone=phone))

@app.route("/Gaurnteeletter")
def guarantee_letter():
    name = request.args.get("name", "Guest")
    phone = request.args.get("phone", "Unknown")
    return render_template("Gaurnteeletter.html", name=name, phone=phone)

@app.route("/bookplace")
def book_place():
    return render_template("bookplace.html")

@app.route("/matches")
def show_matches():
    today_matches, upcoming_matches = fetch_matches()
    return render_template("matches.html", today_matches=today_matches, upcoming_matches=upcoming_matches)
@app.route('/bookrank')
def book_rank():
    return render_template('bookrank.html')

@app.route("/home")
def go_home():
    return redirect(url_for("home_page"))  # Redirects to the main home function

if __name__ == '__main__':
    app.run(debug=True)
