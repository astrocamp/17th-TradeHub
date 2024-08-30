## 未完成 用csv.excel 匯入資料

import csv
import pandas as pd
from django.core.management.base import BaseCommand
from myapp.models import MyModel  # 替換為您的模型


class Command(BaseCommand):
    help = "Import data from CSV or Excel file into MyModel"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **kwargs):
        file_path = kwargs["file_path"]
        if file_path.endswith(".csv"):
            self.import_csv(file_path)
        elif file_path.endswith(".xlsx"):
            self.import_excel(file_path)
        else:
            self.stdout.write(self.style.ERROR("Unsupported file type"))

    def import_csv(self, file_path):
        with open(file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                MyModel.objects.create(
                    name=row["name"],
                    phone_number=row["phone_number"],
                    address=row["address"],
                    email=row["email"],
                    create_at=row["create_at"],
                    delete_at=row["delete_at"],
                    note=row.get("note", ""),
                )
        self.stdout.write(self.style.SUCCESS("Successfully imported data from CSV"))

    def import_excel(self, file_path):
        df = pd.read_excel(file_path)
        for index, row in df.iterrows():
            MyModel.objects.create(
                name=row["name"],
                phone_number=row["phone_number"],
                address=row["address"],
                email=row["email"],
                create_at=row["create_at"],
                delete_at=row["delete_at"],
                note=row.get("note", ""),
            )
        self.stdout.write(self.style.SUCCESS("Successfully imported data from Excel"))
