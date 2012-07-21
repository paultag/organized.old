# Copyright (c) Paul Tagliamonte <paultag@debian.org>, 2012 under the terms
# and conditions of the Expat license, a copy of which should be given to you
# with the source of this application.

from flask import Flask, render_template, request

from organized.burndown import generate_daily_bugs
from organized.db import db

app = Flask(__name__)

@app.route("/")
def index():
    projects = db.projects.find()

    return render_template('index.html', **{
        "projects": projects
    })

@app.route("/project/<project>/")
@app.route("/project/<project>/<milestone>")
def project(project=None, milestone=None):
    milestones = db.milestones.find({"_project": project})

    return render_template('project.html', **{
        "project": project,
        "milestone": milestone,
        "milestones": milestones
    })

@app.route("/csv/issues/<project>")
@app.route("/csv/issues/<project>/<milestone>")
def csv_project(project=None, milestone=None):
    total = 0
    totals = {}
    buf = "week,bugcount,closed,opened\n"

    kwargs = {}
    if not milestone is None:
        kwargs['_milestone'] = milestone

    (keys, values) = generate_daily_bugs(project, **kwargs)
    for key in keys:
        closed, opened = values[key]
        total += opened
        total -= closed
        buf += "%s,%s,%s,%s\n" % (
            key,
            total,
            closed,
            opened
        )
    return buf

if __name__ == "__main__":
    app.debug = True
    app.run()
