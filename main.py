import os
import time

# Каталог з текстовими файлами
TEXTS_DIR = "texts"

# Ключові слова для пошуку
KEYWORDS = ["слово1", "слово2", "слово3"]


# Отримання списку файлів
def get_file_list(directory):
    """
    Retrieves a list of all .txt files in the specified directory.

    Args:
        directory (str): The path to the directory to search for .txt files.

    Returns:
        list: A list of file paths to .txt files found in the directory.
    """
    files = []
    for filename in os.listdir(directory):
        if filename.endswith(".txt"):
            files.append(os.path.join(directory, filename))
    return files


# ============================

import threading


def search_keywords_in_files(file_list, keywords, result_dict, lock):
    """
    Searches for specified keywords in a list of files and updates a shared result dictionary.

    Args:
        file_list (list of str): List of file paths to search for keywords.
        keywords (list of str): List of keywords to search for in the files.
        result_dict (dict): Shared dictionary to store the search results.
                            Keys are keywords and values are lists of file paths where the keywords were found.
        lock (threading.Lock): Lock object to ensure synchronized access to the shared result dictionary.

    Raises:
        Exception: If there is an error reading any of the files, an exception is caught and an error message is printed.
    """
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
    """
    Perform a multithreaded search for keywords in a list of files.
    This function divides the list of files into chunks and assigns each chunk to a separate thread.
    Each thread searches for the specified keywords in its assigned files and updates a shared result
    dictionary with the findings. The function waits for all threads to complete before printing the
    results and the execution time.
    Returns:
        dict: A dictionary where keys are keywords and values are lists of files in which the keywords were found.
    """
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
    # Форматований вивід результатів
    print("\nРезультати багатопотокового пошуку:")
    for keyword, files in result_dict.items():
        print(f"\nКлючове слово '{keyword}' знайдено в файлах:")
        if files:
            for file in files:
                print(f" - {file}")
        else:
            print(" - Не знайдено")
    print(f"\nЧас виконання: {end_time - start_time:.6f} секунд")

    return result_dict


# ============================

import multiprocessing


def search_keywords_in_files_mp(file_list, keywords, queue):
    """
    Searches for specified keywords in a list of files and stores the results in a multiprocessing queue.

    Args:
        file_list (list of str): List of file paths to search.
        keywords (list of str): List of keywords to search for in the files.
        queue (multiprocessing.Queue): Queue to store the search results.

    Returns:
        None: The results are put into the provided queue. Each keyword maps to a list of file paths where the keyword was found.

    Raises:
        Exception: If there is an error reading any of the files, an error message is printed.
    """
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
    """
    Perform a multiprocess search for keywords in a list of files.
    This function divides the list of files into chunks and assigns each chunk to a separate process.
    Each process searches for the specified keywords in its assigned files and puts the results into a queue.
    After all processes have completed, the results are collected from the queue and aggregated.
    Returns:
        dict: A dictionary where keys are keywords and values are lists of files in which the keywords were found.
    Note:
        - The number of processes is fixed at 4.
        - The function prints the results and execution time to the console.
    """
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
