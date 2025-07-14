from setuptools import setup

# The main script that starts your application
APP = ['gui.py']

# --- Configuration for py2app ---
OPTIONS = {
    'iconfile': 'backend/assets/icon.icns',
    'packages': [
        'backend', 'numpy', 'pandas', 'scipy',
        'yfinance', 'matplotlib', 'sv_ttk',
        'tkinterdnd2', 'openpyxl'
    ],

    # --- ADD THIS SECTION ---
    # Manually include the missing dylib file.
    # Replace the path with the one you found in Step 1.
    'frameworks': [
    ],

    'plist': {
        'CFBundleName': 'Fintech Alpha',
        'CFBundleDisplayName': 'Fintech Alpha',
        'CFBundleGetInfoString': "Black-Scholes, Monte Carlo, and DCF Modeling",
        'CFBundleIdentifier': "com.traslappen.bsmsim",
        'CFBundleVersion': "1.0.0",
        'CFBundleShortVersionString': "1.0",
        'NSHumanReadableCopyright': 'Copyright © 2025, Traslappen, All Rights Reserved'
    }
}

# NOTE: The monkey-patch and 'excludes' for setuptools are no longer needed
# with modern py2app and can sometimes cause issues. This is a cleaner setup.

setup(
    app=APP,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)