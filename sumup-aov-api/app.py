from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.oauth2 import service_account
from datetime import datetime
from flask_restx import Api, Resource, fields, Namespace

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Create credentials and BigQuery client
credentials = service_account.Credentials.from_service_account_file(
    "credentials/service-account.json",
    scopes=["https://www.googleapis.com/auth/cloud-platform"],
)
bq_client = bigquery.Client(
    credentials=credentials,
    project=credentials.project_id,
)

# Initialize Flask-RESTX
api = Api(app,
    version='1.0',
    title='AOV Match Data API',
    description='API for retrieving AOV (Arena of Valor) match data',
    doc='/swagger'
)

# Create namespaces
ns_matches = api.namespace('api/matches', description='Match operations')
ns_champions = api.namespace('api/champions', description='Champion statistics')
ns_players = api.namespace('api/players', description='Player statistics')

# Define models for Swagger documentation
match_model = api.model('Match', {
    'id': fields.String(description='Match ID'),
    'start_time': fields.String(description='Match start time'),
    'end_time': fields.String(description='Match end time'),
    'duration_seconds': fields.Integer(description='Match duration in seconds')
})

player_model = api.model('Player', {
    'id': fields.String(description='Player ID'),
    'match_id': fields.String(description='Match ID'),
    'team_id': fields.Integer(description='Team ID'),
    'champion': fields.String(description='Champion name'),
    'kills': fields.Integer(description='Kills'),
    'deaths': fields.Integer(description='Deaths'),
    'assists': fields.Integer(description='Assists'),
    'total_damage_dealt': fields.Integer(description='Total damage dealt'),
    'total_damage_taken': fields.Integer(description='Total damage taken'),
    'gold_earned': fields.Integer(description='Gold earned'),
    'win': fields.Boolean(description='Whether the player won')
})

team_model = api.model('Team', {
    'id': fields.String(description='Team ID'),
    'match_id': fields.String(description='Match ID'),
    'team_id': fields.Integer(description='Team ID'),
    'win': fields.Boolean(description='Whether the team won'),
    'dragons': fields.Integer(description='Dragons killed'),
    'barons': fields.Integer(description='Barons killed'),
    'towers': fields.Integer(description='Towers destroyed'),
    'total_kills': fields.Integer(description='Total kills'),
    'total_gold': fields.Integer(description='Total gold earned')
})

match_details_model = api.model('MatchDetails', {
    'match': fields.Nested(match_model),
    'teams': fields.List(fields.Nested(team_model)),
    'players': fields.List(fields.Nested(player_model))
})

champion_stats_model = api.model('ChampionStats', {
    'champion': fields.String(description='Champion name'),
    'games_played': fields.Integer(description='Number of games played'),
    'wins': fields.Integer(description='Number of wins'),
    'win_rate': fields.Float(description='Win rate percentage'),
    'avg_kills': fields.Float(description='Average kills'),
    'avg_deaths': fields.Float(description='Average deaths'),
    'avg_assists': fields.Float(description='Average assists'),
    'avg_kda': fields.Float(description='Average KDA ratio'),
    'avg_damage_dealt': fields.Float(description='Average damage dealt'),
    'avg_damage_taken': fields.Float(description='Average damage taken'),
    'avg_gold': fields.Float(description='Average gold earned')
})

top_player_model = api.model('TopPlayer', {
    'champion': fields.String(description='Champion name'),
    'avg_kda': fields.Float(description='Average KDA ratio'),
    'games_played': fields.Integer(description='Number of games played'),
    'avg_kills': fields.Float(description='Average kills'),
    'avg_deaths': fields.Float(description='Average deaths'),
    'avg_assists': fields.Float(description='Average assists'),
    'win_rate': fields.Float(description='Win rate percentage')
})

def _format_timestamp(timestamp):
    """Format BigQuery TIMESTAMP to ISO string"""
    if timestamp:
        if isinstance(timestamp, datetime):
            return timestamp.isoformat()
        return timestamp
    return None

# RESTX Resources
@ns_matches.route('')
class MatchList(Resource):
    @ns_matches.doc('list_matches', params={
        'limit': {'description': 'Maximum number of matches to return', 'type': 'integer', 'default': 10},
        'offset': {'description': 'Number of matches to skip', 'type': 'integer', 'default': 0}
    })
    @ns_matches.marshal_list_with(match_model)
    def get(self):
        """Get a list of matches with optional filtering"""
        limit = request.args.get('limit', 10, type=int)
        offset = request.args.get('offset', 0, type=int)

        query = """
        SELECT id, start_time, end_time, duration_seconds
        FROM `matches`
        ORDER BY start_time DESC
        LIMIT @limit
        OFFSET @offset
        """

        query_params = [
            bigquery.ScalarQueryParameter("limit", "INTEGER", limit),
            bigquery.ScalarQueryParameter("offset", "INTEGER", offset)
        ]

        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = bq_client.query(query, job_config=job_config)
        results = query_job.result()

        matches = []
        for row in results:
            matches.append({
                'id': row.id,
                'start_time': _format_timestamp(row.start_time),
                'end_time': _format_timestamp(row.end_time),
                'duration_seconds': row.duration_seconds
            })

        return matches

@ns_matches.route('/<string:match_id>')
@ns_matches.param('match_id', 'The match identifier')
class MatchDetail(Resource):
    @ns_matches.doc('get_match')
    @ns_matches.marshal_with(match_details_model)
    @ns_matches.response(404, 'Match not found')
    def get(self, match_id):
        """Get detailed information about a specific match"""
        # Get match data
        match_query = """
        SELECT id, start_time, end_time, duration_seconds
        FROM `matches`
        WHERE id = @match_id
        """

        match_params = [bigquery.ScalarQueryParameter("match_id", "STRING", match_id)]
        match_config = bigquery.QueryJobConfig(query_parameters=match_params)
        match_job = bq_client.query(match_query, job_config=match_config)
        match_results = match_job.result()

        match_data = None
        for row in match_results:
            match_data = {
                'id': row.id,
                'start_time': _format_timestamp(row.start_time),
                'end_time': _format_timestamp(row.end_time),
                'duration_seconds': row.duration_seconds
            }

        if not match_data:
            api.abort(404, f"Match {match_id} not found")

        # Get players data
        players_query = """
        SELECT id, match_id, team_id, champion, kills, deaths, assists,
               total_damage_dealt, total_damage_taken, gold_earned, win
        FROM `players`
        WHERE match_id = @match_id
        """

        players_params = [bigquery.ScalarQueryParameter("match_id", "STRING", match_id)]
        players_config = bigquery.QueryJobConfig(query_parameters=players_params)
        players_job = bq_client.query(players_query, job_config=players_config)
        players_results = players_job.result()

        players = []
        for row in players_results:
            players.append({
                'id': row.id,
                'match_id': row.match_id,
                'team_id': row.team_id,
                'champion': row.champion,
                'kills': row.kills,
                'deaths': row.deaths,
                'assists': row.assists,
                'total_damage_dealt': row.total_damage_dealt,
                'total_damage_taken': row.total_damage_taken,
                'gold_earned': row.gold_earned,
                'win': row.win
            })

        # Get teams data
        teams_query = """
        SELECT id, match_id, team_id, win, dragons, barons,
               towers, total_kills, total_gold
        FROM `teams`
        WHERE match_id = @match_id
        """

        teams_params = [bigquery.ScalarQueryParameter("match_id", "STRING", match_id)]
        teams_config = bigquery.QueryJobConfig(query_parameters=teams_params)
        teams_job = bq_client.query(teams_query, job_config=teams_config)
        teams_results = teams_job.result()

        teams = []
        for row in teams_results:
            teams.append({
                'id': row.id,
                'match_id': row.match_id,
                'team_id': row.team_id,
                'win': row.win,
                'dragons': row.dragons,
                'barons': row.barons,
                'towers': row.towers,
                'total_kills': row.total_kills,
                'total_gold': row.total_gold
            })

        # Combine all data
        result = {
            "match": match_data,
            "teams": teams,
            "players": players
        }

        return result

@ns_champions.route('')
class ChampionStats(Resource):
    @ns_champions.doc('get_champion_stats')
    @ns_champions.marshal_list_with(champion_stats_model)
    def get(self):
        """Get statistics about champions"""
        query = """
        SELECT 
            champion,
            COUNT(*) as games_played,
            SUM(CASE WHEN win THEN 1 ELSE 0 END) as wins,
            AVG(kills) as avg_kills,
            AVG(deaths) as avg_deaths,
            AVG(assists) as avg_assists,
            AVG(CASE WHEN deaths > 0 THEN (kills + assists) / deaths ELSE kills + assists END) as avg_kda,
            AVG(total_damage_dealt) as avg_damage_dealt,
            AVG(total_damage_taken) as avg_damage_taken,
            AVG(gold_earned) as avg_gold
        FROM `players`
        GROUP BY champion
        ORDER BY games_played DESC
        """

        query_job = bq_client.query(query)
        results = query_job.result()

        stats = []
        for row in results:
            win_rate = (row.wins / row.games_played) * 100 if row.games_played > 0 else 0

            stats.append({
                'champion': row.champion,
                'games_played': row.games_played,
                'wins': row.wins,
                'win_rate': round(win_rate, 2),
                'avg_kills': round(row.avg_kills, 2),
                'avg_deaths': round(row.avg_deaths, 2),
                'avg_assists': round(row.avg_assists, 2),
                'avg_kda': round(row.avg_kda, 2),
                'avg_damage_dealt': round(row.avg_damage_dealt, 2),
                'avg_damage_taken': round(row.avg_damage_taken, 2),
                'avg_gold': round(row.avg_gold, 2)
            })

        return stats

@ns_players.route('/top')
class TopPlayers(Resource):
    @ns_players.doc('get_top_players', params={
        'limit': {'description': 'Maximum number of players to return', 'type': 'integer', 'default': 10}
    })
    @ns_players.marshal_list_with(top_player_model)
    def get(self):
        """Get top players by KDA"""
        limit = request.args.get('limit', 10, type=int)

        query = """
        SELECT 
            player_stats.champion,
            AVG(player_stats.kda) as avg_kda,
            COUNT(*) as games_played,
            AVG(player_stats.kills) as avg_kills,
            AVG(player_stats.deaths) as avg_deaths,
            AVG(player_stats.assists) as avg_assists,
            SUM(CASE WHEN player_stats.win THEN 1 ELSE 0 END) / COUNT(*) * 100 as win_rate
        FROM (
            SELECT 
                champion,
                kills,
                deaths,
                assists,
                win,
                CASE WHEN deaths > 0 THEN (kills + assists) / deaths ELSE kills + assists END as kda
            FROM `players`
        ) as player_stats
        GROUP BY champion
        ORDER BY avg_kda DESC
        LIMIT @limit
        """

        query_params = [bigquery.ScalarQueryParameter("limit", "INTEGER", limit)]
        job_config = bigquery.QueryJobConfig(query_parameters=query_params)
        query_job = bq_client.query(query, job_config=job_config)
        results = query_job.result()

        top_players = []
        for row in results:
            top_players.append({
                'champion': row.champion,
                'avg_kda': round(row.avg_kda, 2),
                'games_played': row.games_played,
                'avg_kills': round(row.avg_kills, 2),
                'avg_deaths': round(row.avg_deaths, 2),
                'avg_assists': round(row.avg_assists, 2),
                'win_rate': round(row.win_rate, 2)
            })

        return top_players

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)
