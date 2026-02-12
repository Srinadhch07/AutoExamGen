import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Firebase
PROJECT_ID = "aits-lifelet"
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "keys/aits-lifelet-firebase-adminsdk-fbsvc-45213288ea.json")

# Apple APNs
TEAM_ID = "67XH487NTB"
KEY_ID = "ADD9G493GD"
BUNDLE_ID = "com.aits.lifelet"
P8_FILE_PATH = os.path.join(BASE_DIR, "keys/AuthKey_ADD9G493GD.p8")
IS_PRODUCTION = True
