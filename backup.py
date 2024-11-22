import json
import shutil
import os
import datetime

from pcloud import PyCloud  # type: ignore

paths: list[str] = []


def main() -> None:

    input_file = "env/input.json"

    # Open and read the JSON file
    with open(input_file, "r") as file:
        data = json.load(file)

    username = data.get("username")
    if not username:
        raise Exception(
            "The 'username' field does not exist or is empty in the JSON data."
        )

    password = data.get("password")
    if not password:
        raise Exception(
            "The 'password' field does not exist or is empty in the JSON data."
        )

    endpoint = data.get("endpoint")
    if not endpoint:
        raise Exception(
            "The 'endpoint' field does not exist or is empty in the JSON data."
        )

    cloudpath = data.get("cloudpath")
    if not cloudpath:
        raise Exception(
            "The 'cloudpath' field does not exist or is empty in the JSON data."
        )
    localpath = data.get("localpath")
    if not localpath:
        raise Exception(
            "The 'localpath' field does not exist or is empty in the JSON data."
        )

    modification_date = get_folder_modification_date(localpath)

    print(f"The folder was last modified on: {modification_date}")

    print(f"Backuping {cloudpath} to {localpath}")

    pc = PyCloud(username, password, endpoint)
    info = pc.listfolder(path="/Documents", recursive=True)

    contents = info.get("metadata").get("contents")
    print_contents(contents, "/Documents")

    file_path = "build/output.json"

    # Writing the JSON data to a file
    with open(file_path, "w") as file:
        json.dump(info, file, indent=4)

    print(f"JSON data has been saved to {file_path}")

    for path in paths:
        # print(f"Path is {path}")
        localFilePath = path.replace("/Documents/", localpath)
        # print(f"Local file path is {localFilePath}")

        if not os.path.exists(localFilePath):
            # print(f"File does not exist: {localFilePath}")
            directory = os.path.dirname(localFilePath)
            if not os.path.exists(directory):
                print(f"Creating directory: {directory}")
                os.makedirs(directory)
            newPath = path.replace("/Documents/", "/home/ash/pCloudDrive/Documents/")
            print(newPath)
            print(localFilePath)
            shutil.copyfile(newPath, localFilePath)
            # print(f"Result: {code}")


def print_contents(contents, parent):
    for item in contents:
        if item.get("isfolder"):
            path = parent + "/" + item.get("name")

            # Recursively call the function to handle the nested contents
            if item.get("contents"):
                print_contents(item.get("contents"), path)
        else:
            path = parent + "/" + item.get("name")
            paths.append(path)
            # print(f"File: {path}")


def get_folder_modification_date(folder_path):
    # Get the last modification time (in seconds since the epoch)
    modification_time = os.path.getmtime(folder_path)

    # Convert the modification time to a human-readable format
    modification_date = datetime.datetime.fromtimestamp(modification_time)

    return modification_date


if __name__ == "__main__":
    main()
