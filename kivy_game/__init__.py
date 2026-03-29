import sys
import os as _os

# Add project root to sys.path so intra-package imports (from shared / from pygame) work
# when any module inside this package is imported.
_project_root = _os.path.dirname(_os.path.dirname(_os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
