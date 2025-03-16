import os

# Folder containing the songs
folder_path = "D:\Downl\Music"

# Ensure the folder exists
if not os.path.exists(folder_path):
    print(f"Folder '{folder_path}' not found.")
else:
    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        old_path = os.path.join(folder_path, filename)
        
        # Check if it's a file (not a folder)
        if os.path.isfile(old_path):
            # Split at the first hyphen and keep the part after it
            new_name = filename.split('- ', 1)[-1] if '- ' in filename else filename
            new_path = os.path.join(folder_path, new_name)

            # Rename the file
            os.rename(old_path, new_path)
            print(f"Renamed: '{filename}' -> '{new_name}'")

    print("Renaming completed!")
