#
from organized.remotes import Remote
import logging
import json

logger = logging.getLogger('organized')

API_BASE = "https://api.github.com"
PREFIX = "gh"

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
        logger.info("fetching open issues")
        issues = self.get_bugs_for(state='open')
        logger.info("fetching closed issues")
        issues += self.get_bugs_for(state='closed')

        issue_migration = {
            "assignee": "owner",
            "labels": "tags",
            "user": "reporter"
        }

        for issue in issues:
            eye_dee = "%s-issue-%s-%s-%s" % (
                PREFIX,
                self.user,
                self.repo,
                issue['number']
            )

            for mig in issue_migration:
                issue[issue_migration[mig]] = issue[mig]
                del(issue[mig])

            issue['_id'] = eye_dee
            self.save_issue(issue)

        logger.info("fetching open milestones")
        milestones = self.get_milestones_for(state='open')
        logger.info("fetching closed milestones")
        milestones += self.get_milestones_for(state='closed')

        for milestone in milestones:
            eye_dee = "%s-milestone-%s-%s-%s" % (
                PREFIX,
                self.user,
                self.repo,
                milestone['number']
            )
            milestone['_id'] = eye_dee
            self.save_milestone(milestone)

        self.ping_project()
