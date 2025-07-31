import os
import pandas as pd
import numpy as np
from scipy import stats
from oil_project.scripts.utils import load_data, clean_column_names, save_dataframe

# تحديد seed للتكرارية
np.random.seed(42)

# تحديد مسار المشروع الرئيسي بشكل ديناميكي
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
input_path = os.path.join(base_dir, "data", "raw", "oil_field_production_data.csv")

def handle_missing_values(df):
    """
    دالة لمعالجة القيم المفقودة في إطار البيانات.
    """
    print("\n--- معالجة القيم المفقودة ---")
    print("نسبة القيم المفقودة لكل عمود:")
    print(df.isnull().mean() * 100)
    
    # ملء القيم المفقودة للأعمدة الرقمية بالمتوسط
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].mean())
    
    # إسقاط الصفوف التي تحتوي على قيم مفقودة في الأعمدة غير الرقمية
    non_numeric_cols = df.select_dtypes(exclude=[np.number]).columns
    df.dropna(subset=non_numeric_cols, inplace=True)
    
    print("تمت معالجة القيم المفقودة.")
    return df

def handle_outliers(df, columns, method="IQR"):
    """
    دالة لمعالجة القيم الشاذة باستخدام IQR أو Z-score.
    """
    print("\n--- معالجة القيم الشاذة ---")
    for col in columns:
        if method == "IQR":
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        elif method == "zscore":
            z_scores = np.abs(stats.zscore(df[col]))
            df[col] = df[col].where(z_scores < 3, df[col].mean())
        print(f"تم معالجة القيم الشاذة في العمود: {col}")
    return df

def main():
    """
    الدالة الرئيسية لتنظيف البيانات.
    """
    # تحميل البيانات
    print(f"\n--- تحميل البيانات من: {input_path} ---")
    df = load_data(input_path)
    
    # ملخص قبل التنظيف
    print("\n--- ملخص البيانات قبل التنظيف ---")
    print(df.info())
    print("\nالإحصاءات الوصفية:")
    print(df.describe())
    
    # تنظيف أسماء الأعمدة
    df = clean_column_names(df)
    
    # تحويل العمود date إلى datetime إذا وجد
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        print("تم تحويل عمود 'date' إلى صيغة datetime.")
    
    # معالجة القيم المفقودة
    df = handle_missing_values(df)
    
    # معالجة القيم الشاذة للأعمدة الرقمية
    numeric_cols = ['oil_production_bbl', 'gas_production_mcf', 'water_production_bbl', 
                    'wellhead_pressure_psi', 'tubing_pressure_psi', 'choke_size_in', 'pump_efficiency__']
    numeric_cols = [col for col in numeric_cols if col in df.columns]
    df = handle_outliers(df, numeric_cols, method="IQR")
    
    # ملخص بعد التنظيف
    print("\n--- ملخص البيانات بعد التنظيف ---")
    print(df.info())
    print("\nالإحصاءات الوصفية:")
    print(df.describe())
    
    # حفظ البيانات المنظفة في المسار الصحيح
    output_dir = os.path.join(base_dir, "data", "processed")
    save_dataframe(df, "cleaned_oil_field_production_data", output_dir=output_dir)

if __name__ == "__main__":
    main()