# %%
import pandas as pd

data = {
    'index': [
        1, 2, 3, 4, 5,
        6, 7, 8, 9, 10,
        11, 12, 13, 14, 15,
        16, 17, 18, 19, 20,
        21, 22, 23, 24, 25,
        26, 27, 28, 29, 30, 31, 32, 33, 34
    ],
    'sub': [
        '0001', '0004', '0004', '0004', '0005',
        '0007', '0014', '0016', '0016', '0016',
        '0017', '0017', '0017', '0024', '0025',
        '0025', '0025', '0066', '0066', '0066',
        '0069', '0070', '0075', '0102', '0102',
        '0102', '0102', '0122', '0122',
        '0122', '0122', '0122', '0122',
        '0131'
    ],
    'ses': [
        '02', '02', '03', '04', '04',
        '03', '02', '01', '01', '01',
        '02', '02', '02', '03', '04',
        '04', '04', '03', '03', '03',
        '01', '04', '03', '02', '02',
        '02', '02', '03', '03',
        '03', '03', '03', '03',
        '03'
    ],
    'task': [
        'narratives', 'faces', 'social', 'alignvideo', 'fractional',
        'social', 'narratives', 'social', 'social', 'social',
        'alignvideo', 'alignvideo', 'alignvideo', 'social', 'social',
        'social', 'social', 'social', 'social', 'social',
        'social', 'social', 'shortvideo', 'narratives', 'faces',
        'faces', 'faces', 'social', 'social',
        'social', 'social', 'social', 'social',
        'alignvideo'
    ],
    'run': [
        '02', '01', '03', '01', '01',
        '03', '01', '04', '05', '06',
        '02', '03', '04', '05', '04',
        '05', '06', '03', '04', '06',
        '03', '06', '01', '04', '01',
        '02', '03', '01', '02',
        '03', '04', '05', '06',
        '02'
    ]
}

df = pd.DataFrame(data)
# df.set_index('index', inplace=True)

print(df)
# %%
import json

nested_json = {}

for task, sub_df in df.groupby('task'):
    nested_json[f"task-{task}"] = {}
    
    for sub, sub_df in sub_df.groupby('sub'):
        nested_json[f"task-{task}"][f"sub-{sub}"] = []
        
        for _, row in sub_df.iterrows():
            ses = 'ses-' + row['ses']
            run = 'run-' + row['run']
            value = f"{ses}_{run}"
            
            nested_json[f"task-{task}"][f"sub-{sub}"].append(value)

nested_json_str = json.dumps(nested_json, indent=4)
print(nested_json_str)
file_path = 'not_in_intendedFor.json'
with open(file_path, 'w') as file:
    json.dump(nested_json, file, indent=4)

# %%
for _, row in df.iterrows():
    task = row['task']
    sub = row['sub']
    run = row['run']
    
    item = {
        "task": task,
        "sub": sub,
        "run": run
    }
    
    nested_json["data"].append(item)

nested_json_str = json.dumps(nested_json, indent=4)
print(nested_json_str)
