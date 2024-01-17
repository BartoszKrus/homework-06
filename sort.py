import os
import shutil
import sys
import unicodedata
import re
import zipfile
import tarfile


IMAGE_EXTENSIONS = {'JPEG', 'PNG', 'JPG', 'SVG'}
VIDEO_EXTENSIONS = {'AVI', 'MP4', 'MOV', 'MKV'}
DOCUMENT_EXTENSIONS = {'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'}
AUDIO_EXTENSIONS = {'MP3', 'OGG', 'WAV', 'AMR'}
ARCHIVE_EXTENSIONS = {'ZIP', 'GZ', 'TAR'}


CATEGORIES = {'images', 'video', 'documents', 'audio', 'archives', 'unknown'}


def categorize_file(file_extension):
    '''
    The function takes a file extension and returns the name of the category.
    '''
    if file_extension in IMAGE_EXTENSIONS:
        return 'images'
    elif file_extension in VIDEO_EXTENSIONS:
        return 'video'
    elif file_extension in DOCUMENT_EXTENSIONS:
        return 'documents'
    elif file_extension in AUDIO_EXTENSIONS:
        return 'audio'
    elif file_extension in ARCHIVE_EXTENSIONS:
        return 'archives'
    else:
        return 'unknown'
    

def sort_files(folder_path, sorted_path, ignore_folders):
    '''
    The function sorts all files.
    '''
    if not os.path.exists(sorted_path):
        os.makedirs(sorted_path)

    for category in CATEGORIES:
        category_path = os.path.join(sorted_path, category)
        os.makedirs(category_path, exist_ok=True)

    for item in os.listdir(folder_path):
        if item.lower() in ignore_folders:
            continue

        item_path = os.path.join(folder_path, item)

        if os.path.isfile(item_path):
            _, file_extension = os.path.splitext(item)
            file_extension = file_extension[1:].upper()
            category = categorize_file(file_extension)
            shutil.move(item_path, os.path.join(sorted_path, category, item))
            
        elif os.path.isdir(item_path):
            sort_files(item_path, sorted_path, ignore_folders)

    if not os.listdir(folder_path) and folder_path != sorted_path:
        os.rmdir(folder_path)


def extract_archive(file_path, extract_to):
    '''
    The function takes care of unpacking a single archive.
    '''
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif tarfile.is_tarfile(file_path):
        with tarfile.open(file_path) as tar_ref:
            tar_ref.extractall(extract_to)


def unpack_archives(archives_path):
    '''
    The function iterates over all archives in the specified folder, extracts them, and deletes the original archive files.
    '''
    for archive in os.listdir(archives_path):
        archive_path = os.path.join(archives_path, archive)
        if os.path.isfile(archive_path):
            extract_to_path = os.path.splitext(archive_path)[0]
            os.makedirs(extract_to_path, exist_ok=True)
            extract_archive(archive_path, extract_to_path)
            os.remove(archive_path)


def normalize(filename):
    '''
    The function normalizes the name of a single file (without changing the extension)
    '''
    name, extension = os.path.splitext(filename)
    name = unicodedata.normalize('NFD', name)
    name = name.replace('ł', 'l').replace('Ł', 'L')
    name = name.encode('ascii', 'ignore')
    name = name.decode("utf-8")
    name = re.sub(r'\W', '_', name)
    return name + extension


def normalize_contents(folder_path):
    '''
    The function goes through all files and normalizes file and folder names.
    '''
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files + dirs:
            normalized_name = normalize(name)
            original_path = os.path.join(root, name)
            normalized_path = os.path.join(root, normalized_name)

            if original_path != normalized_path:
                shutil.move(original_path, normalized_path)


def generate_report(sorted_path):
    '''
    The function generates a report from the sorted folder.
    '''
    known_extensions = set()
    unknown_extensions = set()
    file_report = {category: [] for category in CATEGORIES}

    for category in file_report:
        category_path = os.path.join(sorted_path, category)
        for file in os.listdir(category_path):
            file_report[category].append(file)
            _, ext = os.path.splitext(file)
            ext = ext[1:].upper()
            if category == 'unknown':
                unknown_extensions.add(ext)
            else:
                known_extensions.add(ext)

    return file_report, known_extensions, unknown_extensions


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main_folder = sys.argv[1]                                               #python sort.py C:\\Users\\barto\\OneDrive\\Pulpit\\Bałagan
        sorted_folder = main_folder
        ignore_folders = {'archives', 'video', 'audio', 'documents', 'images', 'unknown'}

        sort_files(main_folder, sorted_folder, ignore_folders)

        unpack_archives(os.path.join(sorted_folder, 'archives'))

        normalize_contents(sorted_folder)

        file_report, known_exts, unknown_exts = generate_report(sorted_folder)
        print("File reports in each category:")
        for category, files in file_report.items():
            print(f"{category.capitalize()}: {len(files)} pcs.")
            file_list = []
            for file in files:
                file_list.append(file)
                # print(f" - {file}")                                           # Print a list of files with hyphens one below the other
            print(file_list)
                
        print("\nKnown file extensions:", known_exts)
        print("\nUnknown file extensions:", unknown_exts)