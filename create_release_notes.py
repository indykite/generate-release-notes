import re
import os
import argparse
from patterns import *
from datetime import datetime


class ReleaseNoteGenerator:

    def _parse_changelog(self):
        parsed_changelog = {'release_url': os.environ['REPO_RELEASE_URL'],
                            'release_date': self._format_date(os.environ['RELEASE_DATE']),
                            'release_version': os.environ['TAG_NAME'], 'repo_name': os.environ['REPO_NAME'],
                            'repo_url': os.environ['REPO_URL'], 'changes': []}

        changelog_lines = [
            line for line in os.environ['CHANGELOG_BODY'].splitlines() if line]
        for line in changelog_lines:
            # e.g. ### Bug Fixes. Do not match release headline
            if line.startswith(change_headline_start) and not re.match(release_headline_pattern, line):
                parsed_changelog['changes'].append(
                    {'change_headline': line.replace(change_headline_start, '', 1)})
                # the commits are grouped under the changes headline
                parsed_changelog['changes'][-1]['commits'] = []
            # Add commit messages to the last change headline
            elif line.startswith(commit_message_start):
                commit_message = line.replace(commit_message_start, '', 1)
                commit_hash = re.search(commit_pattern, line).group(1)
                parsed_changelog['changes'][-1]['commits'].append(
                    {'message': commit_message, 'hash': commit_hash})
        return parsed_changelog

    def _format_date(self, input_date):
        output_date = datetime.strptime(
            input_date, github_date_format).strftime(output_date_format)

        return output_date

    def _load_file(self, path):
        with open(path, 'r') as file:
            content = file.readlines()
        return content

    def _prepend_release_note(self, path, file_content, parsed_changelog):
        # iterates file content and when finds delimeter_pattern, writes the release note. Then writes rest of the file
        with (open(path, 'w')) as file:
            if not file_content:
                # file is empty, write release note at the top
                self._write_release_note(
                    file, parsed_changelog, include_headline=True)
            else:
                found_delimiter = False
                for line in file_content:
                    if not found_delimiter and re.match(delimeter_pattern, line):
                        self._write_release_note(file, parsed_changelog)
                        file.write(line)
                        found_delimiter = True
                    else:
                        file.write(line)
                if not found_delimiter:
                    # delimeter_pattern not found in the file and file not empty, append release note
                    self._write_release_note(
                        file, parsed_changelog, include_headline=True)

    def _write_release_note(self, file, parsed_changelog, include_headline=False):
        if include_headline:
            file.write(f"{file_headline}\n\n")
            file.write(f"{section_delimeter}\n")
        file.write(
            f"<!--Release note {parsed_changelog['release_version']}!-->\n")
        file.write(
            f"### {parsed_changelog['release_date']} [{parsed_changelog['repo_name']}]({parsed_changelog['repo_url']})\n")
        file.write(
            f"* #### [{parsed_changelog['release_version']}]({parsed_changelog['release_url']})\n\n")
        for change in parsed_changelog['changes']:
            file.write(f"#### {change['change_headline']}\n\n")
            for commit in change['commits']:
                file.write(f"* {commit['message']}\n\n")
        file.write(f"{section_delimeter}\n\n")

    def _verify_parsed_changelog(self, parsed_changelog):
        for key, value in parsed_changelog.items():
            if not value:
                raise ValueError(
                    f"Parsing changelog failed. All values must be filled in. Value for key '{key}' is missing.")

    def _output_env_variable(self, name, value):
        with open(os.environ['GITHUB_OUTPUT'], 'a') as output_file:
            print(f'{name}={value}', file=output_file)

    def generate(self):
        parsed_changelog = self._parse_changelog()
        self._verify_parsed_changelog(parsed_changelog)
        # output repo_name and release_version as env to be used later in workflow
        self._output_env_variable(
            'REPO_NAME_RELEASE', f"{parsed_changelog['repo_name']} {parsed_changelog['release_version']}")

        return parsed_changelog

    def update_release_notes(self, release_notes_path, parsed_changelog):
        file_content = self._load_file(release_notes_path)
        self._prepend_release_note(
            release_notes_path, file_content, parsed_changelog)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate release notes')
    parser.add_argument('--release_notes_path', type=str,
                        help='Path to release notes file', required=True)
    args = parser.parse_args()

    ReleaseNote = ReleaseNoteGenerator()
    parsed_changelog = ReleaseNote.generate()
    ReleaseNote.update_release_notes(args.release_notes_path, parsed_changelog)
