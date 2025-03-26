from models import db, Player, Match

def addNewPlayer(data):
    if "players" not in data:
        return {"error": "Invalid request. 'players' key missing."}, 400

    existing_names = {player.name for player in Player.query.all()}  # Fetch existing player names from DB

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

        new_player = Player(name=name, position=position, strength=strength)
        db.session.add(new_player)
        added_players.append({"name": name, "position": position, "strength": strength})

    db.session.commit()  # Save to DB

    return {
        "message": f"{len(added_players)} player(s) added successfully.",
        "added_players": added_players,
        "skipped_players": skipped_players
    }, 201

def editPlayer(data):  
    player = Player.query.get(data.get("id"))

    if not player:
        return {"message": "Player not found", "success": False}, 404
    
    player.name = data.get("name", player.name)
    player.position = data.get("position", player.position)
    player.strength = data.get("strength", player.strength)

    db.session.commit()
    return {"message": "Player updated successfully", "success": True}, 200

def deletePlayer(data):
    player = Player.query.get(data.get("id"))

    if not player:
        return {"message": "Player not found", "success": False}, 404

    db.session.delete(player)
    db.session.commit()
    return {"message": "Player deleted successfully", "success": True}, 200

def submitMatchResult(data):
    if not data or "winner" not in data or "teams" not in data:
        return {"error": "Invalid input format"}, 400

    # Create a new match entry
    match_result = Match(
        winner=data["winner"],
        team1=data["teams"]["team1"],
        team2=data["teams"]["team2"]
        )

    db.session.add(match_result)
    db.session.commit()  # Save match to PostgreSQL

    return {"message": "Match result saved successfully!"}, 201
