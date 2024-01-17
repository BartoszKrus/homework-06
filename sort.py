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


# Funcja przyjmuje rozszerzenie pliku i zwróci nazwę kategorii
def categorize_file(file_extension):
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
    

# Funkcja sortuje wszystkie pliki.
def sort_files(folder_path, sorted_path, ignore_folders):
    # image_extensions = {'JPEG', 'PNG', 'JPG', 'SVG'}
    # video_extensions = {'AVI', 'MP4', 'MOV', 'MKV'}
    # document_extensions = {'DOC', 'DOCX', 'TXT', 'PDF', 'XLSX', 'PPTX'}
    # audio_extensions = {'MP3', 'OGG', 'WAV', 'AMR'}
    # archive_extensions = {'ZIP', 'GZ', 'TAR'}

    if not os.path.exists(sorted_path):
        os.makedirs(sorted_path)

    # for category in ['images', 'video', 'documents', 'audio', 'archives', 'unknown']:
    #     category_path = os.path.join(sorted_path, category)
    #     os.makedirs(category_path, exist_ok=True)

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

            # if file_extension in IMAGE_EXTENSIONS:
            #     shutil.move(item_path, os.path.join(sorted_path, 'images', item))
            # elif file_extension in VIDEO_EXTENSIONS:
            #     shutil.move(item_path, os.path.join(sorted_path, 'video', item))
            # elif file_extension in DOCUMENT_EXTENSIONS:
            #     shutil.move(item_path, os.path.join(sorted_path, 'documents', item))
            # elif file_extension in AUDIO_EXTENSIONS:
            #     shutil.move(item_path, os.path.join(sorted_path, 'audio', item))
            # elif file_extension in ARCHIVE_EXTENSIONS:
            #     shutil.move(item_path, os.path.join(sorted_path, 'archives', item))
            # else:
            #     shutil.move(item_path, os.path.join(sorted_path, 'unknown', item))
            category = categorize_file(file_extension)
            shutil.move(item_path, os.path.join(sorted_path, category, item))
            
        elif os.path.isdir(item_path):
            sort_files(item_path, sorted_path, ignore_folders)

    if not os.listdir(folder_path) and folder_path != sorted_path:
        os.rmdir(folder_path)


# Funkcja zajmuje się rozpakowywaniem pojedynczego archiwum.
def extract_archive(file_path, extract_to):
    if zipfile.is_zipfile(file_path):
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
    elif tarfile.is_tarfile(file_path):
        with tarfile.open(file_path) as tar_ref:
            tar_ref.extractall(extract_to)


# Funcka iteruje po wszystkich archiwach w określonym folderze, rozpakowuje je i usuwa oryginalne pliki archiwum.
def unpack_archives(archives_path):
    for archive in os.listdir(archives_path):
        archive_path = os.path.join(archives_path, archive)
        if os.path.isfile(archive_path):
            extract_to_path = os.path.splitext(archive_path)[0]
            os.makedirs(extract_to_path, exist_ok=True)
            extract_archive(archive_path, extract_to_path)
            os.remove(archive_path)


# Funckja normalizuje nazwę pojedynczego pliku (bez zmiany rozszerzenia)
def normalize(filename):
    name, extension = os.path.splitext(filename)
    name = unicodedata.normalize('NFD', name)
    name = name.replace('ł', 'l').replace('Ł', 'L')
    name = name.encode('ascii', 'ignore')
    name = name.decode("utf-8")
    name = re.sub(r'\W', '_', name)
    return name + extension


# Funkcja przechodzi przez wszystkie pliki i normalizuje nazwy plików i folderów
def normalize_contents(folder_path):
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for name in files + dirs:
            normalized_name = normalize(name)
            original_path = os.path.join(root, name)
            normalized_path = os.path.join(root, normalized_name)

            if original_path != normalized_path:
                shutil.move(original_path, normalized_path)


# Generowanie raportu wg wytycznych
def generate_report(sorted_path):
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

        sort_files(main_folder, sorted_folder, ignore_folders)                  # Sortowanie plików

        unpack_archives(os.path.join(sorted_folder, 'archives'))                # Rozpakowanie plików w 'archives' oraz usuwanie plików źródłowych

        normalize_contents(sorted_folder)                                       # Zmiana znaków wg wytycznych

        file_report, known_exts, unknown_exts = generate_report(sorted_folder)  # Wygenerowanie raportu wg wytycznych
        print("File reports in each category:")
        for category, files in file_report.items():
            print(f"{category.capitalize()}: {len(files)} pcs.")
            file_list = []
            for file in files:
                file_list.append(file)
                # print(f" - {file}")                                           # Wyprintowanie listy plików od myślników jeden pod drugim
            print(file_list)
                
        print("\nKnown file extensions:", known_exts)
        print("\nUnknown file extensions:", unknown_exts)