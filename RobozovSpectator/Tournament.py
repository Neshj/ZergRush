# !/usr/bin/python
# -*- coding: utf-8 -*-

#   Amir Krayden
#   18/04/15
#

from random import randint

class TournamentUtility:
    
    def __init__(self):
        print ("Tournament init")
        
    def GenerateTournament(self,config_data):
        # Build a tuple for each team
        teams = list(config_data['Teams'])

        match_list = []

        # Find all Matches

        while (len(teams) > 1):
            # Get a random current team
            current_team = teams.pop(randint(0,len(teams)-1)) 
            
            remaining_teams = list(teams)
            
            while (len(remaining_teams) > 0):
                opp_team = remaining_teams.pop(randint(0,len(remaining_teams)-1))
                match_tup = (current_team['id'], current_team['name'],opp_team['id'], opp_team['name'], '0')
                match_list.append(match_tup)
        
        # Permute the games
        perm_match_list = []
        
        while (len(match_list) > 0):
            perm_match_list.append(match_list.pop(randint(0,len(match_list)-1)))
            
        return (perm_match_list)

