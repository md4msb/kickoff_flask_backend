from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "Kickoff Flask Backend is Running! 🚀"

# Get the PORT from Render's environment variable
port = int(os.environ.get("PORT", 10000))  # Default is 10000

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=port, debug=True)

# Match Data File
MATCH_FILE = "match_data.json"

# Load Match History
def load_match_data():
    if not os.path.exists(MATCH_FILE):
        return {"matches": []}  # Return empty if file does not exist

    with open(MATCH_FILE, "r") as file:
        content = file.read().strip()

        if not content:
            return {"matches": []}

        return json.loads(content)

# Save Match History
def save_match_data(match):
    data = load_match_data()
    data["matches"].append(match)

    with open(MATCH_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Function to Split Teams Fairly
def split_teams(players):
    sorted_players = sorted(players, key=lambda x: x["strength"], reverse=True)
    team1, team2 = [], []
    team1_strength, team2_strength = 0, 0

    for player in sorted_players:
        if team1_strength <= team2_strength:
            team1.append(player)
            team1_strength += player["strength"]
        else:
            team2.append(player)
            team2_strength += player["strength"]

    return {"team1": team1, "team2": team2}

# Function to Recommend Teams Based on Match History
def recommend_teams(players):
    match_data = load_match_data()

    if not match_data["matches"]:  # No history, just balance based on strength
        return split_teams(players)

    # Count how many times each player has won
    winner_counts = {}
    
    for match in match_data["matches"]:
        if "winner" in match and match["winner"] in match:
            for player in match[match["winner"]]:
                winner_counts[player["name"]] = winner_counts.get(player["name"], 0) + 1

    # Sort players by how many times they have won
    sorted_players = sorted(players, key=lambda x: winner_counts.get(x["name"], 0), reverse=True)

    # Now balance the teams properly
    return split_teams(sorted_players)

# API to Recommend Teams
@app.route('/recommend-teams', methods=['POST'])
def get_recommendations():
    try:
        data = request.get_json()
        if not data or "players" not in data:
            return jsonify({"error": "Invalid input format"}), 400

        players = data["players"]
        teams = recommend_teams(players)

        return jsonify({"teams": teams})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API to Submit Match Result
@app.route('/submit-match', methods=['POST'])
def submit_match():
    try:
        data = request.get_json()
        if not data or "winner" not in data or "teams" not in data:
            return jsonify({"error": "Invalid input format"}), 400

        match_result = {
            "winner": data["winner"],
            "team1": data["teams"]["team1"],
            "team2": data["teams"]["team2"]
        }

        save_match_data(match_result)
        return jsonify({"message": "Match result saved successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run Flask Server
if __name__ == "__main__":
    app.run(debug=True)
