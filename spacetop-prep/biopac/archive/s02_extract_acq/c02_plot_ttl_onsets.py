# grab all .csv files
# concatenate into one big dataframe
# TODO: add sub, ses, run, task info to pandas
# resources:
# * https://community.plotly.com/t/multiple-traces-plotly-express/23360/4
# %%

from operator import index
import os, glob
from turtle import color
import pandas as pd
import matplotlib.pyplot as plt


# %%
main_dir = '/Volumes/spacetop'
ttl_list = glob.glob(
    os.path.join(main_dir, 'biopac', 'dartmouth', 'b03_extract_ttl', 
    'sub-*', 'ses-*', 'task-social', 'sub-*_ses-*_task-social_run-*_physio-ttl.csv')) 

# %% concatenate pandas dataframe
appended_data = []
for infile in ttl_list:
    data = pd.read_csv(infile)
    appended_data.append(data)
final_df = pd.concat(appended_data)
final_df.reset_index(inplace=True)

# %% 
final_df.to_csv('/Users/h/Desktop/biopac_ttl_onset.csv')
# f"{sub}_{ses}_{task}_{run}_physio-ttl.csv"
# %% plot
# MATPLOTLIB
from matplotlib.pyplot import figure
figure(figsize=(6, 20), dpi=300)
plt.plot(final_df.ttl_r1, final_df.index, linestyle="",marker="o", markersize = 1)
plt.plot(final_df.ttl_r2, final_df.index, linestyle="",marker="o", markersize = 1)
plt.plot(final_df.ttl_r3, final_df.index, linestyle="",marker="o", markersize = 1)
plt.plot(final_df.ttl_r4, final_df.index, linestyle="",marker="o", markersize = 1)
plt.xlim([-2.5, 18])
plt.xlabel('time (s)')
plt.ylabel('trial no #')
plt.vlines(2, 0, len(final_df), colors='orange', linestyles ="dashed")
plt.vlines(7, 0, len(final_df), colors='green', linestyles ="dashed")
plt.vlines(9, 0, len(final_df), colors='red', linestyles ="dashed")


# %%
# PLOTLY
import os, glob
import plotly 
import pandas as pd
import dash_core_components as dcc
import plotly.express as px

# %%
final_df = pd.read_csv('/Users/h/Desktop/biopac_ttl_onset.csv')
final_df.reset_index(inplace=True)
final_df.rename( columns={'Unnamed: 0':'stacked_trials'}, inplace=True )

# %% PLOTLY

melt_df = pd.melt(plotly_df, 
id_vars = 'stacked_trials', 
var_name = 'ttl', 
value_name = 'onset')
# %%
fig_plotly = px.scatter(data_frame = melt_df, 
                        x='onset', y='stacked_trials', 
                        color = 'ttl', range_x=[-5,20], 
                        marginal_x='box', 
                        size_max = 5,
                        # mode = 'markers'
                        # marker
                        )
fig_plotly.update_xaxes(title_text='Pain trial TTL onset (s)')
fig_plotly.update_yaxes(title_text='trial No.')
lines = {'ttl1':2,'ttl2':7,'ttl3':9}
line_col = {'ttl1':'red','ttl2':'green','ttl3':'magenta'}
for k in lines.keys():
    fig_plotly.add_shape(type='line',
                    yref="y",
                    xref="x",
                    x0=lines[k],
                    y0=-3,
                    x1=lines[k],
                    y1=melt_df['stacked_trials'].max()*1,
                    line={'dash': 'dash', 'color':line_col[k]}
                    )
fig_plotly.update_traces(marker=dict(size=3),
                  selector=dict(mode='markers'),
                  )

fig_plotly.update_layout(
    width=500, height=1000)
fig_plotly
