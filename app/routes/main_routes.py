from flask import Blueprint, render_template, request


main_bp = Blueprint("main", __name__)


@main_bp.get("/")
def landing():
    return render_template("pages/landing.html")


@main_bp.get("/stylist")
def stylist():
    return render_template("pages/stylist.html")


@main_bp.get("/results")
def results():
    # Results are primarily loaded via the API; this page hosts the UI shell.
    return render_template("pages/results.html")


@main_bp.get("/explore")
def explore():
    return render_template("pages/explore.html")


@main_bp.get("/saved")
def saved():
    return render_template("pages/saved.html")

