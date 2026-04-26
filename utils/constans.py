# Legacy Google Sheets constants (kept for compatibility, but not used in China deployment)
LEGACY_SCOPE = "https://www.googleapis.com/auth/spreadsheets"
LEGACY_SPREADSHEET_ID = "1rkMVLvh3JrBq_tbi4Ho0qjCDAP3vYdNuWOEjYpkJLNU"
SHEET_NAME = "Database"
LEGACY_GSHEET_URL = f"https://docs.google.com/spreadsheets/d/{LEGACY_SPREADSHEET_ID}"

# China-compatible database settings
DATABASE_PATH = "platform.db"
CHINA_DEPLOYMENT = True  # Set to True for China deployment

COMMENT_TEMPLATE_MD = """{} - {}
> {}"""