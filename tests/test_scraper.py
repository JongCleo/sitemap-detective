from src.scraper import Job
from src.helper_functions import clean_output_directory
import os


def test_small_sample():
    # Arrange
    clean_output_directory()
    filename = "small_test.csv"
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]

    job = Job(filename, term_list, page_list)

    # Act
    job.process_file()

    # Assert
    cwd = os.path.abspath(os.path.dirname(__file__))
    output_dir = os.path.join(cwd, "../src/output")
    output_file = [
        f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))
    ][0]

    with open(os.path.join(output_dir, output_file)) as f:
        ## confirm that the headers is correct
        lines = f.read().splitlines()
        for line in lines:
            peek_value = line.split(",")[0]

            if peek_value == "sites":
                assert (
                    "sites,term_connect,term_integration,page_connect,page_integration"
                    == line
                )
            elif peek_value == "http://www.hublio.com":
                assert "http://www.hublio.com,True,False,False,False" == line
            elif peek_value == "http://www.atera.com":
                assert "http://www.atera.com,True,True,True,True" == line
            else:
                pass
