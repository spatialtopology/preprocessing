# scans_list = sorted(glob.glob('sub-*/**/*scans*.tsv', recursive=True))
# for scan_fname in scans_list:
#     # NOTE: Step 1: Get the scans.tsv using datalad
#     run_command(f"datalad get {scan_fname}")
#     print(f"datalad get {scan_fname} ")
#     # Check if scans_file is not empty and unlock it using git annex
#     if os.path.exists(scan_fname) and os.path.getsize(scan_fname) > 0:
#         run_command(f"git annex unlock {scan_fname}")
#         print(f"unlock {scan_fname}")

#     scans_df = pd.read_csv(scan_fname, sep='\t')

#     # NOTE: Step 2: Define the directory containing the task-cue event files
#     cue_events_dir = './' + os.path.dirname( scan_fname) + '/func'
#     cue_event_files = sorted([f for f in os.listdir(cue_events_dir) if 'task-cue' in f and f.endswith('_events.tsv')])

#     # NOTE: Step 3: Function to extract cue metadata and run information from filenames
#     # Create a dictionary to map run to cue metadata
#     cue_metadata_dict = {}
#     for file in cue_event_files:
#         metadata, run = extract_cue_metadata_and_run(file)
#         cue_metadata_dict[run] = metadata


#     # NOTE: Step 4: Apply the function to add the task-social_runtype column
#     scans_df['task-social_runtype'] = scans_df['filename'].apply(lambda x: map_social_to_cue(x) if 'task-social' in x else None)
#     scans_df['task-social_runtype'].fillna('n/a', inplace=True)


#     # NOTE: Step 5: if events file and niftifiles disagree, delete files
#     nifti_files, event_files = list_nifti_and_event_files(cue_events_dir)
#     orphan_files = remove_orphan_nifti_files(nifti_files, event_files)
#     if orphan_files:
#         for orphan_file in orphan_files:
#             print(f"Removing {orphan_file}")
#             #run_command(f"git rm {orphan_file}")
#             scans_df = scans_df[scans_df['filename'] != os.path.basename(orphan_file)]

#     # Save the updated DataFrame back to the scans_file
#     scans_df.to_csv(scan_fname, index=False, sep='\t')

#     # Add the updated scans_file back to git annex
#     print(f"made edits to events file and deleted nifti files if not harmonized: {scan_fname}")
#     run_command(f"git annex add {scan_fname}")
#     run_command(f"git commit -m 'DOC: update scans tsv with task-social runtype metadata and remove orphan NIfTI files'")

    
#     # run_command(f"git annex add {scan_fname}")
#     # run_command(f"git commit -m 'DOC: update scans tsv and remove orphan NIfTI files'")
#     # NOTE: Step 6: ultimately, delete BIDS data
#     for event_fname in cue_event_files:
#         event_fpath = os.path.join(cue_events_dir, event_fname)
#         run_command(f"git rm {event_fpath}")
#         print(f"remove all the task-cue events files {event_fpath}")
#     run_command(f"git commit -m 'DEP: delete non-bids compliant events file'")
#     print("run_command(git commit -m DEP: delete non-bids compliant events file")
