from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from app import app
import os
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage

# Configure upload destinations
app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(app.config['UPLOAD_FOLDER'], 'photos')
app.config['UPLOADED_VIDEOS_DEST'] = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')

# Define UploadSets
photos = UploadSet('photos', IMAGES)
videos = UploadSet('videos', ALL)

# Bind UploadSets to Flask app
configure_uploads(app, (photos, videos))
