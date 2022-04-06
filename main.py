import logging
from flask import Flask, render_template
from google.cloud import storage

from fcms.common import get_db, get_env_var

logger = logging.getLogger("fcms")

app = Flask("fcms")


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"


@app.route("/cases/<case_key>")
def case_details(case_key):
    db = get_db()
    case_obj = db["cases"].find_one({"case_key": int(case_key)})
    logger.debug(f"{case_obj=}")
    return render_template("case_details.html", case_obj=case_obj)


# Route for case files
@app.route("/cases/<case_key>/files")
def case_files(case_key):
    # Fetch file list from bucket
    CLOUD_BUCKET = get_env_var("CLOUD_BUCKET")
    storage_client = storage.Client()
    storage_bucket = storage.Bucket(storage_client, CLOUD_BUCKET)
    case_files = storage_bucket.list_blobs(prefix=case_key)
    return render_template("case_files.html", case_files=case_files)


# Route for case history
@app.route("/cases/<case_key>/history")
def case_history(case_key):
    db = get_db()
    case_obj = db["cases"].find_one({"case_key": case_key})
    return render_template("case_history.html", case=case_obj)
