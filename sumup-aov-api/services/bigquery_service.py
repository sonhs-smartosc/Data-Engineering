from google.cloud import bigquery
import os
from datetime import datetime

class BigQueryService:
    def __init__(self):
        # Initialize BigQuery client
        self.client = bigquery.Client()
        self.project_id = os.environ.get('GCP_PROJECT_ID')
        self.dataset_id = os.environ.get('BQ_DATASET_ID')
    
    def _format_timestamp(self, timestamp):
        """Format BigQuery TIMESTAMP to ISO string"""
        if timestamp:
            if isinstance(timestamp, datetime):
                return timestamp.isoformat()
            return timestamp
        return None
    
    def get_matches(self, limit=10, offset=0):
        """Get a list of matches with pagination"""
        query = f"""
        SELECT id, start_time, end_time, duration_seconds
        FROM `{self.project_id}.{self.dataset_id}.matches`
        ORDER BY start_time DESC
        LIMIT {limit}
        OFFSET {offset}
        """
        
        query_job = self.client.query(query)
        results = query_job.result()
        
        matches = []
        for row in results:
            matches.append({
                'id': row.id,
                'start_time': self._format_timestamp(row.start_time),
                'end_time': self._format_timestamp(row.end_time),
                'duration_seconds': row.duration_seconds
            })
            
        return matches
    
    def get_match_by_id(self, match_id):
        """Get a single match by ID"""
        query = f"""
        SELECT id, start_time, end_time, duration_seconds
        FROM `{self.project_id}.{self.dataset_id}.matches`
        WHERE id = @match_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("match_id", "STRING", match_id)
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        
        for row in results:
            return {
                'id': row.id,
                'start_time': self._format_timestamp(row.start_time),
                'end_time': self._format_timestamp(row.end_time),
                'duration_seconds': row.duration_seconds
            }
        
        return None
    
    def get_players_by_match_id(self, match_id):
        """Get all players in a match"""
        query = f"""
        SELECT id, match_id, team_id, champion, kills, deaths, assists,
               total_damage_dealt, total_damage_taken, gold_earned, win
        FROM `{self.project_id}.{self.dataset_id}.players`
        WHERE match_id = @match_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("match_id", "STRING", match_id)
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        
        players = []
        for row in results:
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
            
        return players
    
    def get_teams_by_match_id(self, match_id):
        """Get team data for a match"""
        query = f"""
        SELECT id, match_id, team_id, win, dragons, barons,
               towers, total_kills, total_gold
        FROM `{self.project_id}.{self.dataset_id}.teams`
        WHERE match_id = @match_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("match_id", "STRING", match_id)
            ]
        )
        
        query_job = self.client.query(query, job_config=job_config)
        results = query_job.result()
        
        teams = []
        for row in results:
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
            
        return teams
    
    def get_champion_stats(self):
        """Get statistics about champions"""
        query = f"""
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
        FROM `{self.project_id}.{self.dataset_id}.players`
        GROUP BY champion
        ORDER BY games_played DESC
        """
        
        query_job = self.client.query(query)
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
    
    def get_top_players(self, limit=10):
        """Get top players by KDA ratio"""
        query = f"""
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
            FROM `{self.project_id}.{self.dataset_id}.players`
        ) as player_stats
        GROUP BY champion
        ORDER BY avg_kda DESC
        LIMIT {limit}
        """
        
        query_job = self.client.query(query)
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
