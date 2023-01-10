import sportsdataverse as sdv


class NBA:
    def __init__(self):
        self.teams = sdv.nba.nba_teams.espn_nba_teams()
        self.team_id = 0

    def set_team_id(self, team_name):
        self.team_id = int(self.teams[self.teams["team_name"] == team_name]["team_id"])
        print("Object.team_id set to {}".format(self.team_id))

    def get_pbp(self, seasons, team_name=None):
        # error handle argument
        if min(seasons) < 2002:
            raise ValueError("Invalid season(s) entered. Season must be above 2002")

        # # pull requested team id
        # team_id = self.get_team_id(team_name) if team else 0

        # load play-by-play data // slice for specific team if requested
        pbp_data = sdv.nba.nba_loaders.load_nba_pbp(seasons=seasons)
        if self.team_id:
            pbp_data = pbp_data[(pbp_data["home_team_id"] == self.team_id) | (pbp_data["away_team_id"] == self.team_id)]
        
        # clean type_text column
        pbp_data["cleaned_type_text"] = pbp_data["type_text"]
        for i, row in pbp_data.iterrows():
            play_type = row["type_text"]
            if "Jump Shot" in play_type:
                play_type = "Jump Shot"
            elif "Layup" in play_type:
                play_type = "Layup"
            elif "Dunk" in play_type:
                play_type = "Dunk"
            elif "Hook" in play_type:
                play_type = "Hook Shot"
            elif "Free Throw" in play_type:
                play_type = "Free Throw"
            elif "Foul" in play_type:
                play_type = "Foul"
            elif "Turnover" in play_type:
                play_type = "Turnover"
            elif "Challenge" in play_type:
                play_type = "Challenge"
            elif "Jumpball" in play_type:
                play_type = "Jump Ball"

            pbp_data.loc[i, "cleaned_type_text"] = play_type

        # unique_texts = pbp_data.loc[:,"cleaned_type_text"].unique()
        # print(unique_texts)
        print(pbp_data.columns)
        return pbp_data

    def get_second_chance_points(self, pbp_data, team=None):
        # doesn't take into account fouls after offensive rebounds
        # UPDATE: There are some free throws taken into account after offensive rebounds
        #           Need to do more research on if all free throws after ORB are accounted for (and not have lag1 = foul instead of ORB)

        # create lag 1 column
        pbp_data["lag_1_text"] = pbp_data["cleaned_type_text"].shift(1)

        # calculate all second chance points
        pbp_data["is_second_chance_point"] = False
        for i, row in pbp_data.iterrows():
            if (row["lag_1_text"] == "Offensive Rebound") and (row["scoring_play"] == True):
                pbp_data.loc[i, "is_second_chance_point"] = True

        # filter pbp for specific team
        # pull requested team id
        # team_id = self.get_team_id(team_name) if team else 0

        team_pbp = pbp_data[pbp_data["team_id"] == str(self.team_id)]

        # get total second chance points per game for requested team
        second_chance_points_pbp = team_pbp[team_pbp["is_second_chance_point"] == True]
        second_chance_points_per_game = second_chance_points_pbp.groupby("game_id").sum(numeric_only=True)["score_value"]
        print(second_chance_points_per_game)
        

if __name__ == "__main__":
    nba = NBA()

    team = "Pacers"
    nba.set_team_id(team)
    pbp = nba.get_pbp(seasons=[2022])
    
    # get second chance points for specified team
    # nba.get_second_chance_points(pbp_data=pbp)


