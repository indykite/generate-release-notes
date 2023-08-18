# REGEX PATTERNS
# release headline. Contains link to compare releases and date.
release_headline_pattern = r'^#{2,3} (\[[0-9]+\.[0-9]+\.[0-9]+\].*) \([0-9]{4}-[0-9]{2}-[0-9]{2}\)'
# extract commit from github url
commit_pattern = r'https:\/\/.*\/commit\/([0-9a-z]*)'
delimeter_pattern = r'^\<\!\-\-Release note v[0-9]+\.[0-9]+\.[0-9]+\!\-\-\>$'

# CHANGELOG PATTERNS
commit_message_start = '* '
change_headline_start = '### '

# RELEASE NOTE PATTERNS
file_headline = '# Changelog'
section_delimeter = '***'

# DATE FORMATS
github_date_format = '%Y-%m-%dT%H:%M:%SZ'
output_date_format = '%d %B %Y'
