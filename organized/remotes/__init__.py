from organized.db import db

import logging
import urllib2
import urllib

import datetime as dt

logger = logging.getLogger('organized')

class Remote(object):
    def _fetch_bugs(self, project):
        raise NotImplemented("Sorry.")

    def _get_api_response(self, url):
        f = urllib2.urlopen(url)
        return f.read()

    def _safe_urlencode(self, dic):
        return urllib.urlencode(dic)

    def update(self):
        logger.info('updating')
        return self._update()

    def project(self, project):
        logger.info('setting project to %s' % project)
        self._project = project

    def get_bugs_for(self, **kwargs):
        logger.info('fetching bugs')
        return self._fetch_bugs(**kwargs)

    def get_milestones_for(self, **kwargs):
        logger.info('fetching milestones')
        return self._fetch_milestones(**kwargs)

    def save_issue(self, issue):
        # ok, slight mangle.
        issue['_project'] = self._project
        logger.info('adding issue %s' % issue['_id'])
        db.issues.update(
            {"_id": issue['_id']},
            issue,
            True,
            safe=True)

    def ping_project(self):
        # slight mangle
        project = {
            "name": self._project,
            "ping": dt.datetime.now()
        }
        db.projects.update(
            {"_id": self._project},
            project,
            True,
            safe=True)

    def save_milestone(self, milestone):
        # ok, slight mangle.
        milestone['_project'] = self._project
        logger.info('adding milestone %s' % milestone['_id'])
        db.milestones.update({"_id": milestone['_id']},
                             milestone,
                             True,
                             safe=True)
