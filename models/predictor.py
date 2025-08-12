import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
import os
from config import Config

class ArtAnalyzer:
    def __init__(self):
        self.authenticity_model = None
        self.style_effnet_model = None
        self.style_convnext_model = None
        
        self.style_classes = sorted([
            'art_nouveau', 'baroque', 'expressionism', 'impressionism',
            'post_impressionism', 'realism', 'renaissance', 'romanticism',
            'surrealism', 'ukiyo_e'
        ])
        
        self.authenticity_classes = ['AI Generated', 'Human Created']
        
        self._load_models()
    
    def _load_models(self):
        """Load all trained models"""
        print("Starting model loading...")
        
        # Try loading authenticity model
        try:
            if os.path.exists(Config.AUTHENTICITY_MODEL_PATH):
                print(f"Loading authenticity model from: {Config.AUTHENTICITY_MODEL_PATH}")
                file_size = os.path.getsize(Config.AUTHENTICITY_MODEL_PATH)
                print(f"Authenticity model file size: {file_size / (1024*1024):.2f} MB")
                
                if file_size > 0:
                    self.authenticity_model = tf.keras.models.load_model(Config.AUTHENTICITY_MODEL_PATH, compile=False)
                    print("✅ Authenticity model loaded successfully")
                else:
                    print("❌ Authenticity model file is empty")
            else:
                print(f"❌ Authenticity model not found at: {Config.AUTHENTICITY_MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading authenticity model: {e}")
        
        # Try loading EfficientNet model
        try:
            if os.path.exists(Config.STYLE_EFFNET_MODEL_PATH):
                print(f"Loading EfficientNet model from: {Config.STYLE_EFFNET_MODEL_PATH}")
                file_size = os.path.getsize(Config.STYLE_EFFNET_MODEL_PATH)
                print(f"EfficientNet model file size: {file_size / (1024*1024):.2f} MB")
                
                if file_size > 0:
                    self.style_effnet_model = tf.keras.models.load_model(Config.STYLE_EFFNET_MODEL_PATH, compile=False)
                    print("✅ EfficientNet style model loaded successfully")
                else:
                    print("❌ EfficientNet model file is empty")
            else:
                print(f"❌ EfficientNet model not found at: {Config.STYLE_EFFNET_MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading EfficientNet model: {e}")
        
        # Try loading ConvNeXt model
        try:
            if os.path.exists(Config.STYLE_CONVNEXT_MODEL_PATH):
                print(f"Loading ConvNeXt model from: {Config.STYLE_CONVNEXT_MODEL_PATH}")
                file_size = os.path.getsize(Config.STYLE_CONVNEXT_MODEL_PATH)
                print(f"ConvNeXt model file size: {file_size / (1024*1024):.2f} MB")
                
                if file_size > 0:
                    self.style_convnext_model = tf.keras.models.load_model(Config.STYLE_CONVNEXT_MODEL_PATH, compile=False)
                    print("✅ ConvNeXt style model loaded successfully")
                else:
                    print("❌ ConvNeXt model file is empty")
            else:
                print(f"❌ ConvNeXt model not found at: {Config.STYLE_CONVNEXT_MODEL_PATH}")
        except Exception as e:
            print(f"❌ Error loading ConvNeXt model: {e}")
        
        print("Model loading complete.")
        print(f"Available models: Authenticity={self.authenticity_model is not None}, "
              f"EfficientNet={self.style_effnet_model is not None}, "
              f"ConvNeXt={self.style_convnext_model is not None}")
    
    def analyze_image(self, image_path):
        """Analyze artwork for authenticity and style"""
        print(f"Starting analysis of image: {image_path}")
        
        results = {
            'authenticity': None,
            'style': None,
            'error': None
        }
        
        try:
            # Check if image exists and is readable
            if not os.path.exists(image_path):
                results['error'] = 'Image file not found'
                return results
            
            image = Image.open(image_path)
            print(f"Image loaded successfully: {image.size}")
            
            # Analyze authenticity
            if self.authenticity_model:
                print("Running authenticity analysis...")
                results['authenticity'] = self._predict_authenticity(image)
                print(f"Authenticity result: {results['authenticity']}")
            else:
                results['authenticity'] = {'error': 'Authenticity model not available'}
                print("Authenticity model not available")
            
            # Analyze style
            if self.style_effnet_model and self.style_convnext_model:
                print("Running style analysis...")
                results['style'] = self._predict_style(image)
                print(f"Style result: {results['style']}")
            elif self.style_effnet_model or self.style_convnext_model:
                results['style'] = {'error': 'Only one style model available - need both for ensemble prediction'}
                print("Incomplete style models - need both EfficientNet and ConvNeXt")
            else:
                results['style'] = {'error': 'Style models not available'}
                print("Style models not available")
            
        except Exception as e:
            error_msg = f"Error during analysis: {str(e)}"
            print(error_msg)
            results['error'] = error_msg
        
        print("Analysis complete")
        return results
    
    def _predict_authenticity(self, image):
        """Predict if artwork is AI-generated or human-created"""
        try:
            # Preprocess for authenticity model
            img_array = self._preprocess_for_authenticity(image)
            
            # Predict
            prediction = self.authenticity_model.predict(img_array)
            class_idx = int(np.round(prediction[0][0]))
            confidence = float((prediction[0][0] if class_idx == 1 else 1 - prediction[0][0]) * 100)
            
            return {
                'prediction': self.authenticity_classes[class_idx],
                'confidence': confidence,
                'is_human': class_idx == 1
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _predict_style(self, image):
        """Predict artistic style using ensemble of models"""
        try:
            # Preprocess for both models
            effnet_input = self._preprocess_for_effnet(image)
            convnext_input = self._preprocess_for_convnext(image)
            
            # Get predictions
            effnet_pred = self.style_effnet_model.predict(effnet_input)[0]
            convnext_pred = self.style_convnext_model.predict(convnext_input)[0]
            
            # Ensemble prediction
            ensemble_pred = (effnet_pred + convnext_pred) / 2.0
            style_idx = np.argmax(ensemble_pred)
            confidence = float(np.max(ensemble_pred) * 100)
            
            # Get top 3 predictions
            top_3_idx = ensemble_pred.argsort()[-3:][::-1]
            top_3_styles = [
                {
                    'style': self.style_classes[i].replace('_', ' ').title(),
                    'confidence': float(ensemble_pred[i] * 100)
                }
                for i in top_3_idx
            ]
            
            return {
                'predicted_style': self.style_classes[style_idx].replace('_', ' ').title(),
                'confidence': confidence,
                'top_3_predictions': top_3_styles
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _preprocess_for_authenticity(self, image):
        """Preprocess image for authenticity model"""
        img = image.resize((224, 224)).convert('RGB')
        img_array = tf.keras.preprocessing.image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return img_array / 255.0
    
    def _preprocess_for_effnet(self, image):
        """Preprocess image for EfficientNet model"""
        img = image.resize((260, 260)).convert('RGB')
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return tf.keras.applications.efficientnet_v2.preprocess_input(img_array)
    
    def _preprocess_for_convnext(self, image):
        """Preprocess image for ConvNeXt model"""
        img = image.resize((224, 224)).convert('RGB')
        img_array = np.array(img)
        img_array = np.expand_dims(img_array, axis=0)
        return tf.keras.applications.convnext.preprocess_input(img_array)