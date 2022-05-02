import os


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ["csv"]


def clean_output_directory():
    cwd = os.path.abspath(os.path.dirname(__file__))
    path_to_output = os.path.join(cwd, "./output")
    output_files = os.listdir(path_to_output)

    if len(output_files) >= 1:
        for filename in output_files:
            file_path = os.path.join(path_to_output, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
            except Exception as e:
                print("Failed to delete %s. Reason: %s" % (file_path, e))
