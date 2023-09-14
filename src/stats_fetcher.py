import requests

class StatsFetcher:
    def __init__(self):
        self.modes = ["eight_one", "eight_two", "four_three", "four_four"]
    
    def update_api_key(self, api_key):
        print(f"Updating API key to {api_key}")
        self.api_key = api_key
        
    def fetch_player_uuid(self, player_name):
        api_url = f"https://api.mojang.com/users/profiles/minecraft/{player_name}"

        response = requests.get(api_url)
        
        if response.status_code == 200:
            return response.json()["id"]
        print(f"Error fetching UUID for {player_name}: {response.status_code}")
        return None

    def make_request(self, player_name):
        print(f"Fetching stats for {player_name}")
        player_uuid = self.fetch_player_uuid(player_name)
        
        if not player_uuid:
            print(f"UUID not found for {player_name}")
            return None

        api_url = f"https://api.hypixel.net/player?key={self.api_key}&uuid={player_uuid}"
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            if data["success"]:
                return data["player"]["stats"].get("Bedwars", None)
        
        # Handle 404 status code specifically
        if response.status_code == 404:
            print(f"Error 404: Making all stats '?' for {player_name}")
            return {'AllStats': '?'}

        print(f"Failed to fetch Bedwars stats for {player_name}")
        return None

    def fetch_final_kills(self, stats):
        if stats.get('AllStats') == '?':
            return '?'
        return sum(int(stats.get(f"{mode}_final_kills_bedwars", 0)) for mode in self.modes)

    def fetch_final_deaths(self, stats):
        if stats.get('AllStats') == '?':
            return '?'
        return sum(int(stats.get(f"{mode}_final_deaths_bedwars", 0)) for mode in self.modes)

    def fetch_wins(self, stats):
        if stats.get('AllStats') == '?':
            return '?'
        return sum(int(stats.get(f"{mode}_wins_bedwars", 0)) for mode in self.modes)

    def fetch_losses(self, stats):
        if stats.get('AllStats') == '?':
            return '?'
        return sum(int(stats.get(f"{mode}_losses_bedwars", 0)) for mode in self.modes)

    def fetch_beds_broken(self, stats):
        if stats.get('AllStats') == '?':
            return '?'
        return sum(int(stats.get(f"{mode}_beds_broken_bedwars", 0)) for mode in self.modes)

    def get_stats(self, player_name):
        bedwars_stats = self.make_request(player_name)

        if bedwars_stats:
            fk = self.fetch_final_kills(bedwars_stats)
            fd = self.fetch_final_deaths(bedwars_stats)
            fkdr = '?' if fk == '?' or fd == '?' else (round(fk / fd, 2) if fd else 0)

            wins = self.fetch_wins(bedwars_stats)
            losses = self.fetch_losses(bedwars_stats)
            wlr = '?' if wins == '?' or losses == '?' else (round(wins / losses, 2) if losses else 0)

            beds = self.fetch_beds_broken(bedwars_stats)

            return [player_name, f"{fk:,}" if fk != '?' else '?', f"{fd:,}" if fd != '?' else '?', fkdr, f"{wins:,}" if wins != '?' else '?', wlr, f"{beds:,}" if beds != '?' else '?']
