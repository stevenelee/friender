import os
from dotenv import load_dotenv

import logging
import boto3
from botocore.exceptions import ClientError

from flask import (
    Flask, render_template, request, flash, redirect, session, g, abort,
)
from flask_debugtoolbar import DebugToolbarExtension

from forms import (
    AddImageForm
)

load_dotenv()

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ['SECRET_KEY']
toolbar = DebugToolbarExtension(app)


@app.get('/')
def inputForm():
    """input form"""

    form = AddImageForm()

    return render_template('form.html', form=form)


@app.post('/')
def uploadImage():
    """Test upload of Image to S3.
    """
    print("printing request.files", request.files['image'])
    new_file = request.files['image']

    upload_file(new_file, "s3://jstern-friendly/images")

    # g.image = request.files.

    # upload_file(file)
    return redirect('/')




def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True

    return redirect("/")