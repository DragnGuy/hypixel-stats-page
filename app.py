from flask import Flask, render_template, request
import requests
import pandas as pd


app = Flask(__name__)

@app.route('/')
def index():
    render_template('stats.html')

def send_req(url):
    response = requests.get(url)
    data = response.json()
    return data

@app.route('/stats', methods=['GET', 'POST'])
def stats():
    if request.method == 'POST':
        player_name = request.form['player_name']

        url = f"https://api.mojang.com/users/profiles/minecraft/{player_name}?"
        identification = send_req(url)

        if identification and "id" in identification: 
            uuid = identification["id"]
        else:
            error_message = "Error: Player not found. Please try again."
            return render_template('stats.html', error_message=error_message)

        api_key = "fab4723a-fe4c-4fb6-afda-674f970b55b0"
        url = f"https://api.hypixel.net/v2/player?key={api_key}&uuid={uuid}"
        data = send_req(url)

        if data and "success" in data:
            # player name
            if "playername" in data["player"]:
                player_name = data["player"]["playername"]
            else:
                player_name = "ACTUAL ERROR"

            # display name
            if "displayname" in data["player"]:
                display_name = data["player"]["displayname"]
            else:
                display_name = "ACTUAL ERROR"

            # Check if "newPackageRank/prefix" key exists, set default if not
            if "prefix" in data["player"]:
                rank = data["player"]["prefix"]
            elif "newPackageRank" in data["player"]:
                rank = data["player"]["newPackageRank"]
            else:
                rank = "Default"

            # Count the number of one-time achievements
            onetimeachievements_count = len(data["player"]["achievementsOneTime"]) if "achievementsOneTime" in data["player"] else 0

            # Creating the table for stats
            player_stats = pd.DataFrame({
                "Info Type": ["Player Name", "Display Name", "Rank", "one time achievements"],
                "Info": [player_name, display_name, rank, onetimeachievements_count]
            })

            # get the players bedwars games played
            total_played_bedwars_games = data["player"]["stats"]["Bedwars"]["games_played_bedwars"] if "games_played_bedwars" in data["player"]["stats"]["Bedwars"] else 0
            # get  the playes deaths in bedwars
            total_bedwars_deaths = data["player"]["stats"]["Bedwars"]["deaths_bedwars"] if "deaths_bedwars" in data["player"]["stats"]["Bedwars"] else 0
            # get final deaths
            total_final_deaths = data["player"]["stats"]["Bedwars"]["final_deaths_bedwars"] if "final_deaths_bedwars" in data["player"]["stats"]["Bedwars"] else 0
            #get the total bedwars kills
            total_bedwars_kills = data["player"]["stats"]["Bedwars"]["kills_bedwars"] if "kills_bedwars" in data["player"]["stats"]["Bedwars"] else 0
            # get the total final kills
            total_bedwars_final_kills = data["player"]["stats"]["Bedwars"]["final_kills_bedwars"] if "final_kills_bedwars" in data["player"]["stats"]["Bedwars"] else 0
            #get the total bedwars wins
            total_bedwars_wins = data["player"]["achievements"]["bedwars_wins"] if "bedwars_wins" in data["player"]["achievements"] else 0
            #get the total losses
            total_bedwars_losses = data["player"]["stats"]["Bedwars"]["losses_bedwars"] if "losses_bedwars" in data["player"]["stats"]["Bedwars"] else 0

            # Create a table for bedwars outside the loop
            bedwars = pd.DataFrame({
                "Info Type": ["Total Bedwars Games Played", "Total  Bedwars Wins", "Total Bedwars Losses", "Total Deaths", "Total final deaths", "total kills", "Total final kills"],
                "Info": [total_played_bedwars_games, total_bedwars_wins, total_bedwars_losses, total_bedwars_deaths, total_final_deaths, total_bedwars_kills, total_bedwars_final_kills]
            })
           

            return render_template('result.html', player_stats=player_stats, bedwars=bedwars)
        else:
            error_message = "Error in API response. Debugging information:"
            return render_template('stats.html', error_message=error_message, debugging_info=data)

    return render_template('stats.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
