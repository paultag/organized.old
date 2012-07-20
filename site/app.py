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

@app.route("/project/<project>")
def project(project=None):
    milestones = db.milestones.find({"_project": project})

    return render_template('project.html', **{
        "project": project,
        "milestones": milestones
    })

@app.route("/csv/issues/<project>")
def csv_project(project=None):
    total = 0
    totals = {}
    buf = "week,bugcount,closed,opened\n"

    (keys, values) = generate_daily_bugs(project)
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

@app.route("/project/<project>/<milestone>")
def milestone(project=None, milestone=None):
    issues = db.issues.find({"_milestone": milestone})

    return render_template('milestone.html', **{
        "issues": issues
    })

if __name__ == "__main__":
    app.debug = True
    app.run()
