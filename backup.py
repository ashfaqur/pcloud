import logging
import json
import shutil
import subprocess
import os
from datetime import datetime
from argparse import ArgumentParser


logger = logging.getLogger(__name__)

INPUT_FILE = "env/input.json"
CLOUD_PATH = "cloudpath"
LOCAL_PATH = "localpath"

paths: list[str] = []


def validate_input(source: str, destination: str):
    if not source:
        raise Exception("The 'cloudpath' field does not exist.")
    if not os.path.exists(source):
        raise Exception(f"The cloudpath '{source}' does not exist")
    if not destination:
        raise Exception("The 'localpath' field does not exist.")
    if not os.path.exists(destination):
        raise Exception(f"The localpath '{destination}' does not exist")


def main(source: str, destination: str) -> None:

    files_skipped = 0
    files_copied = 0
    # Walk through the directory tree
    for root, dirs, files in os.walk(source):
        for file_name in files:
            absolute_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(absolute_path, source)
            destination_path = os.path.join(destination, relative_path)
            logger.debug(f"Processing file: {file_name}")
            logger.debug(f"  Source: {absolute_path}")
            logger.debug(f"  Destination: {destination_path}")
            # Ensure the destination directory exists
            destination_dir = os.path.dirname(destination_path)
            if not os.path.exists(destination_dir):
                logger.debug(f"Creating directory: {destination_dir}")
                os.makedirs(destination_dir)
            if not os.path.exists(destination_path):
                logger.debug(f"Copying to {destination_path}")
                shutil.copyfile(absolute_path, destination_path)
                files_copied += 1
            else:
                files_skipped += 1
                logger.debug(f"File already exists in {destination_path}")
    logger.info("Summary:")
    logger.info(f"Files copied: {files_copied}")
    logger.info(f"Files skipped: {files_skipped}")

    run_git_commands(destination, "update")


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
        logger.error(f"Error while running Git command: {e}")
    except FileNotFoundError:
        logger.error("Git is not installed or the path is incorrect.")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


def args_parser() -> ArgumentParser:
    """
    Parses command line arguments.

    :return: An ArgumentParser object containing parsed command line arguments.
    :rtype: ArgumentParser
    """
    arg_parser: ArgumentParser = ArgumentParser(
        description="Backup files from a cloud storage to a local storage."
    )
    arg_parser.add_argument("source", type=str, help="Path to cloud storage source")
    arg_parser.add_argument(
        "destination", type=str, help="Path to local storage destination"
    )
    arg_parser.add_argument(
        "-v", "--verbose", action="store_true", help="Set the log level to DEBUG"
    )
    arg_parser.add_argument("-l", "--log", type=str, help="Path to log file")
    return arg_parser


def setup_logging(args):
    log_level = logging.INFO
    if args.verbose:
        log_level = logging.DEBUG
    if args.log:
        logging.basicConfig(
            filename=args.log,
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=log_level,
            datefmt="%H:%M:%S",
        )
    else:
        logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=log_level,
            datefmt="%H:%M:%S",
        )


if __name__ == "__main__":
    parser: ArgumentParser = args_parser()
    args = parser.parse_args()
    setup_logging(args)
    source: str = args.source
    destination: str = args.destination
    validate_input(source, destination)
    main(source, destination)
