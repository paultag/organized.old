#
import datetime as dt
from organized.remotes import Remote
import logging
import json

logger = logging.getLogger('organized')

API_BASE = "https://api.github.com"
PREFIX = "gh"

def gh_issue_id(user, repo, number):
    return "%s-issue-%s-%s-%s" % (
        PREFIX,
        user,
        repo,
        number
    )

def gh_milestone_id(user, repo, number):
    return "%s-milestone-%s-%s-%s" % (
        PREFIX,
        user,
        repo,
        number
    )

def parse_time(time):
    if time is None:
        return None

    time = dt.datetime.strptime( time, "%Y-%m-%dT%H:%M:%SZ" )
    return time


class GitHub(Remote):

    def __init__(self, user, repo):
        logger.info('create github object.')
        self.user = user
        self.repo = repo

    def _hit_api(self, url):
        payload = json.loads(self._get_api_response(url))
        return payload

    def _fetch_bugs(self, **kwargs):
        flags = self._safe_urlencode(kwargs)

        user, repo = self.user, self.repo
        url = "%s/repos/%s/%s/issues?%s" % (
            API_BASE,
            user,
            repo,
            flags
        )
        data = self._hit_api(url)
        return data

    def _fetch_milestones(self, **kwargs):
        flags = self._safe_urlencode(kwargs)

        user, repo = self.user, self.repo
        url = "%s/repos/%s/%s/milestones?%s" % (
            API_BASE,
            user,
            repo,
            flags
        )
        data = self._hit_api(url)
        return data

    def _update(self):
        def update_issues(**kwargs):
            logger.info("fetching issues")
            issues = self.get_bugs_for(**kwargs)
            count = 0
            issue_migration = {
                "assignee": "owner",
                "labels": "tags",
                "user": "reporter"
            }
            for issue in issues:
                eye_dee = gh_issue_id(
                    self.user,
                    self.repo,
                    issue['number']
                )
                for mig in issue_migration:
                    issue[issue_migration[mig]] = issue[mig]
                    del(issue[mig])
                issue['_id'] = eye_dee

                if issue['milestone'] != None:
                    real_milestone = gh_milestone_id(
                        self.user,
                        self.repo,
                        issue['milestone']['number'])
                    issue['_milestone'] = real_milestone
                else:
                    issue['_milestone'] = None

                for field in [ 'created_at', 'closed_at', 'updated_at' ]:
                    issue[field] = parse_time(issue[field])

                self.save_issue(issue)
                count += 1
            return count

        def update_milestones(**kwargs):
            logger.info("fetching milestones")
            milestones = self.get_milestones_for(**kwargs)
            count = 0
            for milestone in milestones:
                eye_dee = gh_milestone_id(
                    self.user,
                    self.repo,
                    milestone['number']
                )
                milestone['_id'] = eye_dee

                for field in [ 'created_at', 'due_on' ]:
                    milestone[field] = parse_time(milestone[field])

                self.save_milestone(milestone)
                count += 1
            return count

        for status in [ 'open', 'closed' ]:
            ret_issues = -1
            ret_milestones = -1

            n = 1
            while ret_issues != 0:
                logger.info("Page %s" % ( n ))
                ret_issues = update_issues(
                    state=status,
                    page=n)
                n += 1

            n = 1
            while ret_milestones != 0:
                logger.info("Page %s" % ( n ))
                ret_milestones = update_milestones(
                    state=status,
                    page=n)
                n += 1

        self.ping_project()
