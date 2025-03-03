import pandas as pd

# Replace 'input.tsv' with your TSV filename

fname = '/Users/h/Documents/projects_local/1076_spacetop/sub-0088/ses-03/func/sub-0088_ses-03_task-social_acq-mb8_run-03_events.tsv'


# Read the TSV file
df = pd.read_csv(fname, sep='\t')

# Set 'onset' and 'duration' to "n/a" when 'trial_index' is 10, 11, or 12
df.loc[df['trial_index'].isin([10, 11, 12]), ['onset', 'duration']] = 'n/a'

# Save the modified DataFrame to a new TSV file
df.to_csv(fname, sep='\t', index=False)

print("Modified file saved as", fname)
