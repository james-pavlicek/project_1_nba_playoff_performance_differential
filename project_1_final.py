### This code will:
#1. Make a dataframe of league average true shooting percentage for the regular season and playoffs 
#2. Make a dataframe of NBA players who have played over 2000 playoff minutes and were drafted 1979 or after
#3. Make a dataframe for each individual player's regular season data with PER and ts%
#4. Make a dataframe for each individual player's playoff data with PER and ts% (Adjust data to control for playoff difficulty and injuries)
#5. Combine regular season and playoff data 
#6. Clean Data and calculate the traditional and adjusted PER differential: sum, average and % change (+ is a playoff riser, - is a playoff faller) 
#7. Export dataframes for Analysis 

# Notes: (RS = Regular Season)(P = Playoffs)(DF = Dataframe)(TS% = True Shooting Percentage)(PER = Player Efficiency Rating)




#----------------------Import Packages----------------------#

import pandas as pd
import requests
from pandas import DataFrame
from nba_api.stats.endpoints.drafthistory import DraftHistory
import time
from bs4 import BeautifulSoup as Soup




#-----------------------------------------------------------#
#-------STEP 1: RS & Playoff League Average TS% DF ---------#
#-----------------------------------------------------------#



#--------------------Regular Season TS%---------------------#

#Navigate to website
response = requests.get('https://www.basketball-reference.com/leagues/NBA_stats_totals.html')

#Get raw html data 
nba_ts_soup = Soup(response.text,features="html.parser")

#Find all the tables in html text
tables = nba_ts_soup.find_all('table')

#Find the number of tables 
print(len(tables))

#Grab the first table
nba_ts_table = tables[0]

#Set the rows as the values in the table that start with 'tr'
rows = nba_ts_table.find_all('tr')

#Confirm the rows are the same rows as the website
#print(rows)

#Find the first row of data
first_data_row = rows[2]

#Find all data in the row tagged with 'td'
first_data_row.find_all('td')

#Call a string function to get the data out
[str(x.string) for x in first_data_row.find_all('td')]

#Create a function that will work on all rows 
def parse_row(row):
    return [str(x.string) for x in row.find_all('td')]

#Apply the function to each row of data
list_of_parsed_rows = [parse_row(row) for row in rows[1:]]

#Create a dataframe from the list
df = DataFrame(list_of_parsed_rows)

#User the header row as the column headers in the dataframe
df_columns = [str(x.string).lower() for x in rows[1].find_all('th')]

#Remove the 'rk' row (Solves dataframe shape issue)
df_columns.remove('rk')

#set the columns in df as df_columns
df.columns = df_columns

#Drop all blank rows
df= df.dropna(subset=['lg'])

#Drops seasons that were before the 1979-80 season 
df = df[df['season'] >= '1979-80']

#Sets 'pts', 'fga', 'fta' as float type for ts% calculation
rs_tspercent_df = df[['pts', 'fga', 'fta']].astype(float) 

#TS% calculation
rs_tspercent_df['league_avg_rs_ts%'] = rs_tspercent_df['pts'] / (2 * (rs_tspercent_df['fga'] + (0.44 * rs_tspercent_df['fta'])))

#Copy the 'season' column in the df dataframe 
rs_tspercent_df['season'] = df['season']

#Drop 'pts', 'fga', 'fta' columns 
rs_tspercent_df = rs_tspercent_df.drop(['pts', 'fga', 'fta'],axis=1)

#The dataframe now only has 'season','league_avg_rs_ts%' columns
rs_tspercent_df = rs_tspercent_df[['season','league_avg_rs_ts%']]

#Coverts the season from "XXXX-XX" to "XXXX"
rs_tspercent_df['season'] = rs_tspercent_df['season'].str[:2] + rs_tspercent_df['season'].str[5:]
rs_tspercent_df.at[26,'season'] = 2000

#Set the 'season' column to integer type 
rs_tspercent_df['season'] = rs_tspercent_df['season'].astype(int)



#---------------PLAYOFF TS% Years 1980-1983-----------------#

#start a blank dictionary
output_dict = {}

#Assign the desired years to the start and end values 
start = 1980
end = 2023

#For loop that will run when the year in the url is 1980-1983
for year in range(start,end+1):
    
    #10 second delay between requests
    time.sleep(10)

    #Navigate to website
    response = requests.get(f'https://www.basketball-reference.com/playoffs/NBA_{year}.html')

    #Get raw html data 
    nba_soup = Soup(response.text,features="html.parser")

    #Find all the tables in html text
    tables = nba_soup.find_all('table')

    #Find the number of tables 
    print(len(tables))

    #If the year is 1980-83 return 16, if the year is 1984-2023 return 20
    if year <= 1983:
        x = 16
    else:
        x = 20

    #Grab the 17th table or 21st table
    p_ts_table = tables[x]

    #Set the rows as the values in the table that start with 'tr'
    rows = p_ts_table.find_all('tr')

    #Find the first row of data
    first_data_row = rows[2]

    #Find all data in the row tagged with 'td'
    first_data_row.find_all('td')

    #Call a string function to get the data out
    [str(x.string) for x in first_data_row.find_all('td')]

    #Apply the function to each row of data
    def parse_row(row):
        return [str(x.string) for x in row.find_all('td')]

    #Apply the function to each row of data
    list_of_parsed_rows = [parse_row(row) for row in rows[1:]]

    #Create a dataframe from the list
    df = DataFrame(list_of_parsed_rows)

    #User the header row as the column headers in the dataframe
    df_columns = [str(x.string).lower() for x in rows[1].find_all('th')]

    #Remove the 'rk' row (Solves dataframe shape issue)
    df_columns.remove('rk')

    #set the columns in df as df_columns
    df.columns = df_columns

    #Drop all blank rows
    df= df.dropna(subset=['w'])

    #If there is 'tm' in the dataframe, replace it with 'team'
    if 'tm'in df:
        df.rename(columns={'tm':'team'},inplace=True) 

    #Set the index to 'team'
    df = df.set_index('team')

    #Print the TS% to confirm program is running correctly
    print(df.loc['League Average']['ts%'])

    #Assign the line to the output_dictionary
    output_dict[year] = (df.loc['League Average']['ts%'])


#Create a dataframe from the output_dict   
playoff_tspercent_df = pd.DataFrame.from_dict(output_dict, orient='index')

#Reset the index of the dataframe
playoff_tspercent_df = playoff_tspercent_df.reset_index()

#Set the columns as 'season' and 'ts%'
playoff_tspercent_df.columns = ['season', 'ts%']

#Set the index as a range of numbers equal to the length of the dataframe
playoff_tspercent_df['index'] = range(len(playoff_tspercent_df))

#Set the index as the column titled 'index'
playoff_tspercent_df.set_index('index', inplace=True)

#Set TS% as float type
playoff_tspercent_df['ts%'] = playoff_tspercent_df['ts%'].astype(float) 

#Rename the 'ts%' column as 'league_avg_playoff_ts%'
playoff_tspercent_df.rename(columns={'ts%':'league_avg_playoff_ts%'},inplace=True)

#Merge the regular season and playoff ts% dataframes on the season column 
League_average_ts_RS_and_Playoffs = pd.merge(rs_tspercent_df,playoff_tspercent_df, on= 'season')

#Calculate the playoff 'difficulty factor' by finding the percent change in scoring efficiency from the regular season to the playoffs
League_average_ts_RS_and_Playoffs['difficulty factor'] = ((League_average_ts_RS_and_Playoffs['league_avg_rs_ts%'] - League_average_ts_RS_and_Playoffs['league_avg_playoff_ts%']) / League_average_ts_RS_and_Playoffs['league_avg_rs_ts%'] + 1).round(5)





#-----------------------------------------------------------#
#-----STEP 2: Player DF (>2000 MIN & 1979+ Draft Year)------#
#-----------------------------------------------------------#



#----------FIND PLAYERS WITH 2000+ PLAYOFF MINUTES----------#

#Navigate to website and grab the .json
nba_playoff_min_leader_request = requests.get(url='https://stats.nba.com/stats/leagueLeaders?ActiveFlag=No&LeagueID=00&PerMode=Totals&Scope=S&Season=All%20Time&SeasonType=Playoffs&StatCategory=MIN').json()

#Check if data is a Dictionary
is_it_a_dict = type(nba_playoff_min_leader_request)
print(F'Data Check Results: {is_it_a_dict}')

#Sort the content for Headers
column_titles =  nba_playoff_min_leader_request["resultSet"]["headers"]

#Check if column_titles are correct
print(f'Column Titles: {column_titles}')

#Build a Pandas Dataframe
nba_playoff_min_leader_df = pd.DataFrame(nba_playoff_min_leader_request["resultSet"]['rowSet'],columns=column_titles)

#Only select the players who have played more than 2000 playoff minutes
nba_playoff_min_leader_df_over_2000_min = nba_playoff_min_leader_df.loc[nba_playoff_min_leader_df['MIN'] >= 2000]

#Start a new dataframe with only the PLAYER_ID, PLAYER_NAME and MIN columns
nba_playoff_min_leader_df_over_2000_min_trimmed = nba_playoff_min_leader_df_over_2000_min[['PLAYER_ID','PLAYER_NAME','MIN']]

#Print the dataframe to confirm all changes 
print(nba_playoff_min_leader_df_over_2000_min_trimmed.head())



#----------FIND PLAYERS DRAFTED AFTER 1973----------#

#Use the DraftHistory Endpoint from nba_api (https://github.com/swar/nba_api)
draft_data = DraftHistory()

#Get a dataframe of the data
draft_df = draft_data.get_data_frames()[0]

#Change the SEASON column to a integer
draft_df['SEASON'] = draft_df['SEASON'].astype('int')

#Only select the players who were drafted after 1973
player_dict_drafted_after_1979 = draft_df.loc[draft_df['SEASON'] >= 1979]

#Start a new dataframe with only the PERSON_ID, PLAYER_NAME and SEASON columns
player_dict_drafted_after_1979_trimmed = player_dict_drafted_after_1979[['PERSON_ID','PLAYER_NAME','SEASON']]

#Rename the PERSON_ID to PLAYER_ID so the dataframes can merge
player_dict_drafted_after_1979_trimmed.rename(columns={'PERSON_ID' : 'PLAYER_ID'}, inplace=True)

#Print the dataframe to confirm all changes 
print(player_dict_drafted_after_1979_trimmed.head())



#----------MERGE THE DATA TO FIND OUR PLAYERSET----------#
playerset = pd.merge(nba_playoff_min_leader_df_over_2000_min_trimmed,player_dict_drafted_after_1979_trimmed, on=['PLAYER_ID'])

#Confirm PLAYER_NAME_x and PLAYER_NAME_y match 
name_check = playerset['PLAYER_NAME_x'].equals(playerset['PLAYER_NAME_y'])
print(f'Name Check Results: {name_check}')

#Remove the redundant column  
playerset.drop('PLAYER_NAME_y', axis=1, inplace=True)

#Confirm that there are 217 players and 4 columns (as of July 6 2023)
print(f'The Shape of the playerset data is: {playerset.shape}')

 


#-----------------------------------------------------------#
#-------STEP 3: Player's RS data (with PER and ts%)---------#
#-----------------------------------------------------------#


#Run 217 times for the 217 players in the playerset
start = 0
end = 216

#Given the index number we are on, do the following: 
for player_index in range(start,end+1):
   
    #Import nba_api for career stats  
    from nba_api.stats.endpoints.playercareerstats import PlayerCareerStats

    time.sleep(1)
    
    #Lookup the Player_ID in playerset based on the index 
    player_id = playerset.at[player_index,'PLAYER_ID']

    #Get Regular Season data for the given Player_ID
    pbp_data = PlayerCareerStats(player_id=player_id, timeout=3)  
    
    #Convert the data into a dataframe
    pbp_df = pbp_data.get_data_frames()[0]

    x = pbp_df

    ### PER FORMULA: https://bleacherreport.com/articles/113144-cracking-the-code-how-to-calculate-hollingers-per-without-all-the-mess

    #For the Given Player_ID calculate the Regular Season PER
    x['PER'] =  ((x['FGM'] * 85.910)
                + (x['STL'] * 53.897)
                + (x['FG3M'] * 51.757)
                + (x['FTM']* 46.845)
                + (x['BLK'] * 39.190)
                + (x['OREB'] * 39.190)
                + (x['AST'] * 34.677)
                + (x['DREB'] * 14.707)
                + (x['PF'] * -17.174)
                + ((x['FTA'] - x['FTM']) *-20.091)
                + ((x['FGA'] - x['FGM']) * -39.190)
                + (x['TOV'] *-53.897)) / x['MIN']
               
    #Confirm PER and player_ID output
    print((x['PER']).head(1))

    #Calculate Player TS%
    x['TS%'] = x['PTS'] / (2 * (x['FGA'] + (0.44 * x['FTA'])))
    
    #Give all Regular Season Data a prefix of 'RS_'
    prefix = 'RS_'
    new_columns = {col: f"{prefix}{col}" for col in x.columns}
    x = x.rename(columns=new_columns)
    
    #Create a column titled 'season' so we can merge the data later
    x['season'] = x['RS_SEASON_ID'].str[:2] + x['RS_SEASON_ID'].str[5:]
    x['season'] = x['season'].astype(int)
    x.loc[x['season'] == 1900, 'season'] = 2000

    #Give the dataframe a prefix and the player_id so we can use the regular season data later
    exec(F"RS_data_{player_id} = x")
    
    


    #-----------------------------------------------------------#
    #----STEP 4: Player's Playoff data (with PER and ts%)-------#
    #-----------------------------------------------------------#
    

    time.sleep(1)

    #Lookup the Player_ID in playerset based on the index 
    player_id = playerset.at[player_index,'PLAYER_ID']

    #Get career stats for the given Player_ID
    playoff_pbp_df = PlayerCareerStats(player_id=player_id, timeout=3)  

    #Specify that we want Playoff data and covert the data into dataframe
    playoff_pbp_df = playoff_pbp_df.season_totals_post_season.get_data_frame()

    y = playoff_pbp_df

    #For the Given Player_ID calculate the Playoff PER
    y['PER'] =  ((y['FGM'] * 85.910)
                + (y['STL'] * 53.897)
                + (y['FG3M'] * 51.757)
                + (y['FTM']* 46.845)
                + (y['BLK'] * 39.190)
                + (y['OREB'] * 39.190)
                + (y['AST'] * 34.677)
                + (y['DREB'] * 14.707)
                + (y['PF'] * -17.174)
                + ((y['FTA'] - y['FTM']) *-20.091)
                + ((y['FGA'] - y['FGM']) * -39.190)
                + (y['TOV'] *-53.897)) / y['MIN']
               
    #Confirm PER and player_ID output
    print((y['PER']).head(1))

    #Calculate Player TS%
    y['TS%'] = y['PTS'] / (2 * (y['FGA'] + (0.44 * y['FTA'])))

    #Give all Regular Season Data a prefix of 'P_'
    prefix = 'P_'
    new_columns = {col: f"{prefix}{col}" for col in y.columns}
    y = y.rename(columns=new_columns)
    
    
    #Create a column titled 'season' so we can merge the data later
    y['season'] = y['P_SEASON_ID'].str[:2] + y['P_SEASON_ID'].str[5:]
    y['season'] = y['season'].astype(int)
    y.loc[y['season'] == 1900, 'season'] = 2000
    
    #Give the dataframe a prefix and the player_id so we can use the playoff data later
    exec(F"P_data_{player_id} = y")
    

    #Only select playoff runs with more than 3 games played to adjust for first round injuries 
    y = y[y['P_GP'] > 3]
    



    #-----------------------------------------------------------#
    #----STEP 5:  Combine Regular Season and Playoff Data-------#
    #-----------------------------------------------------------#


    #Merge the RS and Playoff data with an inner join
    x_and_y = pd.merge(x,y, on= 'season')
    
    #Merge the new combined RS and Playoff data with the TS% dataframe made in Step 1
    final_data = pd.merge(x_and_y,League_average_ts_RS_and_Playoffs, on= 'season')
    
    # Calculations used for data analysis 
    final_data['traditional_differential'] = final_data['P_PER'] - final_data['RS_PER']
    final_data['traditional_%change'] =  (((final_data['P_PER'] -  final_data['RS_PER']) / final_data['P_PER'])*100)
    
    #Formula for Adjusted Playoff PER to account for playoff difficulty 
    final_data['adj_P_PER'] = final_data['P_PER'] * ( (((final_data['P_TS%'] - final_data['league_avg_playoff_ts%']) - (final_data['RS_TS%'] - final_data['league_avg_rs_ts%']))*.5)   + final_data['difficulty factor'] ) 
    
    # The next three metrics that start with 'adj_' will all be used in Data Analysis  
    final_data['adj_differential'] = final_data['adj_P_PER'] - final_data['RS_PER']
    final_data['adj_%change'] = (((final_data['adj_P_PER'] -  final_data['RS_PER']) / final_data['adj_P_PER'])*100)

    # 'adj_differential' adjusted for games played to account give more weight to longer playoff runs
    final_data['adj_differential_by_GP'] = (final_data['adj_differential'] * (( final_data['P_GP'] ) / (final_data['P_GP'].sum() ) *  (final_data['P_GP'].count())))

    #Confirming the player_ID in our dataframe is the same as the one being used in the calculations
    final_data['PLAYER_ID'] = player_id

    #Taking the sum of the following stats 
    sum_columns = final_data[['traditional_differential','adj_differential','adj_differential_by_GP']].sum()

    #Taking the average of the following stats 
    average_columns = final_data[[ 'RS_PER','P_PER' , 'adj_P_PER', 'traditional_differential','traditional_%change','adj_differential','adj_%change','adj_differential_by_GP']].mean()

    #Merging the sum and averages of our stats into one dataframe 
    comparative_stats = pd.concat([sum_columns,average_columns])

    #Restructuring the dataframe to be compatible with the .concat function
    comparative_stats['PLAYER_ID'] = player_id
    comparative_stats = comparative_stats.reset_index()
    comparative_stats = comparative_stats.transpose()
    headers = comparative_stats.iloc[0]
    comparative_stats_final  = pd.DataFrame(comparative_stats.values[1:], columns=headers)
    
    #Give the dataframe a prefix and the player_id so we can use the comparative data later
    exec(F"comparative_data_{player_id} = comparative_stats_final")

    #Give the dataframe a prefix and the player_id, this dataframe will be used to double check my work.
    exec(F"all_data_{player_id} = final_data")




    #-----------------------------------------------------------#
    #-----STEP 6 & 7: Organize and Export data for Analysis-----#
    #-----------------------------------------------------------#


    #Combine all dataframes that have the prefix 'comparative_data_'
    player_dataframe_comparative_data = [var for var in globals() if var.startswith('comparative_data_')]
    complete_dataframe_comparative_data = pd.concat([globals()[var] for var in player_dataframe_comparative_data])
    
    #Combine all dataframes that have the prefix 'all_data_'
    player_dataframe_all_data = [var for var in globals() if var.startswith('all_data_')]
    complete_dataframe_all_data = pd.concat([globals()[var] for var in player_dataframe_all_data])
        
    #Combine all dataframes that have the prefix 'P_data_'
    player_dataframe_all_playoff_data = [var for var in globals() if var.startswith('P_data_')]
    complete_dataframe_all_playoff_data = pd.concat([globals()[var] for var in player_dataframe_all_playoff_data])
    
    #Combine all dataframes that have the prefix 'RS_data_'
    player_dataframe_all_RS_data = [var for var in globals() if var.startswith('RS_data_')]
    complete_dataframe_all_RS_data = pd.concat([globals()[var] for var in player_dataframe_all_RS_data])
    
    
#Merge the complete_dataframe_comparative_data and our playerset so we can have player's names in our final dataset
complete_dataframe_comparative_data_final = complete_dataframe_comparative_data.merge(playerset[['PLAYER_ID', 'PLAYER_NAME_x']], on='PLAYER_ID')

#Rename the 'PLAYER_NAME_x' column 
complete_dataframe_comparative_data_final['Player_Name'] = complete_dataframe_comparative_data_final['PLAYER_NAME_x']

#Drop 'PLAYER_NAME_x' to get rid of the duplicate column
complete_dataframe_comparative_data_final = complete_dataframe_comparative_data_final.drop(['PLAYER_NAME_x'],axis=1)

#Make the first column the 'Player_Name'
first_column = complete_dataframe_comparative_data_final.pop('Player_Name')
complete_dataframe_comparative_data_final.insert(0, 'Player_Name', first_column)

#Export complete_dataframe_comparative_data_final as a .CSV (This is the main dataframe we will be using.)
complete_dataframe_comparative_data_final.to_csv('nba_project_1_complete_dataframe_comparative_data.csv')


#The same as above but for complete_dataframe_all_data 
complete_dataframe_all_data_final = complete_dataframe_all_data.merge(playerset[['PLAYER_ID', 'PLAYER_NAME_x']], on='PLAYER_ID')
complete_dataframe_all_data_final['Player_Name'] = complete_dataframe_all_data_final['PLAYER_NAME_x']
complete_dataframe_all_data_final = complete_dataframe_all_data_final.drop(['PLAYER_NAME_x'],axis=1)
first_column_2 = complete_dataframe_all_data_final.pop('Player_Name')
complete_dataframe_all_data_final.insert(0, 'Player_Name', first_column_2)
complete_dataframe_all_data_final.to_csv('nba_project_1_complete_dataframe_all_data.csv')
    

#Select players in the dataset with a average adjusted playoff PER that is higher than 15
complete_dataframe_comparative_data_final_trimmed = complete_dataframe_comparative_data_final[complete_dataframe_comparative_data_final['adj_P_PER'] > 15]

#Export complete_dataframe_comparative_data_final_trimmed as a .CSV
complete_dataframe_comparative_data_final_trimmed.to_csv('nba_project_1_complete_dataframe_comparative_data_trimmed.csv')


#Export complete_dataframe_all_RS_data as a .CSV
complete_dataframe_all_RS_data.to_csv('nba_project_1_RS_stats.csv')

#Export complete_dataframe_all_playoff_data as a .CSV
complete_dataframe_all_playoff_data.to_csv('nba_project_1_playoff_stats.csv')





#-----------------------------------------------------------#
#---------------STEP 8: Get Player Headshots----------------#
#-----------------------------------------------------------#



import urllib.request


start = 0
end = 206

#Given the index number we are on, do the following: 
for player_index in range(start,end+1):

    time.sleep(3)

    #Lookup the Player_ID in playerset based on the index 
    player_id = playerset.at[player_index,'PLAYER_ID']

    #Grab the image from this website
    imgURL = f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"


    urllib.request.urlretrieve(imgURL, f"C:\\Users\\James Coding\\Desktop\\Python\\Project_1_Final\\headshots\\{player_id}.png")