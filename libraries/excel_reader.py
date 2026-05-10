import os
import openpyxl
import logging

class ExcelReader:
    """Class for reading data from Excel files."""

    def __init__(self, file_path):
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)

    def read_wholesalers(self):
        """Reads wholesaler names from the first column of the Excel file."""
        if not os.path.exists(self.file_path):
            self.logger.error(f"ERROR: File {self.file_path} not found.")
            return []

        try:
            wb = openpyxl.load_workbook(self.file_path)
            ws = wb.active
            wholesalers = [row[0] for row in ws.iter_rows(min_row=2, values_only=True) if row[0]]
            return wholesalers
        except Exception as e:
            self.logger.error(f"ERROR: Failed to read Excel file: {e}")
            return []
