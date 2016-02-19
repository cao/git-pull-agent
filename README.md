# Git Pull Agent

This is a *very* simple Twisted daemon that pulls a specific reference for a
repository after having received a push event via a webhook.

Possible use cases include base repositories for configuration management and
then restarting a specific service or in the meta-case (ansible/salt/puppet
configuration) to deploy the configuration automatically.

This daemon eliminates the first step of having to pull new changes from a
remote, which means that you should do whatever you want to do through a Git
hook afterwards (and possibly are doing already).

At this point, it supports only GitLab and GitHub webhooks.

Naturally, it might require a deployment key to pull from your repository if
your repository is not publicly accessible.


## Install Dependencies

Python 3.5.1 is supported, but it was also working for Python 2.7 at one
point in the past. Therefore, I do not expect it to not work there also.

Simply set up a Python 3.5.1 virtual environment and install the requirements:

    pip install -r requirements.txt


## Configure It

To configure it, simply set up to three environment variables:

    GIT_PULL_AGENT_PORT=12345
    GIT_PULL_AGENT_DIR=/path/to/git/repository
    GIT_PULL_AGENT_REF=refs/heads/master

Correspondingly, the defaults for those variables are:

    GIT_PULL_AGENT_PORT=10000
    GIT_PULL_AGENT_DIR=.
    GIT_PULL_AGENT_REF=refs/heads/master


## Run It

It should be run via:

    twistd -ny git-pull-agent.tac -pidfile /run/git-pull-agent.pid


## Notes

Right now, it has practically no safe-guards whatsoever for events that are
not well-formed and might in fact break easily. Hence: do not use it on
untrusted networks (aka. the Internet) unless you understand what can break
and what not.

It will, however, *not* pull from remotes it has never seen. It will always
sanitize remotes against ones that exist locally.
