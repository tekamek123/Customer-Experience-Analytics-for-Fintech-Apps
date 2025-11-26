"""
Helper script to install spaCy English model
Run this before using thematic_analysis.py
"""

import subprocess
import sys

def install_spacy_model():
    """Install spaCy English model."""
    print("Installing spaCy English model (en_core_web_sm)...")
    print("This may take a few minutes...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "spacy", "download", "en_core_web_sm"
        ])
        print("✓ spaCy model installed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"✗ Error installing spaCy model: {str(e)}")
        print("\nYou can try manually:")
        print("  python -m spacy download en_core_web_sm")


if __name__ == "__main__":
    install_spacy_model()

