import re
import pandas as pd


galaxies_df = pd.DataFrame(columns = ['galaxy', 'ra', 'dec'])

with open('all_northern_galaxies.reg') as f:
    lines = f.readlines()
    for i,line in enumerate(lines):
        coord_pattern = re.compile(r'\([^)]*\)')
        coord_matches = coord_pattern.findall(line)
        coord_lst = coord_matches[0][1:-1].split(',') 
        ra = float(coord_lst[0])
        dec = float(coord_lst[1])
        name_pattern = re.compile(r'\{[^}]*\}')
        name_matches = name_pattern.findall(line)
        name = name_matches[0][1:-1]
        galaxies_df.loc[i] = [name, ra, dec]

print(galaxies_df)
# galaxies_df.to_csv('all_northern_galaxies.csv')