import sys
import os
from pathlib import Path

# Agregar el directorio raíz al PYTHONPATH
root_dir = str(Path(__file__).parent.parent)
sys.path.append(root_dir)