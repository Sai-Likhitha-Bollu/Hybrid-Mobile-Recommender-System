import pandas as pd
import numpy as np
import random
import re

# --- Load your data ---
df2 = pd.read_csv("D:\Project\Data\Mobiles Dataset (2025).csv")   # update filename if needed
df3 = pd.read_csv("D:\Project\Data\smartphone_cleaned_v5.csv")   # update filename if needed
print("DF2 columns:", df2.columns)
print("DF3 columns:", df3.columns)

# --- Step 1: Fix duplicate column names ---
def fix_duplicate_columns(df):
    """Fix duplicate column names by adding suffix"""
    cols = df.columns.tolist()
    seen = {}
    for i, col in enumerate(cols):
        if col in seen:
            seen[col] += 1
            cols[i] = f"{col}_{seen[col]}"
        else:
            seen[col] = 0
    df.columns = cols
    return df

if not df2.columns.is_unique:
    df2 = fix_duplicate_columns(df2)

if not df3.columns.is_unique:
    df3 = fix_duplicate_columns(df3)

# --- Step 2: Rename df2 columns to align with df3 ---
rename_map = {
    "Company Name": "brand_name",
    "Model Name": "model",
    "Mobile Weight": "weight",
    "RAM": "ram_capacity",
    "Front Camera": "primary_camera_front",
    "Back Camera": "primary_camera_rear",
    "Processor": "processor_brand",
    "Battery Capacity": "battery_capacity",
    "Screen Size": "screen_size",
    "Launched Year": "launch_year"
}
df2 = df2.rename(columns=rename_map)

# --- Step 3: Standardize price ---
price_cols = [col for col in df2.columns if "Launched Price" in col]
if price_cols:
    df2["price"] = df2[price_cols[0]]   # keep the first available
    df2 = df2.drop(columns=price_cols)

# --- Step 4: Add missing columns from df3 into df2 ---
for col in df3.columns:
    if col not in df2.columns:
        df2[col] = pd.NA

# --- Step 5: Reorder df2 to match df3 ---
df2 = df2[df3.columns]

# --- Step 6: Concatenate both datasets ---
combined = pd.concat([df3, df2], ignore_index=True, sort=False)

# --- Step 7: Standardize memory fields ---
def clean_memory(value):
    """
    Convert memory strings like '8GB', '128 GB', '1 TB' to integers in GB.
    """
    if pd.isna(value):
        return np.nan
    value = str(value).strip().upper()
    
    match = re.match(r"(\d+\.?\d*)\s*(GB|TB)", value)
    if match:
        num, unit = match.groups()
        num = float(num)
        if unit == "TB":
            num *= 1024
        return int(num)
    
    # if it's just a number
    try:
        return int(value)
    except ValueError:
        return np.nan

if "ram_capacity" in combined.columns:
    combined["ram_capacity"] = combined["ram_capacity"].apply(clean_memory)
if "internal_memory" in combined.columns:
    combined["internal_memory"] = combined["internal_memory"].apply(clean_memory)

# --- Step 8: Inject fake ratings where missing ---
def random_rating():
    return round(random.uniform(6.0, 9.0), 1)

if "rating" in combined.columns:
    combined["rating"] = combined["rating"].apply(
        lambda x: random_rating() if pd.isna(x) else x
    )

# --- Step 9: Save final dataset ---
print("✅ Combined DataFrame created successfully!")
print("Final columns:", combined.columns.tolist())
print("Shape:", combined.shape)
combined.to_csv("final_dataset.csv", index=False)
print("💾 Saved as final_dataset.csv")