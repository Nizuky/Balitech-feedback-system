import os
import sys

# Add root folder to python path so app module can be found
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

app = create_app(os.environ.get('FLASK_ENV', 'production'))
