import os
import time

# Каталог з текстовими файлами
TEXTS_DIR = "texts"

# Ключові слова для пошуку
KEYWORDS = ["слово1", "слово2", "слово3"]


# Отримання списку файлів
def get_file_list(directory):
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            files.append(os.path.join(directory, filename))
    return files


# ============================

import threading


def search_keywords_in_files(file_list, keywords, result_dict, lock):
    local_result = {keyword: [] for keyword in keywords}
    for file_path in file_list:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for keyword in keywords:
                    if keyword in content:
                        local_result[keyword].append(file_path)
        except Exception as e:
            print(f"Помилка при обробці файлу {file_path}: {e}")
    # Синхронізований доступ до загального словника
    with lock:
        for keyword in keywords:
            result_dict[keyword].extend(local_result[keyword])


def multithreaded_search():
    start_time = time.time()

    files = get_file_list(TEXTS_DIR)
    num_threads = 4  # Кількість потоків
    files_per_thread = len(files) // num_threads
    threads = []
    result_dict = {keyword: [] for keyword in KEYWORDS}
    lock = threading.Lock()

    for i in range(num_threads):
        start_index = i * files_per_thread
        end_index = (i + 1) * files_per_thread if i != num_threads - 1 else len(files)
        thread_files = files[start_index:end_index]
        t = threading.Thread(
            target=search_keywords_in_files,
            args=(thread_files, KEYWORDS, result_dict, lock),
        )
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()

    print("\nРезультати багатопотокового пошуку:")
    for keyword, files in result_dict.items():
        print(f"\nКлючове слово '{keyword}' знайдено в файлах:")
        if files:
            for file in files:
                print(f" - {file}")
        else:
            print(" - Не знайдено")
    print(f"\nЧас виконання: {end_time - start_time:.6f} секунд")
    print(f"\n---------------------------------")

    return result_dict


# ============================

import multiprocessing


def search_keywords_in_files_mp(file_list, keywords, queue):
    local_result = {keyword: [] for keyword in keywords}
    for file_path in file_list:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                for keyword in keywords:
                    if keyword in content:
                        local_result[keyword].append(file_path)
        except Exception as e:
            print(f"Помилка при обробці файлу {file_path}: {e}")
    queue.put(local_result)


def multiprocess_search():
    start_time = time.time()

    files = get_file_list(TEXTS_DIR)
    num_processes = 4  # Кількість процесів
    files_per_process = len(files) // num_processes
    processes = []
    result_dict = {keyword: [] for keyword in KEYWORDS}
    queue = multiprocessing.Queue()

    for i in range(num_processes):
        start_index = i * files_per_process
        end_index = (
            (i + 1) * files_per_process if i != num_processes - 1 else len(files)
        )
        process_files = files[start_index:end_index]
        p = multiprocessing.Process(
            target=search_keywords_in_files_mp, args=(process_files, KEYWORDS, queue)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Збір результатів з черги
    while not queue.empty():
        local_result = queue.get()
        for keyword in KEYWORDS:
            result_dict[keyword].extend(local_result[keyword])

    end_time = time.time()

    print("\nРезультати багатопроцесорного пошуку:")
    for keyword, files in result_dict.items():
        print(f"\nКлючове слово '{keyword}' знайдено в файлах:")
        if files:
            for file in files:
                print(f" - {file}")
        else:
            print(" - Не знайдено")
    print(f"\nЧас виконання: {end_time - start_time:.6f} секунд")
    print(f"\n---------------------------------")

    return result_dict


# ============================

if __name__ == "__main__":
    print("Виберіть режим роботи:")
    print("1. Багатопотоковий")
    print("2. Багатопроцесорний")
    mode = input("Ваш вибір (1 або 2): ")
    if mode == "1":
        multithreaded_search()
    elif mode == "2":
        multiprocess_search()
    else:
        print("Невірний вибір")
