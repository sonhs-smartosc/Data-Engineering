import json
import time
import random
from datetime import datetime
from kafka import KafkaProducer

# Champions list
CHAMPIONS = [
    "Valhein", "Butterfly", "Murad", "Lauriel", "Nakroth", "Tel'Annas", "Zuka",
    "Raz", "Violet", "Yorn", "Zephys", "Airi", "Ilumia", "Arthur", "Toro",
    "Capheny", "Quillen", "Elsu", "Rourke", "Ignis", "Slimz", "Lindis", 
    "Ryoma", "Omen", "Kil'Groth", "Preyta", "Aleister", "Krixi", "Mganga", 
    "Diao Chan", "Jinna", "Skud", "Lumburr", "Grakk", "Chaugnar", "Ormarr", 
    "Taara", "Maloch", "Arduin", "Sephera", "Annette", "Dirak", "Zill", 
    "Wisp", "Fennik", "Wonder Woman", "Superman", "Batman", "The Flash", 
    "Cresht", "Roxie", "Florentino", "Yena", "Richter", "Errol"
]

# Match types
MATCH_TYPES = ["Ranked", "Normal", "Custom", "Tournament"]

# Map names
MAPS = ["Antaris Battlefield", "Valley of Kings", "Dragon's Altar"]

# Random game duration between 15-35 minutes
def generate_game_duration():
    return random.randint(15 * 60, 35 * 60)  # in seconds

# Generate teams (5 champions per team)
def generate_teams():
    available_champions = CHAMPIONS.copy()
    team1 = []
    team2 = []
    
    # Select 5 champions for team 1
    for _ in range(5):
        champion = random.choice(available_champions)
        team1.append(champion)
        available_champions.remove(champion)
        
    # Select 5 champions for team 2
    for _ in range(5):
        champion = random.choice(available_champions)
        team2.append(champion)
        available_champions.remove(champion)
        
    return team1, team2

# Generate player statistics for each champion
def generate_player_stats(champion, is_winning_team):
    kills = random.randint(0, 15)
    deaths = random.randint(0, 12)
    assists = random.randint(0, 20)
    
    # Winning team tends to have better stats
    if is_winning_team:
        kills += random.randint(0, 5)
        deaths = max(0, deaths - random.randint(0, 3))
        
    gold = random.randint(8000, 18000)
    damage_dealt = random.randint(20000, 150000)
    damage_taken = random.randint(15000, 100000)
    healing_done = random.randint(0, 30000)
    
    return {
        "champion": champion,
        "kills": kills,
        "deaths": deaths,
        "assists": assists,
        "gold": gold,
        "damage_dealt": damage_dealt,
        "damage_taken": damage_taken,
        "healing_done": healing_done
    }

# Generate a match result
def generate_match_result():
    match_id = f"MATCH-{random.randint(10000, 99999)}"
    timestamp = datetime.now().isoformat()
    match_type = random.choice(MATCH_TYPES)
    map_name = random.choice(MAPS)
    duration = generate_game_duration()
    
    team1, team2 = generate_teams()
    
    # Randomly decide which team wins
    winner = random.choice(["team1", "team2"])
    
    # Generate statistics for each player
    team1_stats = [generate_player_stats(champion, winner == "team1") for champion in team1]
    team2_stats = [generate_player_stats(champion, winner == "team2") for champion in team2]
    
    # Generate objective statistics
    objectives = {
        "team1_towers": random.randint(0, 9),
        "team2_towers": random.randint(0, 9),
        "team1_dragons": random.randint(0, 4),
        "team2_dragons": random.randint(0, 4),
        "team1_barons": random.randint(0, 2),
        "team2_barons": random.randint(0, 2)
    }
    
    match_result = {
        "match_id": match_id,
        "timestamp": timestamp,
        "match_type": match_type,
        "map": map_name,
        "duration": duration,
        "winner": winner,
        "team1": team1_stats,
        "team2": team2_stats,
        "objectives": objectives
    }
    
    return match_result

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda x: json.dumps(x).encode('utf-8')
)

# Main function to send match results to Kafka
def send_match_results(topic_name="match-results", num_matches=10, interval=5):
    """
    Send match result events to Kafka
    
    Parameters:
    - topic_name: Kafka topic to send events to
    - num_matches: Number of match results to generate and send
    - interval: Time interval between sends (in seconds)
    """
    print(f"Starting to send {num_matches} match results to topic '{topic_name}'...")
    
    for i in range(num_matches):
        match_result = generate_match_result()
        
        # Send the match result to Kafka
        producer.send(topic_name, value=match_result)
        
        print(f"Sent match result {i+1}/{num_matches}: Match ID {match_result['match_id']}, "
              f"Winner: {match_result['winner']}, Duration: {match_result['duration']//60} minutes")
        
        # Wait for the specified interval before sending the next event
        if i < num_matches - 1:
            time.sleep(interval)
    
    # Flush to ensure all messages are sent
    producer.flush()
    print("All match results sent successfully!")

if __name__ == "__main__":
    try:
        send_match_results(num_matches=20, interval=2)
    except KeyboardInterrupt:
        print("Producer interrupted by user")
    except Exception as e:
        print(f"Error in producer: {e}")
    finally:
        # Close the producer connection
        if producer:
            producer.close()
            print("Producer connection closed")
