# pcloud

A simple python script for making a local backup file copy from
a pcloud mount.


    python backup.py -h

    usage: backup.py [-h] [-v] [-l LOG_DIR] source destination

    Backup files from a cloud storage to a local storage.

    positional arguments:
    source                Path to cloud storage source
    destination           Path to local storage destination

    options:
    -h, --help            show this help message and exit
    -v, --verbose         Set the log level to DEBUG
    -l LOG_DIR, --log_dir LOG_DIR
                            Path to log directory
