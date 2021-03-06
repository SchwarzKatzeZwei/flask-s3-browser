import os
import subprocess
import tempfile
import urllib.parse
import zipfile

from flask import Flask, Response, flash, redirect, render_template, request, session, url_for
from flask_bootstrap import Bootstrap

from config import PASSWORD_LENGTH, S3_BUCKET
from db_access import TinyDBAC
from filters import datetimeformat, file_type, get_archive_pass, get_expire, path_parent
from resources import get_bucket, get_s3_client
from util import check_already_insert_db, dir_file_filter, make_tag, pass_gen

app = Flask(__name__)
Bootstrap(app)
app.secret_key = "secret"
app.jinja_env.filters["datetimeformat"] = datetimeformat
app.jinja_env.filters["file_type"] = file_type
app.jinja_env.filters["path_parent"] = path_parent
app.jinja_env.filters["get_archive_pass"] = get_archive_pass
app.jinja_env.filters["expire"] = get_expire

dbac = TinyDBAC()


@app.route("/", methods=["GET", "POST"])
def index():
    session["bucket"] = S3_BUCKET
    return redirect(url_for("files"))


@app.route("/files", methods=["GET", "POST"])
def files():
    my_bucket = get_bucket()

    if request.method == "GET":
        if (key := request.args.get("export_path")) is None:
            key = ""

    else:  # POST
        key = request.form["key"]

    summaries = my_bucket.objects.filter(Prefix=key)
    summaries = dir_file_filter(summaries, key=key)

    return render_template("files.html", my_bucket=my_bucket, files=summaries, path=key, gen_passwd=pass_gen(PASSWORD_LENGTH))


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    export_path = request.form["export-path"]
    expiration = request.form["expiration"]
    encode_type = request.form["encode"]

    # ćĺšćé
    set_tag = make_tag(ExpireTag=expiration)

    if file.filename == "":
        flash("No file selected.", "alert alert-danger")
        return redirect(url_for("files", export_path=export_path))

    my_bucket = get_bucket()

    # Archive
    if request.form.get("archive") is not None:
        password = request.form["password-text"]
        with tempfile.TemporaryDirectory(prefix="tmp_src", dir=".") as dirpath_src:
            # ă˘ăăă­ăźăăăĄă¤ăŤăäżĺ­
            file.save(os.path.join(dirpath_src, file.filename))

            with tempfile.TemporaryDirectory(prefix="tmp_dst", dir=".") as dirpath_dst:
                if encode_type == "CP932":
                    # CP932ĺ¤ć
                    command = ["/usr/bin/convmv", "-r", "-f", "utf8", "-t", "cp932", f"{dirpath_src}/{file.filename}", "--notest"]
                    subprocess.run(command)

                # ăăšăŻăźăäťăzipăăˇă§ăŤăšăŻăŞăăă§çć
                command = [
                    "/usr/bin/zip",
                    "-r",
                    "-P",
                    f"\'{password}\'",
                    f"../{dirpath_dst}/pass_{os.path.splitext(file.filename)[0]}.zip",
                    "./*",
                ]
                command = " ".join(command)
                print(command)
                subprocess.run(command, cwd=f"{dirpath_src}", shell=True)

                # S3ăŤă˘ăăă­ăźă
                my_bucket.upload_file(
                    f"{dirpath_dst}/pass_{os.path.splitext(file.filename)[0]}.zip",
                    f"{export_path}pass_{os.path.splitext(file.filename)[0]}.zip",
                    ExtraArgs={"ACL": "public-read", "Tagging": set_tag},
                )

        # ăăšăŻăźăăă­ăźăŤăŤDBăŤäżĺ­
        dbac.insert(f"{export_path}pass_{os.path.splitext(file.filename)[0]}.zip", password)

    # Not archive
    else:
        # S3ăŤă˘ăăă­ăźă
        my_bucket.Object(export_path + file.filename).put(Body=file, ACL="public-read", Tagging=set_tag)

    flash("File uploaded successfully.", "alert alert-success")
    return redirect(url_for("files", export_path=export_path))


@app.route("/delete", methods=["POST"])
def delete():
    key = request.form["key"]
    export_path = request.form["export-path"]

    my_bucket = get_bucket()

    # ä¸éĺą¤ĺ¨ĺé¤
    summaries = my_bucket.objects.filter(Prefix=key)
    for summary in summaries:
        my_bucket.Object(summary.key).delete()
        if check_already_insert_db(summary.key):
            dbac.remove(summary.key)

    # čŞĺčŞčşŤăĺé¤
    my_bucket.Object(key).delete()
    if check_already_insert_db(key):
        dbac.remove(key)

    flash("File deleted successfully", "alert alert-success")
    return redirect(url_for("files", export_path=export_path))


@app.route("/download", methods=["POST"])
def download():
    key = request.form["key"]

    my_bucket = get_bucket()
    file_obj = my_bucket.Object(key).get()

    key = urllib.parse.quote(key)

    return Response(
        file_obj["Body"].read(),
        mimetype="text/plain",
        headers={"Content-Disposition": "attachment;filename={}".format(key)},
    )


@app.route("/get_public_url", methods=["POST"])
def get_public_url():
    key = request.form["key"]
    s3_client = get_s3_client()
    bucket_location = s3_client.get_bucket_location(Bucket=S3_BUCKET)
    url = f"https://s3-{bucket_location['LocationConstraint']}.amazonaws.com/{S3_BUCKET}/{key}"
    return url


@app.route("/mkdir", methods=["POST"])
def mkdir():
    new_dir_name = request.form["new-dir-name"]
    export_path = request.form["export-path"]

    # validation check ###############################
    if new_dir_name == "":
        flash("Folder name is empty.", "alert alert-danger")
        return redirect(url_for("files", export_path=export_path))
    elif "/" in new_dir_name:
        flash('You cannot use "/" in the folder name.', "alert alert-danger")
        return redirect(url_for("files", export_path=export_path))

    my_bucket = get_bucket()
    summaries = my_bucket.objects.filter(Prefix=export_path)
    summaries = dir_file_filter(summaries, key=export_path)
    for summary in summaries:
        if isinstance(summary, dict) and summary["key"] == new_dir_name + "/":
            flash("The name is already in use.", "alert alert-danger")
            return redirect(url_for("files", export_path=export_path))
    ###################################################

    # ăăŁăŹăŻăăŞä˝ć
    my_bucket.Object(export_path + new_dir_name + "/").put()

    return redirect(url_for("files", export_path=export_path))


if __name__ == "__main__":
    app.run()
    # çŠşăăŁăŹăŻăăŞăŽĺé¤
