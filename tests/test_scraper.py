from src.scraper import process_file, clean_output_directory, Job
import cProfile
import pstats


def test_scraper():
    # Arrange
    clean_output_directory()
    filename = "test.csv"
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]

    job = Job(filename, term_list, page_list)

    # Act
    process_file(job)

    # Assert
