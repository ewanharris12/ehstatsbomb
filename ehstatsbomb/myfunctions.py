import os
import pandas as pd
import json
from pandas.io.json import json_normalize

@staticmethod
def _test_print():
    print('Test Successful')
    print('Code running well')

@staticmethod
def _open_json_file(file_path):
    """
    Open a json file as a Pandas dataframe when given a path e.g. python_prjects/data/7298.json
    """
    filepath = os.listdir(file_path)
    
    assert filepath.endswith('.json') == False, "File is not json"
    data_file = open(filepath, encoding='utf-8')
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
        matches_path+'/'
        print('Path corrected, / added')

    match_info = pd.DataFrame()

    if not folders:
        folders = os.listdir(matches_path)

    for folder in folders:
            folder_path = matches_path + folder + '/'
            folder_df = self._extract_all_json_files(folder_path)
            print(f'Folder {folder} extracted')

            match_info = pd.concat([match_info,folder_df], sort=False)

    return match_info





