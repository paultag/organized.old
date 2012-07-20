# Copyright (c) Paul Tagliamonte <paultag@debian.org>, 2012 under the terms
# and conditions of the Expat license, a copy of which should be given to you
# with the source of this application.

from flask import Flask, render_template, request
from organized.db import db

app = Flask(__name__)

@app.route("/")
def index():
    projects = db.projects.find({})

    return render_template('index.html', **{
        "projects": projects
    })

@app.route("/project/<project>")
def project(project=None):
    milestones = db.milestones.find({"_project": project})

    return render_template('project.html', **{
        "milestones": milestones
    })

@app.route("/project/<project>/<milestone>")
def milestone(project=None, milestone=None):
    issues = db.issues.find({"_milestone": milestone})

    return render_template('milestone.html', **{
        "issues": issues
    })

if __name__ == "__main__":
    app.debug = True
    app.run()
