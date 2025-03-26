from flask import Flask, request, jsonify
import os
from flask_cors import CORS
from dotenv import load_dotenv
from models import db, Player, Match
from service import addNewPlayer, editPlayer, deletePlayer, submitMatchResult

# Load environment variables
load_dotenv()
DATABASE_URL = os.environ.get("DATABASE_URL")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)  # Initialize db with app

CORS(app)

# Ensure database tables are created
with app.app_context():
    db.create_all()

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
    matches = Match.query.all()  # Fetch all match records from the database

    if not matches:  # No history, just balance based on strength
        return split_teams(players)

    winner_counts = {}
    for match in matches:
        winning_team = match.team1 if match.winner == "team1" else match.team2

        for player in winning_team:
            player_name = player["name"]
            winner_counts[player_name] = winner_counts.get(player_name, 0) + 1

    sorted_players = sorted(players, key=lambda x: winner_counts.get(x["name"], 0), reverse=True)
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
        response, status = submitMatchResult(data)
        return jsonify(response), status
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all players
@app.route("/getAllPlayers", methods=["GET"])
def get_players():
    players = Player.query.all()
    return jsonify([{"id": p.id, "name": p.name, "position": p.position, "strength": p.strength} for p in players])

# Add a new player
@app.route("/addNewPlayers", methods=["POST"])
def add_player():
    data = request.get_json()
    response, status = addNewPlayer(data)
    return jsonify(response), status

# Edit an existing player
@app.route("/editPlayer", methods=["PUT"])
def edit_player():
    data = request.get_json()
    response, status = editPlayer(data)
    return jsonify(response), status

# Delete a player
@app.route("/deletePlayer", methods=["DELETE"])
def delete_player():
    data = request.get_json()
    response, status = deletePlayer(data)
    return jsonify(response), status

@app.route('/')
def home():
    return "Kickoff Flask Backend is Running! 🚀"

# Start Flask Server
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)), debug=True)
