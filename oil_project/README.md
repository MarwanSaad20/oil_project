# مشروع تحليل ونمذجة بيانات إنتاج الحقول النفطية

## الهدف
يهدف هذا المشروع إلى تحليل بيانات إنتاج الحقول النفطية بشكل شامل من خلال:
1. **تنظيف البيانات**: معالجة القيم المفقودة والشاذة لضمان جودة البيانات.
2. **تحليل استكشافي (EDA)**: إنشاء رسوم بيانية تفاعلية (Histogram، Scatter، Boxplot، Heatmap، Time Series) باستخدام **Plotly** لفهم أنماط البيانات.
3. **نمذجة تنبؤية**: بناء نموذج **Random Forest** للتنبؤ بإنتاج النفط بناءً على ميزات مثل الضغط، حجم الحاجز، وكفاءة المضخة.
4. **لوحة تحكم تفاعلية**: عرض التحليلات والرؤى في لوحة تحكم باستخدام **Dash**، مع خيارات تصفية حسب الحقل النفطي والفترة الزمنية.
5. **إنشاء تقارير**: إنتاج تقارير PDF تحتوي على نتائج النمذجة والتحليلات، مع دعم كامل للغة العربية.

المشروع مصمم ليكون احترافيًا، قابلًا للتكرار، وسهل التوسع، مع هيكلية منظمة تدعم إضافة ميزات جديدة.

## هيكل المشروع
oil_project/
├── data/
│   ├── raw/
│   │   └── oil_field_production_data.csv (البيانات الأصلية)
│   └── processed/
│       └── cleaned_oil_field_production_data_YYYYMMDD.csv (البيانات المنظفة)
├── scripts/
│   ├── cleaning.py (تنظيف البيانات ومعالجة القيم المفقودة والشاذة)
│   ├── eda.py (تحليل استكشافي وإنشاء رسوم بيانية)
│   ├── dashboard.py (لوحة تحكم تفاعلية باستخدام Dash)
│   ├── modeling.py (نمذجة تنبؤية باستخدام Random Forest)
│   └── utils.py (دوال مساعدة لتحميل البيانات، إنشاء الرسوم، والتقارير)
├── outputs/
│   ├── figures/
│   │   ├── histogram_YYYYMMDD.html/png (توزيع إنتاج النفط)
│   │   ├── scatter_YYYYMMDD.html/png (علاقة الضغط بإنتاج النفط)
│   │   ├── boxplot_YYYYMMDD.html/png (توزيع الإنتاج حسب الحقل)
│   │   ├── heatmap_YYYYMMDD.html/png (مصفوفة الارتباط)
│   │   ├── timeseries_YYYYMMDD.html/png (تطور الإنتاج بمرور الوقت)
│   │   ├── dashboard_YYYYMMDD.html/png (لوحة تحكم ثابتة)
│   │   ├── predictions_vs_actual_YYYYMMDD.html/png (تنبؤات النموذج مقابل القيم الحقيقية)
│   │   ├── feature_importance_YYYYMMDD.html/png (أهمية الميزات في النموذج)
│   │   ├── temp_fig_0_YYYYMMDD.html/png (رسوم إضافية للنمذجة)
│   │   └── temp_fig_1_YYYYMMDD.html/png (رسوم إضافية للنمذجة)
│   └── reports/
│       └── modeling_report_YYYYMMDD.pdf (تقرير نتائج النمذجة)
├── main.py (نقطة الدخول الرئيسية لتشغيل المشروع)
├── requirements.txt (المكتبات المطلوبة)
└── README.md (هذا الملف)



## متطلبات التشغيل
- **Python**: الإصدار 3.8 أو أحدث.
- **المكتبات المطلوبة** (مدرجة في `requirements.txt`):
  ```text
  pandas>=2.0.0
  numpy>=1.23.0
  plotly>=5.10.0
  dash>=2.9.0
  dash-bootstrap-components>=1.4.0
  reportlab>=3.6.0
  arabic-reshaper>=3.0.0
  python-bidi>=0.4.2
  scikit-learn>=1.2.0
  seaborn>=0.12.0
  matplotlib>=3.5.0
