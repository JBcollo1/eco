from flask_uploads import UploadSet, configure_uploads, IMAGES, ALL
from app import app 
import os


app.config['UPLOADED_PHOTOS_DEST'] = os.path.join(app.config['UPLOAD_FOLDER'], 'photos')
app.config['UPLOADED_VIDEOS_DEST'] = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')

photos = UploadSet('photos', IMAGES)
videos = UploadSet('videos', ALL)

configure_uploads(app, (photos, videos))