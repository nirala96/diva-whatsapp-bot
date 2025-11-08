"""
Google Sheets Integration
Handles authentication and data logging to Google Sheets for conversation tracking.
"""

import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Google Sheets API scope
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]

# Global variables for authenticated client and worksheet
_client = None
_worksheet = None


def get_worksheet():
    """
    Authenticate with Google Sheets API and return the target worksheet.
    Uses service account credentials for server-to-server authentication.
    
    Returns:
        gspread.Worksheet: The authenticated worksheet object
        
    Raises:
        Exception: If authentication fails or sheet is not accessible
    """
    global _client, _worksheet
    
    # Return cached worksheet if already authenticated
    if _worksheet is not None:
        return _worksheet
    
    try:
        # Get credentials file path from environment
        service_account_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        
        if not service_account_file:
            raise ValueError("GOOGLE_SERVICE_ACCOUNT_JSON not set in environment variables")
        
        if not os.path.exists(service_account_file):
            raise FileNotFoundError(f"Service account file not found: {service_account_file}")
        
        # Authenticate using service account credentials
        credentials = Credentials.from_service_account_file(
            service_account_file,
            scopes=SCOPE
        )
        
        # Authorize the client
        _client = gspread.authorize(credentials)
        
        # Open the specified Google Sheet
        sheet_name = os.getenv("SHEET_NAME", "DivaDaulti_Leads")
        spreadsheet = _client.open(sheet_name)
        
        # Get the first worksheet (you can modify this to target a specific sheet)
        _worksheet = spreadsheet.sheet1
        
        print(f"Successfully connected to Google Sheet: {sheet_name}")
        return _worksheet
        
    except Exception as e:
        print(f"Error connecting to Google Sheets: {str(e)}")
        raise


def append_row(row_data):
    """
    Append a new row to the Google Sheet.
    Automatically handles authentication and retries if needed.
    
    Args:
        row_data (list): List of values to append as a new row
                        Example: [timestamp, user, message, reply]
    
    Returns:
        dict: Response from Google Sheets API
        
    Raises:
        Exception: If appending fails after retry
    """
    try:
        worksheet = get_worksheet()
        
        # Append the row to the sheet
        result = worksheet.append_row(row_data)
        
        print(f"Successfully logged conversation to Google Sheets")
        return result
        
    except Exception as e:
        # If authentication expired, reset and retry once
        global _client, _worksheet
        _client = None
        _worksheet = None
        
        print(f"Error appending row, retrying: {str(e)}")
        
        try:
            worksheet = get_worksheet()
            result = worksheet.append_row(row_data)
            print(f"Successfully logged conversation to Google Sheets (retry)")
            return result
        except Exception as retry_error:
            print(f"Failed to append row after retry: {str(retry_error)}")
            raise


def initialize_sheet_headers():
    """
    Initialize the Google Sheet with column headers if it's empty.
    Run this once during setup.
    
    Returns:
        bool: True if headers were added, False if sheet already has data
    """
    try:
        worksheet = get_worksheet()
        
        # Check if sheet is empty
        if len(worksheet.get_all_values()) == 0:
            headers = ["Timestamp", "User", "Customer Message", "AI Reply"]
            worksheet.append_row(headers)
            print("Added headers to Google Sheet")
            return True
        else:
            print("Sheet already has data, skipping header initialization")
            return False
            
    except Exception as e:
        print(f"Error initializing headers: {str(e)}")
        raise


if __name__ == "__main__":
    # Test the Google Sheets connection
    print("Testing Google Sheets connection...")
    try:
        initialize_sheet_headers()
        test_row = [
            "2024-01-01 12:00:00",
            "test_user",
            "Hello, this is a test message",
            "Hi! Thanks for reaching out to Diva Daulti!"
        ]
        append_row(test_row)
        print("✓ Google Sheets integration is working correctly!")
    except Exception as e:
        print(f"✗ Google Sheets integration failed: {str(e)}")
