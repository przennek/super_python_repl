from __future__ import print_function

import io
from typing import List, Optional

import pandas as pd
from googleapiclient.errors import HttpError

from core.google_sheets_service import get_sheet


class SheetsCSV:
    payload: str

    def __init__(self,
                 spreadsheet_id: str,
                 range_name: str):
        try:
            sheet = get_sheet()
            # "A1:C2"
            result = sheet.values().get(
                spreadsheetId=spreadsheet_id,
                range=range_name
            ).execute()
            rows = result.get('values', [])
            self.payload = self.__to_csv(rows)
        except HttpError as error:
            print(f"An error occurred: {error}")
            raise error

    def to_dataframe(self,
                     index_col: Optional[int] = None,
                     parse_dates: bool = False,
                     first_row_as_header=False):
        df = pd.read_csv(
            io.StringIO(self.payload),
            sep=",",
            header=None,
            index_col=index_col,
            parse_dates=parse_dates
        )

        if first_row_as_header:
            columns = df.iloc[0]
            npal = self.payload[self.payload.find("\n")+1:]
            
            df = pd.read_csv(
                io.StringIO(npal),
                sep=",",
                header=None,
                index_col=index_col,
                parse_dates=parse_dates
            )

            df.columns = columns

        return df

    @staticmethod
    def __to_csv(sheet: List[List[str]]) -> str:
        out = ""
        for r in sheet:
            for cv in r:
                c = cv.replace(",", ".")
                out += "," + c
            out += "\n"
        out = out.replace("\n,", "\n")[1:]
        return out

    def __str__(self):
        return self.payload
