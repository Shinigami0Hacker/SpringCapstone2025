import pickle
import os


# def create_schema_column(data: bytes):
#     for record in data:
#         table_name = record.get('name', None)
#         if table_name:
#             table = self.db.table(table_name)
#             table.insert(record)  # Insert the record into the table
#             print(f"Inserted data into table '{table_name}'")