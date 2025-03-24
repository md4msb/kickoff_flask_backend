import json
import os

FILE_PATH = "players.json"

def load_players():
    if not os.path.exists(FILE_PATH):
        return []
    with open(FILE_PATH, "r") as file:
        try:
            return json.load(file)
        except json.JSONDecodeError:
            return []

def save_players(players):
    with open(FILE_PATH, "w") as file:
        json.dump(players, file, indent=4)

def getAllPlayers():
    return load_players()

def addNewPlayer(data):
    players = load_players()  # Load existing players

    if "players" not in data:
        return {"error": "Invalid request. 'players' key missing."}, 400

    existing_names = {player["name"] for player in players}  # Existing player names
    max_id = max([player.get("id", 0) for player in players], default=0)  # Get the last used ID

    new_players = data["players"]
    added_players = []
    skipped_players = []

    for player in new_players:
        name = player.get("name")
        position = player.get("position")
        strength = player.get("strength")

        if not name or not position or strength is None:
            skipped_players.append({"player": player, "reason": "Missing required fields"})
            continue  # Skip this player

        if name in existing_names:
            skipped_players.append({"player": player, "reason": "Player already exists"})
            continue  # Skip duplicate player

        max_id += 1  # Increment ID
        new_player = {"id": max_id, "name": name, "position": position, "strength": strength}
        players.append(new_player)  # Add to player list
        added_players.append(new_player)

    save_players(players)  # Save updated players list

    return {
        "message": f"{len(added_players)} player(s) added successfully.",
        "added_players": added_players,
        "skipped_players": skipped_players
    }, 201


def editPlayer(data):
    players = load_players()
    player_id = data.get("id")

    for player in players:
        if player["id"] == player_id:
            player["name"] = data.get("name", player["name"])
            player["position"] = data.get("position", player["position"])
            player["strength"] = data.get("strength", player["strength"])
            save_players(players)
            return {"message": "Player updated successfully", "success": True}, 200

    return {"message": "Player not found", "success": False}, 404

def deletePlayer(data):
    players = load_players()
    player_id = data.get("id")

    for player in players:
        if player["id"] == player_id:
            players.remove(player)
            save_players(players)
            return {"message": "Player deleted successfully", "success": True}, 200

    return {"message": "Player not found", "success": False}, 404
