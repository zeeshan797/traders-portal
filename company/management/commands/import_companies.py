import csv
from django.core.management.base import BaseCommand
from company.models import Company

class Command(BaseCommand):
    help = 'Import companies from master.csv file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to master.csv file')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        try:
            with open(csv_file, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                companies = []
                count = 0
                
                for row in reader:
                    # Skip empty rows
                    if not row['symbol']:
                        continue
                    
                    company = Company(
                        company_name=row['company_name'],
                        symbol=row['symbol'],
                        scripcode=row['scripcode'] if row['scripcode'] else None,
                    )
                    companies.append(company)
                    count += 1
                    
                    # Bulk insert every 500 records for better performance
                    if len(companies) >= 500:
                        Company.objects.bulk_create(companies, ignore_conflicts=True)
                        self.stdout.write(f'✅ Imported {count} companies so far...')
                        companies = []
                
                # Insert remaining records
                if companies:
                    Company.objects.bulk_create(companies, ignore_conflicts=True)
                    self.stdout.write(f'✅ Imported final batch')
                
                total = Company.objects.count()
                self.stdout.write(self.style.SUCCESS(f'\n✅ Successfully imported {total} total companies to database!'))
        
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'❌ CSV file not found: {csv_file}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {str(e)}'))
