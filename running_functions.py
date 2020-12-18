import ehstatsbomb
import os
import json
from pandas.io.json import json_normalize
import pandas as pd

# %%
from ehstatsbomb import ehsb
sb = ehsb.MyClass()

# # %%
# mp = 'C:/Users/Ewan/OneDrive - Kubrick Group/Personal Development Projects/open-data-master/data/matches/'
# mi = sb.get_all_match_info(matches_path=mp)

# # %%
# tmis = sb.get_team_match_ids('Chelsea FCW','name')

# # %%
spec_match = sb.get_specific_match('19748', path='C:/Users/Ewan/OneDrive - Kubrick Group/Personal Development Projects/open-data-master/data/events/')