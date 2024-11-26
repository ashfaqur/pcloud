import json
import shutil
import subprocess
import os
from datetime import datetime


INPUT_FILE = "env/input.json"
CLOUD_PATH = "cloudpath"
LOCAL_PATH = "localpath"

paths: list[str] = []


def validate_input() -> dict[str, str]:
    if not os.path.exists(INPUT_FILE):
        raise Exception(f"Input file '{INPUT_FILE}' does not exist.")
    # Open and read the JSON file
    with open(INPUT_FILE, "r") as file:
        data: dict[str, str] = json.load(file)
    cloudpath = data.get(CLOUD_PATH)
    if not cloudpath:
        raise Exception("The 'cloudpath' field does not exist.")
    if not os.path.exists(cloudpath):
        raise Exception(f"The cloudpath '{cloudpath}' does not exist")

    localpath = data.get(LOCAL_PATH)
    if not localpath:
        raise Exception("The 'localpath' field does not exist.")
    if not os.path.exists(localpath):
        raise Exception(f"The localpath '{localpath}' does not exist")

    return data


def main(input: dict[str, str]) -> None:
    localPath = input[LOCAL_PATH]
    cloudPath: str = input[CLOUD_PATH]
    files_skipped = 0
    files_copied = 0
    # Walk through the directory tree
    for root, dirs, files in os.walk(cloudPath):
        for file_name in files:
            absolute_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(absolute_path, cloudPath)
            destination_path = os.path.join(localPath, relative_path)
            # print(f"Processing file: {file_name}")
            # print(f"  Source: {absolute_path}")
            # print(f"  Destination: {destination_path}")
            # Ensure the destination directory exists
            destination_dir = os.path.dirname(destination_path)
            if not os.path.exists(destination_dir):
                # print(f"Creating directory: {destination_dir}")
                os.makedirs(destination_dir)
            if not os.path.exists(destination_path):
                # print(f"Copying to {localPath}")
                files_copied += 1
                # shutil.copyfile(absolute_path, os.path.join(localPath, relative_path))
            else:
                files_skipped += 1
                # print(f"File already exists in {localPath}")
    print("Summary:")
    print(f"Files copied: {files_copied}")
    print(f"Files skipped: {files_skipped}")

    run_git_commands(localPath, "update")


def run_git_commands(git_repo: str, commit_message: str):
    try:
        os.chdir(git_repo)
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            stdout=subprocess.PIPE,
            text=True,
        )
        if not result.stdout.strip():
            print("No changes to commit. Working tree is clean.")
            return
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running Git command: {e}")
    except FileNotFoundError:
        print("Git is not installed or the path is incorrect.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    input: dict[str, str] = validate_input()
    main(input)
