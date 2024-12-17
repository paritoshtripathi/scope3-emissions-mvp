import os
import pandas as pd
import random

# Output directory for generated CSV files
OUTPUT_DIR = "ai-ml/kb/generated_data"

# Utility: Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. Generate Data for Purchased Goods and Services (Category 1)
def generate_purchased_goods_data(num_rows=100):
    data = []
    for _ in range(num_rows):
        data.append({
            "Item Name": random.choice(["Steel", "Electronics", "Paper", "Food", "Furniture"]),
            "Supplier Name": f"Supplier-{random.randint(1, 50)}",
            "Quantity Purchased": random.randint(100, 10000),
            "Unit of Measure": random.choice(["kg", "liters", "units"]),
            "Emission Factor (kg CO₂e)": round(random.uniform(0.5, 5.0), 2),
            "Transportation Mode": random.choice(["Sea", "Air", "Road", "Rail"]),
            "Total Emissions (kg CO₂e)": round(random.uniform(500, 5000), 2),
        })
    return pd.DataFrame(data)

# 2. Generate Data for Transportation (Categories 4 & 9)
def generate_transportation_data(num_rows=100):
    data = []
    for _ in range(num_rows):
        data.append({
            "Transport Type": random.choice(["Upstream", "Downstream"]),
            "Mode of Transport": random.choice(["Sea", "Air", "Road", "Rail"]),
            "Distance (km)": random.randint(100, 5000),
            "Weight of Goods (kg)": random.randint(1000, 10000),
            "Emission Factor (kg CO₂e/km/kg)": round(random.uniform(0.001, 0.01), 4),
            "Total Emissions (kg CO₂e)": round(random.uniform(500, 5000), 2),
        })
    return pd.DataFrame(data)

# 3. Generate Data for Business Travel (Category 6)
def generate_business_travel_data(num_rows=100):
    data = []
    for _ in range(num_rows):
        data.append({
            "Employee ID": f"EMP-{random.randint(100, 999)}",
            "Travel Type": random.choice(["Air", "Rail", "Car"]),
            "Distance (km)": random.randint(200, 5000),
            "Trip Duration (days)": random.randint(1, 14),
            "Emission Factor (kg CO₂e/km)": round(random.uniform(0.1, 0.3), 2),
            "Total Emissions (kg CO₂e)": round(random.uniform(50, 1500), 2),
        })
    return pd.DataFrame(data)

# 4. Generate Data for Employee Commuting (Category 7)
def generate_employee_commuting_data(num_rows=100):
    data = []
    for _ in range(num_rows):
        data.append({
            "Employee ID": f"EMP-{random.randint(100, 999)}",
            "Commute Type": random.choice(["Car", "Bus", "EV", "Bicycle"]),
            "Distance Per Trip (km)": random.randint(5, 50),
            "Frequency (days/week)": random.randint(3, 5),
            "Emission Factor (kg CO₂e/km)": round(random.uniform(0.05, 0.2), 2),
            "Total Emissions (kg CO₂e)": round(random.uniform(10, 500), 2),
        })
    return pd.DataFrame(data)

# 5. Generate Data for Waste Generated (Category 5)
def generate_waste_data(num_rows=100):
    data = []
    for _ in range(num_rows):
        data.append({
            "Waste Type": random.choice(["Plastic", "Organic", "Metal", "Glass", "Paper"]),
            "Quantity Generated (kg)": random.randint(100, 5000),
            "Disposal Method": random.choice(["Landfill", "Incineration", "Recycle"]),
            "Emission Factor (kg CO₂e/kg)": round(random.uniform(0.5, 2.0), 2),
            "Total Emissions (kg CO₂e)": round(random.uniform(50, 1000), 2),
        })
    return pd.DataFrame(data)

# Main Function to Generate and Save Data
def generate_and_save_data():
    print("Generating mock data for Scope 3 categories...")

    # Generate data for each category
    purchased_goods_df = generate_purchased_goods_data()
    transportation_df = generate_transportation_data()
    business_travel_df = generate_business_travel_data()
    commuting_df = generate_employee_commuting_data()
    waste_df = generate_waste_data()

    # Save as CSV files
    purchased_goods_df.to_csv(os.path.join(OUTPUT_DIR, "purchased_goods.csv"), index=False)
    transportation_df.to_csv(os.path.join(OUTPUT_DIR, "transportation.csv"), index=False)
    business_travel_df.to_csv(os.path.join(OUTPUT_DIR, "business_travel.csv"), index=False)
    commuting_df.to_csv(os.path.join(OUTPUT_DIR, "employee_commuting.csv"), index=False)
    waste_df.to_csv(os.path.join(OUTPUT_DIR, "waste_generated.csv"), index=False)

    print(f"Data generated successfully! Files saved in {OUTPUT_DIR}")

if __name__ == "__main__":
    generate_and_save_data()
