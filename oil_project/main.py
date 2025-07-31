# main.py
import os
import sys
import glob
from datetime import datetime
import argparse

# إضافة المسار إلى مجلد scripts لاستيراد الوحدات
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))

# استيراد الدوال الرئيسية من الوحدات
from oil_project.scripts.cleaning import main as clean_data
from oil_project.scripts.eda import main as perform_eda
from oil_project.scripts.modeling import main as train_model
from oil_project.scripts.dashboard import main as run_dashboard  # استيراد لوحة التحكم
from oil_project.scripts.utils import load_data, save_dataframe

def get_latest_cleaned_file(base_dir):
    """
    دالة للعثور على أحدث ملف بيانات منظف بناءً على التاريخ في اسم الملف.

    Args:
        base_dir (str): المسار الأساسي للمشروع.

    Returns:
        str or None: مسار أحدث ملف بيانات منظف، أو None إذا لم يتم العثور على ملفات.
    """
    data_dir = os.path.join(base_dir, "data", "processed")
    try:
        # البحث عن ملفات باسم يبدأ بـ "cleaned_oil_field_production_data_" وينتهي بـ ".csv"
        files = glob.glob(os.path.join(data_dir, "cleaned_oil_field_production_data_*.csv"))
        if not files:
            print("لم يتم العثور على ملفات بيانات منظفة!")
            return None
        # اختيار الملف الأحدث بناءً على وقت التعديل
        latest_file = max(files, key=os.path.getmtime)
        print(f"أحدث ملف بيانات منظف: {latest_file}")
        return latest_file
    except Exception as e:
        print(f"خطأ أثناء البحث عن الملفات: {e}")
        return None

def main():
    """
    الدالة الرئيسية لتشغيل المشروع بالكامل، بما في ذلك تنظيف البيانات، التحليل الاستكشافي،
    النمذجة، وتشغيل لوحة التحكم التفاعلية.
    """
    # إعداد تحليل الوسائط باستخدام argparse
    parser = argparse.ArgumentParser(description="تشغيل مشروع تحليل بيانات النفط.")
    parser.add_argument('--steps', nargs='+', default=['clean', 'eda', 'model', 'dashboard'],
                        choices=['clean', 'eda', 'model', 'dashboard'],
                        help="الخطوات المطلوب تنفيذها: clean, eda, model, dashboard")
    args = parser.parse_args()

    print(f"\n=== بدء تشغيل مشروع تحليل بيانات النفط ===")
    print(f"الخطوات المحددة: {args.steps}\n")

    # تحديد المسار الأساسي للمشروع
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    # خطوة تنظيف البيانات
    if 'clean' in args.steps:
        print("--- تنفيذ خطوة تنظيف البيانات ---")
        try:
            clean_data()
        except Exception as e:
            print(f"خطأ أثناء تنظيف البيانات: {e}")
            return

    # الحصول على أحدث ملف بيانات منظفة لخطوات eda، model، وdashboard
    if any(step in args.steps for step in ['eda', 'model', 'dashboard']):
        latest_file = get_latest_cleaned_file(base_dir)
        if not latest_file:
            print("تخطي خطوات التحليل، النمذجة، ولوحة التحكم بسبب عدم وجود بيانات منظفة.")
            return

        # خطوة التحليل الاستكشافي
        if 'eda' in args.steps:
            print("--- تنفيذ خطوة التحليل الاستكشافي ---")
            try:
                perform_eda(latest_file)
            except Exception as e:
                print(f"خطأ أثناء التحليل الاستكشافي: {e}")
                return

        # خطوة النمذجة
        if 'model' in args.steps:
            print("--- تنفيذ خطوة النمذجة ---")
            try:
                train_model(latest_file)
            except Exception as e:
                print(f"خطأ أثناء النمذجة: {e}")
                return

        # خطوة تشغيل لوحة التحكم
        if 'dashboard' in args.steps:
            print("--- تنفيذ خطوة تشغيل لوحة التحكم التفاعلية ---")
            try:
                run_dashboard(latest_file)
            except Exception as e:
                print(f"خطأ أثناء تشغيل لوحة التحكم: {e}")
                return

    print("\n=== اكتمل تشغيل المشروع بنجاح ===")

if __name__ == "__main__":
    main()