import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns
import matplotlib.pyplot as plt
from oil_project.scripts.utils import load_data, save_figure, save_dataframe
import numpy as np

np.random.seed(42)

# تحديد مسار المشروع الرئيسي بشكل ديناميكي
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
outputs_dir = os.path.join(base_dir, "outputs", "figures")  # تغيير إلى figures

def create_histogram(df, column):
    fig = px.histogram(df, x=column, title=f"توزيع {column}",
                       labels={column: column}, nbins=30)
    fig.update_layout(xaxis_title=column, yaxis_title="العدد")
    return fig

def create_scatter(df, x_col, y_col, color_col=None):
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                     title=f"{y_col} مقابل {x_col}",
                     labels={x_col: x_col, y_col: y_col})
    return fig

def create_boxplot(df, column, group_by=None):
    fig = px.box(df, x=group_by, y=column, title=f"صندوقي لـ {column}",
                 labels={column: column, group_by: group_by})
    return fig

def create_heatmap(df, numeric_cols):
    corr = df[numeric_cols].corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.columns,
        colorscale='Viridis'))
    fig.update_layout(title="خريطة حرارية للارتباطات")
    return fig

def create_timeseries(df, date_col, value_col):
    fig = px.line(df, x=date_col, y=value_col, title=f"سلسلة زمنية لـ {value_col}",
                  labels={date_col: "التاريخ", value_col: value_col})
    return fig

def main(input_path=None):
    """
    الدالة الرئيسية لإجراء التحليل الاستكشافي.
    Args:
        input_path (str, optional): مسار ملف البيانات المنظف. إذا لم يُحدد، يتم استخدام المسار الافتراضي.
    """
    if input_path is None:
        input_path = os.path.join(base_dir, "data", "processed", "cleaned_oil_field_production_data_20250731.csv")
    
    print(f"\n--- تحميل البيانات من: {input_path} ---")
    df = load_data(input_path)

    print("\n--- الإحصاءات الوصفية ---")
    print(df.describe())

    numeric_cols = ['oil_production_bbl', 'gas_production_mcf', 'water_production_bbl', 
                    'wellhead_pressure_psi', 'tubing_pressure_psi', 'choke_size_in', 'pump_efficiency__']
    numeric_cols = [col for col in numeric_cols if col in df.columns]

    # إنشاء الرسوم البيانية
    fig_hist = create_histogram(df, "oil_production_bbl")
    save_figure(fig_hist, "histogram", output_dir=outputs_dir)

    fig_scatter = create_scatter(df, "wellhead_pressure_psi", "oil_production_bbl", color_col="field_name")
    save_figure(fig_scatter, "scatter", output_dir=outputs_dir)

    fig_box = create_boxplot(df, "oil_production_bbl", group_by="field_name")
    save_figure(fig_box, "boxplot", output_dir=outputs_dir)

    fig_heatmap = create_heatmap(df, numeric_cols)
    save_figure(fig_heatmap, "heatmap", output_dir=outputs_dir)

    if 'date' in df.columns:
        fig_timeseries = create_timeseries(df, "date", "oil_production_bbl")
        save_figure(fig_timeseries, "timeseries", output_dir=outputs_dir)

    # إنشاء لوحة تحكم تفاعلية
    dashboard = make_subplots(rows=3, cols=2,
                              subplot_titles=("هيستوغرام إنتاج النفط", "رسم مبعثر",
                                              "رسم صندوقي", "خريطة حرارية", "سلسلة زمنية"))

    dashboard.add_trace(fig_hist.data[0], row=1, col=1)
    dashboard.add_trace(fig_scatter.data[0], row=1, col=2)
    dashboard.add_trace(fig_box.data[0], row=2, col=1)
    dashboard.add_trace(fig_heatmap.data[0], row=2, col=2)
    if 'date' in df.columns:
        dashboard.add_trace(fig_timeseries.data[0], row=3, col=1)

    dashboard.update_layout(height=1200, width=1200, title_text="لوحة تحكم تحليل بيانات الحقل النفطي")
    save_figure(dashboard, "dashboard", output_dir=outputs_dir)

if __name__ == "__main__":
    main()