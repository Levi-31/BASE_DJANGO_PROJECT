import logging
from functools import wraps

import gspread
from django.conf import settings
from oauth2client.service_account import ServiceAccountCredentials

from libs.constant import Constant


logger = logging.getLogger("GoogleSpreadSheet")

# --- Mocking missing dependencies for generic usage ---
def exception_handler(priority):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"[{priority} PRIORITY ERROR] in {func.__name__}: {str(e)}")
                raise e
        return wrapper
    return decorator
# ----------------------------------------------------


class GoogleSpreadSheet:
    def __init__(self, url):
        self.url = url

    def get_gspread_creds_path(self):
        # BASE_DIR is a pathlib.Path object in modern Django
        return str(settings.BASE_DIR / "credentials" / "gspread_credentials.json")

    def get_scope(self):
        return [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive",
        ]

    def get_credentials(self):
        credential_path = self.get_gspread_creds_path()
        scope = self.get_scope()
        return ServiceAccountCredentials.from_json_keyfile_name(credential_path, scope)

    def get_spreedsheet(self):
        credentials = self.get_credentials()
        client = gspread.authorize(credentials)
        sheet = client.open_by_url(self.url)
        return sheet

    @exception_handler(Constant.ExceptionPriority.MEDIUM)
    def get_rows(self, work_sheet_number=0):
        sheet = self.get_spreedsheet()
        worksheet = sheet.get_worksheet(work_sheet_number)
        return worksheet.get_values()

    def get_rows_in_chunks(self, chunk_size=1500, work_sheet_number=0):
        try:
            sheet = self.get_spreedsheet()
            worksheet = sheet.get_worksheet(work_sheet_number)

            start_row = 1
            while True:
                end_row = start_row + chunk_size - 1
                cell_range = f"A{start_row}:ZZ{end_row}"

                values = list(worksheet.get_values(cell_range))
                if not values:
                    break

                yield values

                if len(values) < chunk_size:
                    break

                start_row += chunk_size
        except Exception as e:
            logger.error(f"Error while fetching rows in chunks: {e}")
            return
