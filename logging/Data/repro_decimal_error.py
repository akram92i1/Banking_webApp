import json
from decimal import Decimal
import datetime

# Mocking the behavior of execute_sql_query
def test_serialization():
    # Simulate a row from the database
    # Assuming the schema: account_id, balance (Decimal), created_at (datetime)
    row = (1, Decimal('100.50'), datetime.datetime.now())
    colnames = ['account_id', 'balance', 'created_at']
    
    data = []
    row_dict = {}
    
    print("Attempting to serialize row containing Decimal...")
    
    try:
        for i, val in enumerate(row):
            # Existing logic from the user's file
            if hasattr(val, 'isoformat'):
                row_dict[colnames[i]] = val.isoformat()
            else:
                row_dict[colnames[i]] = val
        data.append(row_dict)
        
        # This should fail
        json_output = json.dumps(data, indent=2)
        print("Serialization Successful (Unexpected):")
        print(json_output)
        
    except TypeError as e:
        print(f"Caught expected error: {e}")
    except Exception as e:
        print(f"Caught unexpected error: {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_serialization()
