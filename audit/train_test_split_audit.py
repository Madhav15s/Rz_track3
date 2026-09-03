import pandas as pd

def audit_split():
    df = pd.read_csv("data/raw/observed_data.csv")
    
    train_custs = set(df[df['split'] == 'train']['customer_id'])
    val_custs = set(df[df['split'] == 'val']['customer_id'])
    test_custs = set(df[df['split'] == 'test']['customer_id'])
    
    overlap_train_val = train_custs.intersection(val_custs)
    overlap_train_test = train_custs.intersection(test_custs)
    overlap_val_test = val_custs.intersection(test_custs)
    
    print("Train vs Val overlap:", len(overlap_train_val))
    print("Train vs Test overlap:", len(overlap_train_test))
    print("Val vs Test overlap:", len(overlap_val_test))
    
    if len(overlap_train_val) > 0 or len(overlap_train_test) > 0 or len(overlap_val_test) > 0:
        print("FAIL: Customer overlap detected!")
        exit(1)
    else:
        print("PASS: No customer overlap.")
        
if __name__ == "__main__":
    audit_split()
