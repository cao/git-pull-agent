#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""A simple Git webhook daemon to auto pull a repository on a push event.

Works with
- Github
- Gitlab
"""

from twisted.application import internet, service
from twisted.web import server, resource
from twisted.web.resource import ErrorPage

from git import Repo

import json
import os

__author__ = "Kevin Borgolte <cao@cao.vc>"
__description__ = """Simple Git webhook daemon to auto pull on push."""
__version__ = "1.0.0"


def make_service(options):
    class PullAgent(resource.Resource):
        def getChildWithDefault(self, name, request):
            return self

        def render_POST(self, request):
            if not options['path'] or not options['reference']:
                msg = "The Git pull agent is not configured properly"
                return ErrorPage(405, "Error", msg)

            # Workaround for proper Python 2/3 support
            data = json.loads(request.content.read().decode())
            git = Repo(options['path'])

            if git.is_dirty():
                msg = "Repository '{}' has local changes"
                return ErrorPage(409, "Error", msg.format(options['path']))

            if 'repository' not in data:
                return ErrorPage(400, "Error", "Invalid webhook source")

            urls = []
            for key in ['git_http_url', 'git_ssh_url',      # Gitlab
                        'git_url', 'ssh_url', 'http_url']:  # Github
                if key in data['repository']:
                    urls.append(data['repository'][key])

            remote = [r for r in git.remotes if r.url in urls]

            if not remote:
                msg = "Repository '{}' has no remotes"
                return ErrorPage(400, "Error", msg.format(options['path']))

            remote = remote[0]
            remote.pull(options['reference'], progress=None)
            return "Repository '{}' updated".format(options['path'])

    return internet.TCPServer(int(options['port']), server.Site(PullAgent()))


application = service.Application("Git webhook pull agent")
service = make_service({'port': os.environ.get('GIT_PULL_AGENT_PORT', 10000),
                        'path': os.environ.get('GIT_PULL_AGENT_DIR', "."),
                        'reference':
                        os.environ.get('GIT_PULL_AGENT_REF',
                                       "refs/heads/master")})
service.setServiceParent(application)
