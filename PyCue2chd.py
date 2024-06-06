import os
import subprocess
import concurrent.futures

# Path to the directory containing the PSX ROMs
roms_dir = r'G:\batocera\roms\psx'

# Function to check for existing CHD/CHX files and clean up corresponding BIN/CUE files
def cleanup_existing_chd_chx_files():
    all_files = os.listdir(roms_dir)
    for file in all_files:
        if file.endswith(('.bin', '.cue')):
            base_name = os.path.splitext(file)[0]
            chd_file = base_name + '.chd'
            chx_file = base_name + '.chx'
            if os.path.exists(os.path.join(roms_dir, chd_file)) or os.path.exists(os.path.join(roms_dir, chx_file)):
                delete_original_files([file for file in all_files if file.startswith(base_name) and file.endswith(('.bin', '.cue'))])

# Function to convert BIN/CUE to CHD using chdman
def convert_to_chd(game_files):
    # Find the main BIN file (usually the largest one)
    bin_files = [f for f in game_files if f.endswith('.bin')]
    if not bin_files:
        return
    main_bin = max(bin_files, key=lambda x: os.path.getsize(os.path.join(roms_dir, x)))

    # Create the CHD file name
    chd_file = os.path.splitext(main_bin)[0] + '.chd'

    # Prepare the chdman command
    command = ['chdman', 'createcd', '-i', os.path.join(roms_dir, main_bin), '-o', os.path.join(roms_dir, chd_file)]

    # Execute the command
    try:
        subprocess.run(command, check=True)
        print(f'Successfully converted {main_bin} to {chd_file}')
        delete_original_files(game_files)  # Delete the original files after successful conversion
    except subprocess.CalledProcessError as e:
        print(f'Error converting {main_bin} to {chd_file}: {e}')

# Function to delete original BIN and CUE files after conversion
def delete_original_files(game_files):
    for file in game_files:
        file_path = os.path.join(roms_dir, file)
        try:
            os.remove(file_path)
            print(f'Deleted {file_path}')
        except OSError as e:
            print(f'Error deleting {file_path}: {e}')

# Clean up existing CHD/CHX files
cleanup_existing_chd_chx_files()

# Get the list of all files in the ROMs directory
all_files = os.listdir(roms_dir)

# Group files by game prefix (excluding track numbers and extensions)
games = {}
for file in all_files:
    if file.endswith(('.bin', '.cue')):
        # Extract the game prefix (game name without track number and extension)
        game_prefix = file.rsplit(' (Track ', 1)[0]
        games.setdefault(game_prefix, []).append(file)

# Convert each game's files to a single CHD file using multithreading
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(convert_to_chd, game_files) for game_files in games.values()]
    for future in concurrent.futures.as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f'Error occurred: {e}')
