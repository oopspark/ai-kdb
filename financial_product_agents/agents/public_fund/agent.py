from shared.catalog import SPECS
from shared.csv_agent import CsvProductAgent


class PublicFundAgent(CsvProductAgent):
    def __init__(self, csv_path):
        super().__init__(SPECS["public_fund"], csv_path)

