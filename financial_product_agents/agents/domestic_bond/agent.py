from shared.catalog import SPECS
from shared.csv_agent import CsvProductAgent


class DomesticBondAgent(CsvProductAgent):
    def __init__(self, csv_path):
        super().__init__(SPECS["domestic_bond"], csv_path)

