from addons.googlesheets.model.sheetscsv import SheetsCSV

GOOGLE_SHEET_ID = "1Xe5SIvaAHgjqIipYA-NVXuzpd4cX0xMh-cLnzJFI3mk"
INFLATION_TAB_RANGE = "'inflation, previous month = 100'!A1:M2"


def main():
    df = SheetsCSV(GOOGLE_SHEET_ID, INFLATION_TAB_RANGE).to_dataframe(first_row_as_header=True)
    print(df)


if __name__ == "__main__":
    main()
