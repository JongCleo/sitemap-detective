from src.scraper import process_file, clean_output_directory, Job
import os


def test_small_sample():
    # Arrange
    clean_output_directory()
    filename = "small_test.csv"
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]

    job = Job(filename, term_list, page_list)

    # Act
    process_file(job)

    # Assert
    cwd = os.path.abspath(os.path.dirname(__file__))
    output_dir = os.path.join(cwd, "../output")
    output_file = [
        f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))
    ][0]

    with open(os.path.join(output_dir, output_file)) as f:
        ## confirm that the headers is correct
        headers = f.readline().replace("\n", "")
        hublio = f.readline().replace("\n", "")
        attera = f.readline().replace("\n", "")
        expected_headers = (
            "sites,term_connect,term_integration,page_connect,page_integration"
        )
        expected_hublio = "http://www.hublio.com,True,False,False,False"
        expected_attera = "http://www.atera.com,True,True,True,True"
        assert expected_headers == headers
        assert expected_hublio == hublio
        assert expected_attera == attera
