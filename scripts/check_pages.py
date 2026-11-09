"""Let gallery checks succeed when the account cannot yet enable Pages."""
import json
import os
import urllib.error
import urllib.request

request = urllib.request.Request(
    'https://api.github.com/repos/' + os.environ['GITHUB_REPOSITORY'] + '/pages',
    headers={'Authorization': 'Bearer ' + os.environ['GITHUB_TOKEN'],
             'Accept': 'application/vnd.github+json', 'User-Agent': 'fable-gallery'},
)
try:
    with urllib.request.urlopen(request, timeout=30) as response:
        enabled = json.load(response).get('build_type') == 'workflow'
except urllib.error.HTTPError as error:
    if error.code != 404:
        raise
    enabled = False
with open(os.environ['GITHUB_OUTPUT'], 'a') as output:
    output.write('enabled=' + str(enabled).lower() + '\n')
if not enabled:
    message = ('Pages is not enabled with GitHub Actions. Gallery screenshots and checks '
               'will complete, but deployment is skipped. Enable Pages with Actions on a '
               'plan that supports private repositories, then rerun this workflow.')
    print(message)
    with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as summary:
        summary.write(message + '\n')
