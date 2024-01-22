import os
import asana
from asana.rest import ApiException
from pprint import pprint

# Retrieve Asana access token from GitHub Secrets
access_token = os.getenv('ASANA_TOKEN')
gid = "1200084223367052"
projects = "1206398263390118"
issue_assignee = os.getenv('ISSUE_ASSIGNEE') or None

# Configure Asana client
configuration = asana.Configuration()
configuration.access_token = access_token
api_client = asana.ApiClient(configuration)
tasks_api_instance = asana.TasksApi(api_client)

# Get issue information from GitHub event
issue_title = os.getenv('ISSUE_TITLE')
issue_body = os.getenv('ISSUE_BODY')

body = {
    "data": {
        "gid": gid, 
        "name": issue_title,
        "notes": issue_body,
        "projects": [projects],
        "assignee": issue_assignee,
    }
}
opts = {}

try:
    # Create Asana task
    task = tasks_api_instance.create_task(body, opts)
    pprint(task)
except ApiException as e:
    print("Exception when calling TasksApi->create_task: %s\n" % e)
