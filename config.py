import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
    
    # Model paths
    AUTHENTICITY_MODEL_PATH = 'trained_models/authenticity_model.keras'
    STYLE_EFFNET_MODEL_PATH = 'trained_models/style_model_effnet.keras'
    STYLE_CONVNEXT_MODEL_PATH = 'trained_models/style_model_convnext.keras'