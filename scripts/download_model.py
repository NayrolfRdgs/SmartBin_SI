"""
Smart Bin SI - Automatic Model Downloader
Downloads pre-trained YOLOv8 waste detection models from Roboflow
"""

import os
import sys
from pathlib import Path
import urllib.request
import json

# ============================================
# CONFIGURATION
# ============================================

# Available pre-trained models on Roboflow
AVAILABLE_MODELS = {
    "1": {
        "name": "YOLOv8n Waste (Nano - Fast)",
        "size": "6 MB",
        "fps": "20+ FPS on Jetson",
        "accuracy": "~85%",
        "classes": ["cardboard", "glass", "metal", "paper", "plastic", "trash"],
        "roboflow_url": "https://universe.roboflow.com/fyp-bfx3h/yolov8-trash-detections",
        "workspace": "fyp-bfx3h",
        "project": "yolov8-trash-detections",
        "version": 1,
        "model_type": "yolov8n"
    },
    "2": {
        "name": "YOLOv8s Waste (Small - Balanced)",
        "size": "22 MB",
        "fps": "12-15 FPS on Jetson",
        "accuracy": "~89%",
        "classes": ["cardboard", "glass", "metal", "paper", "plastic", "biodegradable"],
        "roboflow_url": "https://universe.roboflow.com/projectverba/yolo-waste-detection",
        "workspace": "projectverba",
        "project": "yolo-waste-detection",
        "version": 1,
        "model_type": "yolov8s"
    },
    "3": {
        "name": "YOLOv8m Waste (Medium - Accurate)",
        "size": "50 MB",
        "fps": "5-8 FPS on Jetson",
        "accuracy": "~92%",
        "classes": ["recyclable", "organic", "hazardous", "general"],
        "roboflow_url": "https://universe.roboflow.com/waste-management-project/smart-waste-sorting",
        "workspace": "waste-management-project",
        "project": "smart-waste-sorting",
        "version": 2,
        "model_type": "yolov8m"
    }
}

# Paths
SCRIPT_DIR = Path(__file__).parent.parent
MODELS_DIR = SCRIPT_DIR / "models"


# ============================================
# FUNCTIONS
# ============================================

def display_models():
    """Display available models with details"""
    print("\n" + "="*60)
    print("🧠 AVAILABLE PRE-TRAINED YOLO MODELS")
    print("="*60)
    
    for key, model in AVAILABLE_MODELS.items():
        print(f"\n[{key}] {model['name']}")
        print(f"    Size: {model['size']}")
        print(f"    Speed: {model['fps']}")
        print(f"    Accuracy: {model['accuracy']}")
        print(f"    Classes: {', '.join(model['classes'])}")
    
    print("\n" + "="*60)


def download_via_roboflow(model_info):
    """
    Download model using Roboflow API
    Requires roboflow library
    """
    try:
        from roboflow import Roboflow
    except ImportError:
        print("\n❌ Roboflow library not found!")
        print("   Installing roboflow...")
        os.system("pip3 install roboflow")
        from roboflow import Roboflow
    
    print("\n📥 Downloading model from Roboflow...")
    print(f"   Workspace: {model_info['workspace']}")
    print(f"   Project: {model_info['project']}")
    
    # Ask for API key
    api_key = input("\nEnter your Roboflow API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("\n⚠️  No API key provided")
        print("   To get a free API key:")
        print("   1. Go to https://roboflow.com")
        print("   2. Create a free account")
        print("   3. Copy your API key from Settings")
        print("\n   Falling back to manual download...")
        return False
    
    try:
        # Initialize Roboflow
        rf = Roboflow(api_key=api_key)
        
        # Get project
        project = rf.workspace(model_info['workspace']).project(model_info['project'])
        
        # Download dataset with model
        dataset = project.version(model_info['version']).download("yolov8")
        
        print(f"\n✅ Model downloaded to: {dataset.location}")
        
        # Copy weights to models folder
        weights_path = Path(dataset.location) / "weights" / "best.pt"
        if weights_path.exists():
            target_path = MODELS_DIR / f"{model_info['model_type']}_waste.pt"
            import shutil
            shutil.copy(weights_path, target_path)
            print(f"✅ Model copied to: {target_path}")
            return True
        else:
            print("⚠️  Weights file not found in downloaded dataset")
            return False
            
    except Exception as e:
        print(f"\n❌ Error downloading from Roboflow: {e}")
        return False


def download_via_ultralytics():
    """
    Download generic YOLOv8 model from Ultralytics
    This is a fallback if Roboflow doesn't work
    """
    try:
        from ultralytics import YOLO
    except ImportError:
        print("\n❌ Ultralytics library not found!")
        print("   Installing ultralytics...")
        os.system("pip3 install ultralytics")
        from ultralytics import YOLO
    
    print("\n📥 Downloading generic YOLOv8 model...")
    print("   Note: This is NOT specifically trained for waste")
    print("   But it can still detect common objects")
    
    models = ["yolov8n.pt", "yolov8s.pt"]
    
    for model_name in models:
        try:
            print(f"\n   Downloading {model_name}...")
            model = YOLO(model_name)  # Auto-downloads
            
            # Move to models folder
            target_path = MODELS_DIR / model_name
            source_path = Path(model_name)
            
            if source_path.exists():
                import shutil
                shutil.move(str(source_path), str(target_path))
                print(f"   ✅ Saved to: {target_path}")
        except Exception as e:
            print(f"   ❌ Failed to download {model_name}: {e}")
    
    return True


def manual_download_instructions(model_info):
    """
    Display instructions for manual download
    """
    print("\n" + "="*60)
    print("📖 MANUAL DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print(f"\nModel: {model_info['name']}")
    print(f"\n1. Go to: {model_info['roboflow_url']}")
    print("2. Click 'Download Dataset'")
    print("3. Choose format: YOLOv8")
    print("4. Download the ZIP file")
    print("5. Extract it")
    print("6. Find 'weights/best.pt' in the extracted folder")
    print(f"7. Copy 'best.pt' to: {MODELS_DIR}/{model_info['model_type']}_waste.pt")
    print("\n" + "="*60)


def create_model_info_file(model_info):
    """
    Create a README in models folder with model information
    """
    readme_path = MODELS_DIR / "README.md"
    
    content = f"""# 🧠 YOLO Models for Smart Bin SI

## Current Model

**{model_info['name']}**

- **Size:** {model_info['size']}
- **Speed:** {model_info['fps']}
- **Accuracy:** {model_info['accuracy']}
- **Classes:** {', '.join(model_info['classes'])}

## Classes Detected

"""
    
    for i, class_name in enumerate(model_info['classes'], 1):
        content += f"{i}. `{class_name}`\n"
    
    content += f"""
## Source

- **Roboflow Project:** {model_info['roboflow_url']}
- **Workspace:** {model_info['workspace']}
- **Project:** {model_info['project']}
- **Version:** {model_info['version']}

## Usage

```python
from ultralytics import YOLO

# Load model
model = YOLO('models/{model_info['model_type']}_waste.pt')

# Run detection
results = model('path/to/image.jpg')
results.show()
```

## Update Model

To download a different model, run:

```bash
python3 scripts/download_model.py
```
"""
    
    with open(readme_path, 'w') as f:
        f.write(content)
    
    print(f"\n✅ Model info saved to: {readme_path}")


def update_config_file(model_info):
    """
    Update src/config.py with the selected model
    """
    config_path = SCRIPT_DIR / "src" / "config.py"
    
    if not config_path.exists():
        print(f"⚠️  Config file not found: {config_path}")
        return
    
    # Read current config
    with open(config_path, 'r') as f:
        lines = f.readlines()
    
    # Update MODEL_PATH line
    new_lines = []
    for line in lines:
        if line.strip().startswith("MODEL_PATH ="):
            new_lines.append(f'MODEL_PATH = "models/{model_info["model_type"]}_waste.pt"\n')
        else:
            new_lines.append(line)
    
    # Write back
    with open(config_path, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Updated config file: {config_path}")


# ============================================
# MAIN
# ============================================

def main():
    """
    Main function to download YOLO model
    """
    print("\n" + "="*60)
    print("🤖 SMART BIN SI - MODEL DOWNLOADER")
    print("="*60)
    
    # Create models directory if it doesn't exist
    MODELS_DIR.mkdir(exist_ok=True)
    
    # Display available models
    display_models()
    
    # Get user choice
    choice = input("\nSelect model to download (1-3) or 'q' to quit: ").strip()
    
    if choice.lower() == 'q':
        print("\n👋 Exiting...")
        return
    
    if choice not in AVAILABLE_MODELS:
        print("\n❌ Invalid choice!")
        return
    
    model_info = AVAILABLE_MODELS[choice]
    
    print(f"\n✅ Selected: {model_info['name']}")
    
    # Choose download method
    print("\nDownload methods:")
    print("  [1] Roboflow API (Recommended - automatic)")
    print("  [2] Ultralytics Generic (Fallback - not waste-specific)")
    print("  [3] Manual Download (Instructions only)")
    
    method = input("\nChoose method (1-3): ").strip()
    
    success = False
    
    if method == "1":
        success = download_via_roboflow(model_info)
    elif method == "2":
        success = download_via_ultralytics()
        model_info = AVAILABLE_MODELS["1"]  # Use nano as default
    elif method == "3":
        manual_download_instructions(model_info)
        return
    else:
        print("\n❌ Invalid method!")
        return
    
    if success:
        # Create model info file
        create_model_info_file(model_info)
        
        # Update config
        update_config_file(model_info)
        
        print("\n" + "="*60)
        print("✅ MODEL SETUP COMPLETE!")
        print("="*60)
        print("\nNext steps:")
        print("  1. Test detection: python3 src/yolo_detector.py")
        print("  2. Or run automatic mode: bash scripts/run_auto.sh")
        print("="*60 + "\n")
    else:
        print("\n❌ Download failed!")
        print("   Try manual download method instead")
        manual_download_instructions(model_info)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)