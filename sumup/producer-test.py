import json
import time
import random
from datetime import datetime, timedelta


CHAMPIONS = [
    "Valhein", "Butterfly", "Murad", "Lauriel", "Nakroth", "Tel'Annas", "Zuka",
    "Raz", "Violet", "Yorn", "Zephys", "Airi", "Ilumia", "Arthur", "Toro",
    "Capheny", "Quillen", "Elsu", "Rourke", "Ignis", "Kil'Groth", "Lindis", "D'Arcy",
    "Florentino", "Hayate", "Krizzix", "Veres", "Dirak", "Ata", "Rouie", "Yena",
    "Paine", "Bright", "Keera", "Laville", "Ishar", "Zata", "Allain", "Lorion",
    "Aya", "Thorne", "Helen", "Azen'Ka", "Omega", "Skud", "Taara", "Lumburr",
    "Gildur", "Grakk", "Cresht", "Baldum", "Ormarr", "Wonder Woman", "Superman"
]

def generate_player_stats(champion):
    """Generates plausible stats for a single player."""
    # Generate KDA
    kills = random.randint(0, 15)
    deaths = random.randint(0, 12)
    assists = random.randint(0, 25)

    # Generate Damage/Tanked based roughly on KDA and champion type (simplified)
    total_damage_dealt = random.randint(15000, 60000) + kills * 1000 + assists * 500
    total_damage_taken = random.randint(10000, 50000) + deaths * 2000

    # Simulate gold earned by player (simplified based on KDA, not perfect)
    gold_earned = 300 + kills * 300 + assists * 150 + random.randint(3000, 10000) # Base gold + gold from kills/assists + farming/passives
    # Ensure gold is non-negative
    gold_earned = max(0, gold_earned)


    return {
        "champion": champion,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "total_damage_dealt": total_damage_dealt,
        "total_damage_taken": total_damage_taken,
        "gold_earned": gold_earned # Adding player gold earned
    }

def generate_simulated_match_data():
    """Generates data for a single simulated match."""
    match_id = f"simulated_{int(time.time() * 1000)}_{random.randint(1000, 9999)}" # Unique ID based on timestamp

    # Simulate match duration between 1 and 1 seconds (always 1 second)
    duration_minutes = 0
    duration_seconds = 1

    # Simulate start and end time
    end_time = datetime.now()
    start_time = end_time - timedelta(seconds=duration_seconds)

    # Select 10 unique champions for the match
    if len(CHAMPIONS) < 10:
         # Handle case where there aren't enough champions
        picked_champions = random.sample(CHAMPIONS, len(CHAMPIONS)) + random.choices(CHAMPIONS, k=10-len(CHAMPIONS))
        random.shuffle(picked_champions) # Shuffle to mix teams
    else:
        picked_champions = random.sample(CHAMPIONS, 10)

    players_data = []
    # Assign players to teams (simple alternating) and generate base stats
    for i in range(10):
        team_id = 100 if i < 5 else 200 # First 5 players are team 100, next 5 are team 200
        champion = picked_champions[i]
        player_stats = generate_player_stats(champion)
        players_data.append({
            "participant_id": i + 1,
            "team_id": team_id,
            **player_stats
        })

    # --- Determine the winning team (randomly for simulation) ---
    winning_team_id = random.choice([100, 200])

    # --- Add 'win' status and calculate team totals ---
    total_kills_team1 = 0
    total_gold_team1 = 0
    total_kills_team2 = 0
    total_gold_team2 = 0

    for player in players_data:
        # Xóa trường 'win' khỏi từng player
        if 'win' in player:
            del player['win']
        if player["team_id"] == 100:
            total_kills_team1 += player["kills"]
            total_gold_team1 += player["gold_earned"]
        else: # team_id == 200
            total_kills_team2 += player["kills"]
            total_gold_team2 += player["gold_earned"]

    # Simulate team objectives (simplified)
    # For a more realistic simulation, you might adjust objectives slightly based on which team won.
    team1_objectives = {
        "dragons": random.randint(0, 5),
        "barons": random.randint(0, 2),
        "towers": random.randint(0, 11),
        "inhibitors": random.randint(0, 6),
        "heralds": random.randint(0, 2)
    }
    team2_objectives = {
         "dragons": random.randint(0, 5),
        "barons": random.randint(0, 2),
        "towers": random.randint(0, 11),
        "inhibitors": random.randint(0, 6),
        "heralds": random.randint(0, 2)
    }

    # --- Add NEW team-level stats ---
    team1_objectives["total_kills"] = total_kills_team1
    team1_objectives["total_gold"] = total_gold_team1
    team2_objectives["total_kills"] = total_kills_team2
    team2_objectives["total_gold"] = total_gold_team2

    # Thêm trường 'win' vào team1_objectives và team2_objectives
    team1_objectives["win"] = (winning_team_id == 100)
    team2_objectives["win"] = (winning_team_id == 200)

    # Simulate First Objective statuses (booleans)
    # Make winning team slightly more likely to get first objectives (optional bias)
    team1_objectives["first_blood"] = random.random() < (0.6 if winning_team_id == 100 else 0.4)
    team2_objectives["first_blood"] = not team1_objectives["first_blood"] # Only one team gets first blood

    team1_objectives["first_tower"] = random.random() < (0.7 if winning_team_id == 100 else 0.3)
    team2_objectives["first_tower"] = not team1_objectives["first_tower"] # Only one team gets first tower

    # First inhibitor only happens if the team actually took an inhibitor
    team1_objectives["first_inhibitor"] = (team1_objectives["inhibitors"] > 0) and (random.random() < (0.8 if winning_team_id == 100 else 0.2))
    # If team 1 got first inhibitor, team 2 can't. Otherwise, team 2 might if they took inhibitors.
    team2_objectives["first_inhibitor"] = (not team1_objectives["first_inhibitor"]) and (team2_objectives["inhibitors"] > 0) and (random.random() < (0.8 if winning_team_id == 200 else 0.2))
    # Edge case: if somehow both got first inhibitor status (unlikely with logic above but for safety)
    if team1_objectives["first_inhibitor"] and team2_objectives["first_inhibitor"]:
         if winning_team_id == 100: team2_objectives["first_inhibitor"] = False
         else: team1_objectives["first_inhibitor"] = False


    # Adjust objectives slightly for realism (e.g., team with more towers/inhibs likely won)
    # This basic simulation doesn't determine a winner, but you could add that logic.
    if winning_team_id == 100:
         team1_objectives["towers"] = max(team1_objectives["towers"], random.randint(6, 11)) # Winning team likely got more towers
         team2_objectives["towers"] = min(team2_objectives["towers"], random.randint(0, 5)) # Losing team likely got fewer towers
         team1_objectives["inhibitors"] = max(team1_objectives["inhibitors"], random.randint(1, 6)) # Winning team likely got inhibitors
         team2_objectives["inhibitors"] = min(team2_objectives["inhibitors"], random.randint(0, 2)) # Losing team likely got fewer/no inhibitors
         team1_objectives["total_gold"] = max(team1_objectives["total_gold"], team2_objectives["total_gold"] + random.randint(5000, 20000)) # Winning team has significantly more gold
    else: # winning_team_id == 200
         team2_objectives["towers"] = max(team2_objectives["towers"], random.randint(6, 11))
         team1_objectives["towers"] = min(team1_objectives["towers"], random.randint(0, 5))
         team2_objectives["inhibitors"] = max(team2_objectives["inhibitors"], random.randint(1, 6))
         team1_objectives["inhibitors"] = min(team1_objectives["inhibitors"], random.randint(0, 2))
         team2_objectives["total_gold"] = max(team2_objectives["total_gold"], team1_objectives["total_gold"] + random.randint(5000, 20000))


    match_data = {
        "match_id": match_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": duration_seconds,
        "team1_summary": team1_objectives, # Renamed for clarity
        "team2_summary": team2_objectives, # Renamed for clarity
        "players": players_data # players_data now includes the 'gold_earned' field
    }

    return match_data, duration_seconds

# --- Main Producer Loop ---
if __name__ == "__main__":
    print("Starting simulated LoL data producer with more team stats...")
    print("Generating a new match record every simulated match duration.")

    try:
        while True:
            match_data, simulated_duration = generate_simulated_match_data()

            # Output the generated data
            match_json_str = json.dumps(match_data)
            print(str(match_json_str))
            # print(
            #     f"\n--- Match {match_data['match_id']} generated. Simulating {simulated_duration:.2f} seconds until next match. ---")

            # Wait for the duration of the simulated match
            time.sleep(simulated_duration)

    except KeyboardInterrupt:
        print("\nProducer stopped manually.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")