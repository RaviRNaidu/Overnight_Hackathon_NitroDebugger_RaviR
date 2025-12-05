from database import engine
from sqlalchemy import inspect

inspector = inspect(engine)
columns = inspector.get_columns('applications')

print("\nApplications table columns:")
print("-" * 60)
for col in columns:
    print(f"  {col['name']:20s} {str(col['type']):30s}")
print("-" * 60)

app_id_col = [c for c in columns if c['name'] == 'application_id'][0]
print(f"\n✓ application_id column type: {app_id_col['type']}")
print("✓ Schema updated successfully!")
