from app.scraper import process_job
from app.models import Job, User
from depot.manager import DepotManager
import os


def test_small_sample(job):

    # Act
    process_job(job.id)

    # Assert
    output_file_path = Job.query.get(job.id).output_file.path
    output_file = DepotManager.get_file(output_file_path)
    for line in output_file.read().decode("UTF-8").splitlines():
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
    output_file.close()
