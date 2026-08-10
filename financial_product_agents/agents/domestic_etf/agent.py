from shared.catalog import SPECS
from shared.csv_agent import CsvProductAgent


class DomesticEtfAgent(CsvProductAgent):
    def __init__(self, csv_path):
        super().__init__(SPECS["domestic_etf"], csv_path)

