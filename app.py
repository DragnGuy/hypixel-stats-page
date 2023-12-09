from flask import Flask, render_template, request
import sys
import requests
import pandas as pd
from tabulate import tabulate

app = Flask(__name__)

def send_req(url):
    print("Sending request...")
    response = requests.get(url)
    print("Response:")
    data = response.json()
    return data

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        player_name = request.form['player_name']

        url = f"https://api.mojang.com/users/profiles/minecraft/{player_name}?"
        identification = send_req(url)

        if identification and "id" in identification: 
            uuid = identification["id"]
        else:
            error_message = "Error: Player not found. Please try again."
            return render_template('stats.html', error_message=error_message)

        api_key = "9e175ec6-8963-4e69-8175-98d30548ebac"
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

            # Create a table for bedwars outside the loop
            bedwars = pd.DataFrame({
                "Info Type": ["Total Bedwars Games Played", "Total Deaths", "Total final deaths", "total kills", "Total final kills"],
                "Info": [total_played_bedwars_games, total_bedwars_deaths, total_final_deaths, total_bedwars_kills, total_bedwars_final_kills]
            })

            # Display the table stats outside the loop
            print("\nPlayer Stats:")
            print(tabulate(player_stats, headers="keys", tablefmt="fancy_grid", showindex=False))

            print("\nBedwars Stats:")
            print(tabulate(bedwars, headers="keys", tablefmt="fancy_grid", showindex=False))

            return render_template('result.html', player_stats=player_stats, bedwars=bedwars)
        else:
            error_message = "Error in API response. Debugging information:"
            return render_template('stats.html', error_message=error_message, debugging_info=data)

    return render_template('stats.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
