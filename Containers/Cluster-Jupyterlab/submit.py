#!/usr/bin/env python3

# bash prograamming example url: https://www.coursera.org/learn/introduction-high-performance-computing/programming/PnDt1/lab

import requests
import json
import sys
from configparser import ConfigParser
from pathlib import Path
import os
import shutil

# Proxied to www.coursera.org/api/workspaceSubmissions.v1 via gateway.
COURSERA_SUBMISSION_URL = 'https://hub.coursera-apps.org/api/workspaceSubmissions.v1'
BATCH_CREATE_ACTION = '?action=createBatch'

honor_code = """
I understand that submitting work that isn’t my own may result in permanent failure of this course or deactivation of my Coursera account.

You can learn more about Coursera's Honor Code at https://learner.coursera.help/hc/articles/209818863
"""


def submit(submission_token, schema_name):
    try:
        response = requests.post(
            COURSERA_SUBMISSION_URL,
            data=json.dumps({'token': submission_token, 'schemaName': schema_name}),
            timeout=10)
    except Exception as err:
        return 'Failed to execute submission request: {}'.format(err)

    if response.status_code == 201:
        print(response.json()['elements'][0]['message'])
    elif response.status_code == 200:
        print(response.json()['message'])
    elif response.status_code < 500:
        print('Bad request:\n{}'.format(response.json()))
    else:
        error_id, = re.findall(
            'This exception has been logged with id <strong>(.+)</strong>',
            response.text)
        print('Unexpected server error logged with id {}. '.format(error_id) +
              'Please contact Coursera support.')


file_name = sys.argv[1]
token = sys.argv[2]

# there are 2 dirs week-* and week-*-ro, only the first one will be used
project_dirs = Path.home() / Path('projects')
working_dir = [w for w in project_dirs.glob('week*') if not w.name.endswith("-ro")]

# read the configuration file
os.chdir(working_dir[0])
config = ConfigParser()
config.read('.config.ini')
config_section = 'lab'
course_slug = config.get(config_section, 'course_slug')
graded_item_id = config.get(config_section, 'graded_item_id')
schema_name = config.get(config_section, 'schema_name')
part_id = config.get(config_section, 'part_id')
submission_file_name = config.get(config_section, 'submission_file_name')

submission_page_url = "https://www.coursera.org/learn/" + course_slug + "/programming/" + graded_item_id

constructed_schema_name = course_slug + '~' + graded_item_id + part_id

# Error if the file is not the submission_file_name
if os.path.basename(file_name) != submission_file_name:
    print("Your file: ", file_name, " does not have the correct file name: The name should be ",
          submission_file_name, ". Please try again.")
    sys.exit("Submission error: Wrong file name")

print("Submitting your file: ", submission_file_name)
print(honor_code)

submit(token, schema_name)
