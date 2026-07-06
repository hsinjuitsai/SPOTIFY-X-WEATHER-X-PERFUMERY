from pyairtable import Table


class AirtableResults:
    def __init__(self, token: str, base_id: str, table_name: str):
        self.table = Table(token, base_id, table_name)

    def latest(self):
        records = self.table.all(sort=["-createdTime"], max_records=1)
        return records[0] if records else None

