# AOV Match Data API

A Flask-based API for retrieving AOV (Arena of Valor) match data from Google BigQuery.

## Setup

1. Clone this repository
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up environment variables:
   ```
   cp .env.example .env
   ```
   Edit `.env` to include your Google Cloud project details.

5. Set up Google Cloud authentication:
   - Create a service account with access to BigQuery
   - Download the service account key JSON file
   - Set the path in `.env` as `GOOGLE_APPLICATION_CREDENTIALS`
   - Or set the environment variable directly:
     ```
     export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-project-credentials.json"
     ```

## Running the API

For development:
```
python app.py
```

For production:
```
gunicorn app:app
```

## API Endpoints

### Get Matches

```
GET /api/matches?limit=10&offset=0
```

Retrieves a list of matches with pagination.

### Get Match Details

```
GET /api/matches/{match_id}
```

Retrieves detailed information about a specific match, including team and player data.

### Get Champion Statistics

```
GET /api/champions
```

Retrieves aggregated statistics about champions across all matches.

### Get Top Players

```
GET /api/players/top?limit=10
```

Retrieves the top players based on KDA ratio.

## Data Schema

The API uses the following BigQuery tables:

### matches
- `id` (STRING): Unique match ID
- `start_time` (TIMESTAMP): Match start time
- `end_time` (TIMESTAMP): Match end time
- `duration_seconds` (INTEGER): Match duration in seconds

### players
- `id` (STRING): Unique player record ID
- `match_id` (STRING): ID of the match this player participated in
- `team_id` (INTEGER): Team ID (1 or 2)
- `champion` (STRING): Champion name
- `kills` (INTEGER): Number of kills
- `deaths` (INTEGER): Number of deaths
- `assists` (INTEGER): Number of assists
- `total_damage_dealt` (INTEGER): Total damage dealt
- `total_damage_taken` (INTEGER): Total damage taken
- `gold_earned` (INTEGER): Gold earned
- `win` (BOOLEAN): Whether this player won the match

### teams
- `id` (STRING): Unique team record ID
- `match_id` (STRING): ID of the match this team participated in
- `team_id` (INTEGER): Team identifier (1 or 2)
- `win` (BOOLEAN): Whether this team won the match
- `dragons` (INTEGER): Number of dragons killed by the team
- `barons` (INTEGER): Number of barons killed by the team
- `towers` (INTEGER): Number of towers destroyed by the team
- `total_kills` (INTEGER): Total kills by the team
- `total_gold` (INTEGER): Total gold earned by the team
