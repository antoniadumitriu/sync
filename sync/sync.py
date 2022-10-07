import datetime
import hashlib
import os
import sys
import shutil
import time


def synchronize_folders(source_path, replica_path, log_filename):
    # Validate input arguments
    try:
        with open(log_filename, 'a+') as finit:
            finit.write('\n')
            finit.write(datetime.datetime.now().strftime("%Y-%b-%d %H:%M:%S"))
            finit.write('\n')
            finit.write("------------------------------ SYNC ------------------------------")
            finit.write('\n')
            finit.write("      SOURCE: ")
            finit.write(source_path)
            finit.write('\n')
            finit.write(" DESTINATION: ")
            finit.write(replica_path)
            finit.write('\n')
            finit.write("------------------------------------------------------------------")
            finit.write('\n')
    except OSError as err:
        print("Couldn't open or create the log file. Error: {0}".format(err))
        raise

    # Read the files with relative folder from the source path
    source_files_list = []
    for folder, subfolders, files in os.walk(source_path):
        for file in files:
            relative_path = os.path.relpath(folder, source_path)
            source_files_list.append(os.path.join(relative_path, file))

    # print('---- Files that are in the source ---')
    # for file in source_files_list:
    #     print(file)

    # Read the files from the replica path
    replica_files_list = []
    for folder, subfolders, files in os.walk(replica_path):
        for file in files:
            relative_path = os.path.relpath(folder, replica_path)
            replica_files_list.append(os.path.join(relative_path, file))

    # print('---- Files that are in the replica ---')
    # for file in replica_files_list:
    #     print(file)

    # Get the files from the source list that are not in the replica list
    # These need to be created in the replica folder
    files_add_in_replica = list(set(source_files_list) - set(replica_files_list))
    print('---- New files that need to be copied to replica ---')
    with open(log_filename, 'a+') as fcopy:
        for file in files_add_in_replica:
            # Copy files from source to replica
            os.makedirs(os.path.dirname(os.path.join(replica_path, file)), exist_ok=True)
            shutil.copyfile(os.path.join(source_path, file), os.path.join(replica_path, file))
            print("copied new file " + file + " to " + os.path.join(replica_path, file))
            # Write to log
            fcopy.write(datetime.datetime.now().strftime("%Y-%b-%d %H:%M:%S"))
            fcopy.write(" - ")
            fcopy.write("copied new file ")
            fcopy.write(file)
            fcopy.write(" to ")
            fcopy.write(os.path.join(replica_path, file))
            fcopy.write('\n')

    # Get the common files from the source and replica list
    # These need to be checked if there were modified
    source_files_list_as_set = set(source_files_list)
    common_files = list(source_files_list_as_set.intersection(replica_files_list))
    print('---- Common files that were modified and need to be updated ---')
    with open(log_filename, 'a+') as fmodify:
        for file in common_files:
            with open(os.path.join(source_path, file), "rb") as s:
                source_file_hash = hashlib.md5(s.read()).hexdigest()
            with open(os.path.join(replica_path, file), "rb") as r:
                replica_file_hash = hashlib.md5(r.read()).hexdigest()
            if source_file_hash != replica_file_hash:
                # Copy file from source to replica
                shutil.copyfile(os.path.join(source_path, file), os.path.join(replica_path, file))
                print("copied modified file " + file + " to " + os.path.join(replica_path, file))
                # Write to log
                fmodify.write(datetime.datetime.now().strftime("%Y-%b-%d %H:%M:%S"))
                fmodify.write(" - ")
                fmodify.write("copied modified file ")
                fmodify.write(file)
                fmodify.write(" to ")
                fmodify.write(os.path.join(replica_path, file))
                fmodify.write('\n')

    # Get the files from the replica list that are not in the source list
    # These need to be deleted from the replica folder
    files_delete_from_replica = list(set(replica_files_list) - set(source_files_list))
    print('---- Files that need to be deleted from replica ---')
    with open(log_filename, 'a+') as fdelete:
        for file in files_delete_from_replica:
            try:
                os.remove(os.path.join(replica_path, file))
                print("deleted " + os.path.join(replica_path, file))
                # Write to log
                fdelete.write(datetime.datetime.now().strftime("%Y-%b-%d %H:%M:%S"))
                fdelete.write(" - ")
                fdelete.write("deleted ")
                fdelete.write(os.path.join(replica_path, file))
                fdelete.write('\n')
            except OSError as err:
                print("Couldn't delete the file [{0}]. Error: {1}".format(file, err))


if __name__ == '__main__':
    if len(sys.argv) != 5:
        print("Usage: python sync.py {source path} {replica path} {sync in seconds} {log filename}")
        sys.exit()

    source_folder = sys.argv[1]
    replica_folder = sys.argv[2]
    sync_delay = sys.argv[3]
    log_filename = sys.argv[4]

    interrupted = False
    while True:
        print("Syncing...")
        synchronize_folders(source_folder, replica_folder, log_filename)
        time.sleep(5)

        if interrupted:
            print("Done")
            break
