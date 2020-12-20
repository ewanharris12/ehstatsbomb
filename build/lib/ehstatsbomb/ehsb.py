import os
import pandas as pd
import json
from pandas.io.json import json_normalize
import matplotlib.pyplot as plt
from matplotlib.patches import Arc

class MyClass:
    def __init__(self):
        self._match_info_df = None
        self._root_path = None
        self._title_font = "Alegreya Sans"
        self._main_font = "Open Sans"
        
        # import colour codes for teams
        self._c = pd.read_csv("C:\Users\Ewan\Git Repo\ehstatsbomb\ehstatsbomb\color-coding-teams.csv").set_index('name')
        self._c['colcode'].fillna('blue', inplace=True)
        self._c['textcode'].fillna('white', inplace=True)

        self._colours = self._c.to_dict()


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

    def get_starting_xis(self, match_id, ha=None, form='df', path=None):
        """
        Get a dictionary or dataframe of starting xis from a particular match, this returns the Player Id, Name and Jersey Number
        ha can be 'Home' or 'Away' if you only want one of the XIs
        form can 'dic' or 'df' (Default) for Dictionary or DataFrame
        """
        assert ha in ['Home','Away',None], f"Invalid ha: {ha}"
        assert form in ['df','dic'], f"Invalid format: {form}"

        if path == None:
            assert self._root_path != None, "path must be specified"
            path = self._root_path + 'events/'

        df = self.get_specific_match(match_id, path=path)

        df = df[df['type_name'] == 'Starting XI']

        home_xi = df.iloc[0]['tactics_lineup']
        away_xi = df.iloc[1]['tactics_lineup']

        ht, at = {},{}

        for item,dic,team in zip([home_xi, away_xi],[ht,at],['home','away']):
            for i in item:
                id = i['player']['id']
                dic[id] = {}
                dic[id]['team'] = team
                dic[id]['name'] = i['player']['name']
                dic[id]['number'] = i['jersey_number']
                dic[id]['position_id'] = i['position']['id']
                dic[id]['position'] = i['position']['name']

        if ha == 'Home':
            if form == 'dic':
                return ht
            else:
                return pd.DataFrame(ht).T

        elif ha == 'Away':
            if form == 'dic':
                return at
            else:
                return pd.DataFrame(at).T

        else:
            ht.update(at)
            if form == 'dic':
                return ht
            else:
                return pd.DataFrame(ht).T


    def get_avg_positions(self, match_id, path=None):
        """
        Get average positions of the Starting XIs from a particular game
        valid_until column is the timestamp (format: MM:SS) of the first substitution for that team (the time up to which average positions are calculated)
        """
        if path == None:
            assert self._root_path != None, "path must be specified"
            path = self._root_path + 'events/'

        xis = self.get_starting_xis(match_id, path=path)
        events = self.get_specific_match(match_id, path=path)

        events['time_ticker'] = (events['minute']*60) + events['second']


        sub_dict = events[events['type_name'] == 'Substitution'].groupby('team_id').agg(
            {'minute':lambda x: x.iloc[0],'second':lambda x: x.iloc[0],'time_ticker':'min'}).to_dict()

        #players = xis.index.tolist()

        df = events[['team_id','team_name','player_id','player_name','location','time_ticker','minute','second']].dropna()

        df = df.merge(xis, how='inner', left_on='player_id', right_index=True)

        df['x'] = df['location'].apply(lambda x: x[0])
        df['y'] = df['location'].apply(lambda x: x[1])

        presub_df = pd.DataFrame()

        for team in df['team_id'].unique().tolist():
            _df = df[(df['team_id'] == team) & (df['team_id'] < sub_dict['time_ticker'][team])]
            _df['valid_until'] = str(sub_dict['minute'][team]) + ':' + str(sub_dict['second'][team])
            presub_df = pd.concat([presub_df,_df])


        presub_df = presub_df.groupby(['team_id','team_name','player_id','player_name'
                            ,'team', 'number', 'position_id', 'position','valid_until'], as_index=False).agg({'x':'mean','y':'mean'})

        return presub_df


    @staticmethod
    def _plot_football_pitch(scale, lcolour='white', pcolour='grey', fcolour='#444444'):
        #Create figure
        fig=plt.figure(figsize=[scale*6,scale*4])
        ax=fig.add_subplot(1,1,1)
        
        # Set colours
        fig.set_facecolor(fcolour)
        ax.patch.set_facecolor(pcolour)

        #Pitch Outline & Centre Line
        plt.plot([0,0],[0,90], color=lcolour)
        plt.plot([0,130],[90,90], color=lcolour)
        plt.plot([130,130],[90,0], color=lcolour)
        plt.plot([130,0],[0,0], color=lcolour)
        plt.plot([65,65],[0,90], color=lcolour)

        #Left Penalty Area
        plt.plot([16.5,16.5],[65,25],color=lcolour)
        plt.plot([0,16.5],[65,65],color=lcolour)
        plt.plot([16.5,0],[25,25],color=lcolour)

        #Right Penalty Area
        plt.plot([130,113.5],[65,65],color=lcolour)
        plt.plot([113.5,113.5],[65,25],color=lcolour)
        plt.plot([113.5,130],[25,25],color=lcolour)

        #Left 6-yard Box
        plt.plot([0,5.5],[54,54],color=lcolour)
        plt.plot([5.5,5.5],[54,36],color=lcolour)
        plt.plot([5.5,0.5],[36,36],color=lcolour)

        #Right 6-yard Box
        plt.plot([130,124.5],[54,54],color=lcolour)
        plt.plot([124.5,124.5],[54,36],color=lcolour)
        plt.plot([124.5,130],[36,36],color=lcolour)

        #Prepare Circles
        centreCircle = plt.Circle((65,45),9.15,color=lcolour,fill=False)
        centreSpot = plt.Circle((65,45),0.8,color=lcolour)
        leftPenSpot = plt.Circle((11,45),0.8,color=lcolour)
        rightPenSpot = plt.Circle((119,45),0.8,color=lcolour)

        #Draw Circles
        ax.add_patch(centreCircle)
        ax.add_patch(centreSpot)
        ax.add_patch(leftPenSpot)
        ax.add_patch(rightPenSpot)

        #Prepare Arcs
        leftArc = Arc((11,45),height=18.3,width=18.3,angle=0,theta1=310,theta2=50,color=lcolour)
        rightArc = Arc((119,45),height=18.3,width=18.3,angle=0,theta1=130,theta2=230,color=lcolour)

        #Draw Arcs
        ax.add_patch(leftArc)
        ax.add_patch(rightArc)

        #Tidy Axes
        plt.axis('off')

    def plot_avg_positions(self, match_id, ha='All', path=None, scale=1, fsize=12):
        """
        Plot the average postitions of the Starting XIs on a football pitch
        ha can be 'Home', 'Away' or 'All'
        """
        assert match_id != None, "Specify a match_id"
        assert ha in ['Home','Away','All'], f"ha not recognised: {ha}"

        if path == None:
            assert self._root_path != None, "path must be specified"
            path = self._root_path + 'events/'

        df = self.get_avg_positions(match_id, path=path)

        home = df[df['team'] == 'home']
        away = df[df['team'] == 'away']

        cdict = {'home':'r','away':'b'}

        self._plot_football_pitch(scale=scale)

        if ha == 'Home':
            lists = zip([home],['home'],[0],['left'])
        elif ha == 'Away':
            lists = zip([away],['away'],[0],['left'])
        else:
            lists = zip([home,away],['home','away'],[0,130],['left','right'])
            pd.set_option('mode.chained_assignment', None)
            away['x'] = 120 - away['x']
            away['y'] = 80 - away['y']             
        
        for team,name,x,align in lists:
            plt.scatter(team['x'],team['y'], s=200*scale, marker='o', c=self._colours['colcode'][name])
            plt.text(x=x,y=96, s=team['team_name'].max(), c=self._colours['colcode'][name], fontsize=10*scale
            , ha=align, fontfamily=self._title_font, fontweight="bold")
            plt.text(x=x,y=92, s="Valid up to: " + team['valid_until'].max(), c='w', fontsize=6*scale
                     , ha=align, fontfamily=self._main_font)
            for player in team.index:
                plt.annotate(xy=(team.loc[player]['x'],team.loc[player]['y']-1/scale),s=team.loc[player]['number']
                , fontsize=12, c=self._colours['textcode'][team.loc[player]['name']], ha="center", fontfamily=self._main_font)

    def plot_passing_maps(self, match_id, ha='All', path=None, scale=1, fsize=12):
        """
        Plot the Starting XIs average positions and who they passed to regularly (represented by the thickness of the lines between players)
        threshold = minimum number of passes from one individual to another (in either direction) for it to be represented in the plot
        """
        assert match_id != None, "Specify a match_id"
        assert ha in ['Home','Away','All'], f"ha not recognised: {ha}"

        if path == None:
            assert self._root_path != None, "path must be specified"
            path = self._root_path + 'events/'

        match = self.get_specific_match(match_id, path=path)
        passing = match[(match['type_name']=='Pass') & (pd.isnull(match['pass_outcome_name']))]

        p = passing[['id','player_id','player_name','pass_recipient_id','pass_recipient_name']]

        p_agg = p.groupby(['player_id','player_name','pass_recipient_id','pass_recipient_name'],as_index=False).agg({'id':'count'}
                                                                                                   ).rename(columns={'id':'count'})
        
        combined_passes = pd.DataFrame()
        players = p_agg['player_name'].unique().tolist()
        recips = p_agg['pass_recipient_name'].unique().tolist()

        for player in players:
            if player in recips:
                recips.remove(player)
            for receiver in recips:
                player_list = [player,receiver]
                df = p_agg[(p_agg.player_name.isin(player_list)) & (p_agg.pass_recipient_name.isin(player_list))]
                agg = df.agg({'player_id':'max', 'player_name':'max', 'pass_recipient_id':'min', 'pass_recipient_name':'min',
            'count':'sum'})
                
                agg = pd.DataFrame(agg).T.dropna()
                
                combined_passes = pd.concat([combined_passes,agg])

        avg_pos = self.get_avg_positions(match_id, path=path)

        recip_location = avg_pos[['player_id','x','y']].rename(columns={'player_id':'pass_recipient_id','x':'recip_x','y':'recip_y'})

        all_passes = combined_passes.merge(recip_location, how='left', on='pass_recipient_id')

        passing_graph = avg_pos.merge(all_passes, how='left', on=['player_id','player_name'])

        self.plot_avg_positions(match_id,scale=scale, ha=ha, path=path)
        cdict = {'home':'r','away':'b'}

        if ha != 'All':
            passing_graph = passing_graph[passing_graph['team'] == ha.lower()]


        for i in passing_graph.index:
            name = passing_graph.loc[i]['team']
            w =passing_graph.loc[i]['count']
            
            if (name == 'away') & (ha == 'All'):
                x = 120-passing_graph.loc[i]['x']
                recip_x = 120-passing_graph.loc[i]['recip_x']
                y = 80-passing_graph.loc[i]['y']
                recip_y = 80-passing_graph.loc[i]['recip_y']
                
            else:
                x = passing_graph.loc[i]['x']
                recip_x = passing_graph.loc[i]['recip_x']
                y = passing_graph.loc[i]['y']
                recip_y = passing_graph.loc[i]['recip_y']
            #plt.scatter(x=passing_graph.loc[i]['x'],y=passing_graph.loc[i]['y'], c=cdict[name])
            
            plt.plot([x,recip_x]
                    ,[y,recip_y], c=self._colours['colcode'][name], linewidth=w/3)