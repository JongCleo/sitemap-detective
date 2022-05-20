from app.scraper import process_job
from tests import helpers
from app.models import Job, User
from depot.manager import DepotManager
import os


def test_small_sample(db):
    # Arrange

    user = User(email="user@test.com")
    db.session.add(user)
    db.session.commit()

    input_file = helpers.load_binary_file("small_test.csv")
    term_list = ["connect", "integration"]
    page_list = ["connect", "integration"]

    job = Job(
        user_id=user.id, input_file=input_file, term_list=term_list, page_list=page_list
    )
    db.session.add(job)
    db.session.commit()

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
