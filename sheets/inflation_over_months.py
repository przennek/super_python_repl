from addons.googlesheets.model.sheetscsv import SheetsCSV
import pandas as pd
import numpy as np


GOOGLE_SHEET_ID = "1Xe5SIvaAHgjqIipYA-NVXuzpd4cX0xMh-cLnzJFI3mk"
INFLATION_TAB_RANGE = "'inflation, previous month = 100'!A1:M2"


def main():
    global df
    input_df = SheetsCSV(GOOGLE_SHEET_ID, INFLATION_TAB_RANGE).to_dataframe(first_row_as_header=True)
    start_dates = pd.date_range(start=str(int(input_df.iloc[0][0])), periods=12, freq=pd.offsets.MonthBegin(1))
    df = pd.DataFrame(np.zeros([12]), index=start_dates, columns=["inflacja/mdm"])
    for i in range(len(df)):
        if i == 0:
            df.iloc[i] = input_df.iloc[0][i+1] - 100
        else:
            df.iloc[i] = input_df.iloc[0][i] * input_df.iloc[0][i+1] * 0.0001


if __name__ == "__main__":
    main()
