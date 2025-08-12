#!/usr/bin/env python3
"""
Debug script to check model files and loading issues
Run this before starting the Flask app to diagnose problems
"""

import os
import tensorflow as tf
from config import Config

def check_file_status(filepath, name):
    print(f"\n--- Checking {name} ---")
    print(f"Path: {filepath}")
    
    if os.path.exists(filepath):
        file_size = os.path.getsize(filepath)
        print(f"✅ File exists")
        print(f"📏 Size: {file_size:,} bytes ({file_size/(1024*1024):.2f} MB)")
        
        if file_size == 0:
            print("❌ FILE IS EMPTY!")
            return False
        elif file_size < 1024:
            print("⚠️ File is very small - likely a Git LFS pointer")
            return False
        else:
            print("✅ File has reasonable size")
            
            # Try to load the model
            try:
                print("🔄 Attempting to load model...")
                model = tf.keras.models.load_model(filepath, compile=False)
                print(f"✅ Model loaded successfully!")
                print(f"📐 Input shape: {model.input_shape}")
                print(f"📐 Output shape: {model.output_shape}")
                return True
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
                return False
    else:
        print(f"❌ File does not exist!")
        
        # Check if directory exists
        parent_dir = os.path.dirname(filepath)
        if os.path.exists(parent_dir):
            print(f"📁 Parent directory exists: {parent_dir}")
            keras_files = [f for f in os.listdir(parent_dir) if f.endswith('.keras')]
            if keras_files:
                print(f"📁 Keras files in directory: {keras_files}")
            else:
                print("📁 No .keras files found in directory")
        else:
            print(f"❌ Parent directory doesn't exist: {parent_dir}")
        return False

def main():
    print("=" * 60)
    print("ART ANALYSIS PLATFORM - MODEL DEBUG TOOL")
    print("=" * 60)
    
    print(f"\n🔍 System Information:")
    print(f"Python version: {tf.__version__}")
    print(f"TensorFlow version: {tf.__version__}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Check all model files
    models_status = {
        'authenticity': check_file_status(Config.AUTHENTICITY_MODEL_PATH, "Authenticity Model"),
        'effnet': check_file_status(Config.STYLE_EFFNET_MODEL_PATH, "EfficientNet Style Model"),
        'convnext': check_file_status(Config.STYLE_CONVNEXT_MODEL_PATH, "ConvNeXt Style Model")
    }
    
    print(f"\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    working_models = sum(models_status.values())
    total_models = len(models_status)
    
    print(f"✅ Working models: {working_models}/{total_models}")
    
    if working_models == 0:
        print("\n❌ NO MODELS ARE WORKING!")
        print("\n🔧 SOLUTIONS:")
        print("1. Check if model files are actually downloaded (not empty)")
        print("2. If using Git LFS, run: git lfs pull")
        print("3. Re-download model files from original source")
        print("4. Check file permissions")
        
    elif working_models < total_models:
        print(f"\n⚠️ PARTIAL FUNCTIONALITY - {total_models - working_models} model(s) missing")
        print("\n🔧 RECOMMENDATIONS:")
        print("- Authenticity analysis will work if authenticity model is loaded")
        print("- Style analysis needs BOTH EfficientNet and ConvNeXt models")
        
    else:
        print("\n✅ ALL MODELS LOADED SUCCESSFULLY!")
        print("🚀 Your Flask app should work perfectly!")
    
    # Check upload directory
    print(f"\n--- Checking Upload Directory ---")
    upload_dir = Config.UPLOAD_FOLDER
    if os.path.exists(upload_dir):
        print(f"✅ Upload directory exists: {upload_dir}")
    else:
        print(f"⚠️ Upload directory missing (will be created): {upload_dir}")
    
    print(f"\n" + "=" * 60)

if __name__ == "__main__":
    main()