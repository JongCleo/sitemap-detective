import os
from helper_functions import __prepend_http

OUTPUT_FILE = "medium_test_107ffc7d38e241258e74c79f22107b9c.csv"
ORIGINAL_FILE = "medium_test.csv"
cwd = os.path.abspath(os.path.dirname(__file__))


with open(os.path.join(cwd, "../uploads", ORIGINAL_FILE), "r") as f:
    original_urls = [__prepend_http(line) for line in f.read().splitlines()]

with open(os.path.join(cwd, "../output", OUTPUT_FILE), "r") as f:
    output_urls = [row.split(",")[0] for row in f]

print(list(set(original_urls) ^ set(output_urls)))
