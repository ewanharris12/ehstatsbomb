import os
import pandas as pd
import json
from pandas.io.json import json_normalize

class MyClass:
    def __init__(self):
        self._match_info_df = None
        self._root_path = None

    @staticmethod
    def _test_print():
        print('Test Successful')
        print('Code running well')

    @staticmethod
    def _open_json_file(file_path):
        """
        Open a json file as a Pandas dataframe when given a path e.g. python_prjects/data/7298.json
        """
        assert file_path.endswith('.json') == True, f"File is not json, broken link: {file_path}"
        data_file = open(file_path, encoding='utf-8')
        data = json.load(data_file)
        df = json_normalize(data, sep = "_")

        return df

    def _extract_all_json_files(self, folder_path):
        """
        Open all json files from a particular folder, concatenates as a df
        """
        assert folder_path[-1] == '/', "Path must finish with /"
        export_df = pd.DataFrame()

        for filename in os.listdir(folder_path):
            if filename.endswith('.json'):
                file_path = folder_path + filename
                df = self._open_json_file(file_path)

                export_df  = pd.concat([export_df,df], sort=False)

        return export_df

    def get_all_match_info(self, matches_path, folders=None):
        """
        Pass the matches_path e.g. 'python_prjects/data/matches/'
        Pass list of folders which contain match data (optional - otherwise will scan all folders)
        """
        if matches_path[-1] != '/':
            matches_path = matches_path+'/'
            print('Path corrected, / added')

        match_info = pd.DataFrame()

        self._root_path = matches_path.replace('matches/','')

        if not folders:
            folders = os.listdir(matches_path)

        for folder in folders:
                folder_path = matches_path + folder + '/'
                folder_df = self._extract_all_json_files(folder_path)
                print(f'Folder {folder} extracted')

                match_info = pd.concat([match_info,folder_df], sort=False).reset_index(drop=True)
        
        # Remove some of the stupid names
        match_info.rename(columns={'competition_competition_id':'competition_id',
                                    'competition_competition_name':'competition_name',
                                    'season_season_id':'season_id',
                                    'season_season_name':'season_name',
                                    'home_team_home_team_id':'home_team_id',
                                    'home_team_home_team_name':'home_team_name',
                                    'home_team_home_team_gender':'home_team_gender',
                                    'home_team_home_team_group':'home_team_group',
                                    'away_team_away_team_id':'away_team_id',
                                    'away_team_away_team_name':'away_team_name',
                                    'away_team_away_team_gender':'away_team_gender',
                                    'away_team_away_team_group':'away_team_group'}, inplace=True)

        # "Caches" a version of match_info to use in other functions
        if  self._match_info_df == None:
            self._match_info_df = match_info

        else:
            self._match_info_df = pd.concat([self._match_info_df,match_info], sort=False).drop_duplicates().reset_index(drop=True)

        return match_info

    def get_team_match_ids(self, identifier, category):
        """
        Return list of match ids which include the team you have specified
        Category can be 'name' or 'id' 
        """
        assert category in ['name','id']
        assert identifier != None, "Team identifier not specified"
        assert self._match_info_df is not None, "Match info dataframe not found, please run get_all_match_info"

        hfilter = 'home_team_' + category
        afilter = 'away_team_' + category

        _df = self._match_info_df[(self._match_info_df[hfilter]==identifier) | (self._match_info_df[afilter]==identifier)]
        
        ids = _df['match_id'].unique().tolist()

        assert len(ids)>0, "No matches found"

        return ids

    def get_specific_match(self, match_id, path=None):
        """
        Specify a match_id and a dataframe of all the event data from that match is returned
        """

        if path == None:
            assert self._root_path != None, "path must be specified"
            path = self._root_path + 'events/'

        if path[-1] != '/':
            path = path+'/'

        full_path = f'{path}{match_id}.json'

        assert os.path.exists(full_path), f"File does not exist at this path: {full_path}"

        df = self._open_json_file(full_path)

        return df

    def get_team_event_data(self, identifier, category):
        """
        Return event data from all matches involving your chosen team
        """
        assert category in ['name','id']
        assert identifier != None, "Team identifier not specified"

        matches = self.get_team_match_ids(identifier,category)
        events = pd.DataFrame()

        for id in matches:
            _df = self.get_specific_match(id)
            events = pd.concat([events,_df], sort=False)

        return events






