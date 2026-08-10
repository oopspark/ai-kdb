from shared.catalog import SPECS
from shared.csv_agent import CsvProductAgent


class OverseasEtfAgent(CsvProductAgent):
    def __init__(self, csv_path):
        super().__init__(SPECS["overseas_etf"], csv_path)

