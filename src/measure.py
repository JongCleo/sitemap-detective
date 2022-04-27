
from scraper import process_file, Job
from helper_functions import clean_output_directory
import time

if __name__ == "__main__":
    clean_output_directory()
    filename = "small_test.csv"
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]

    file_job = Job(filename, term_list, page_list)

    # Pool
    start_time = time.time()
    process_file(file_job)
    end_time = time.time()
    print("Multicore done in {:.4f} seconds".format(end_time - start_time))
    # Multicore done in 27.6035 seconds