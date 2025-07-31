# scripts/utils.py
import pandas as pd
import os
import re
from datetime import datetime
import plotly.io as pio
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import arabic_reshaper
from bidi.algorithm import get_display

np.random.seed(42)

# تحديد مسار المشروع الرئيسي
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_figures_dir = os.path.join(base_dir, "outputs", "figures")
default_reports_dir = os.path.join(base_dir, "outputs", "reports")
default_processed_data_dir = os.path.join(base_dir, "data", "processed")

def load_data(file_path):
    """
    دالة لتحميل البيانات من ملف CSV.
    
    Args:
        file_path (str): مسار ملف CSV.
    
    Returns:
        pandas.DataFrame: إطار بيانات محمل.
    
    Raises:
        FileNotFoundError: إذا لم يتم العثور على الملف.
    """
    try:
        df = pd.read_csv(file_path)
        print(f"تم تحميل البيانات بنجاح من: {file_path}")
        return df
    except FileNotFoundError:
        print(f"خطأ: الملف {file_path} غير موجود!")
        raise
    except Exception as e:
        print(f"خطأ أثناء تحميل البيانات: {e}")
        raise

def clean_column_names(df):
    """
    دالة لتنظيف أسماء الأعمدة (إزالة المسافات، تحويل إلى حروف صغيرة، إزالة الرموز).
    
    Args:
        df (pandas.DataFrame): إطار البيانات.
    
    Returns:
        pandas.DataFrame: إطار بيانات بأسماء أعمدة نظيفة.
    """
    df.columns = [re.sub(r'[^a-zA-Z0-9_]', '_', col.lower().strip()) for col in df.columns]
    print("تم تنظيف أسماء الأعمدة بنجاح.")
    return df

def save_figure(fig, filename, output_dir=default_figures_dir):
    """
    دالة لحفظ الرسوم البيانية بصيغتي HTML و PNG.
    
    Args:
        fig: كائن Plotly للرسم البياني.
        filename (str): اسم الملف (بدون الامتداد).
        output_dir (str): مسار مجلد الإخراج.
    
    Returns:
        str: مسار ملف PNG.
    """
    os.makedirs(output_dir, exist_ok=True)
    date_suffix = datetime.now().strftime("%Y%m%d")
    html_path = os.path.join(output_dir, f"{filename}_{date_suffix}.html")
    png_path = os.path.join(output_dir, f"{filename}_{date_suffix}.png")
    
    fig.write_html(html_path)
    fig.write_image(png_path)
    print(f"تم حفظ الرسم البياني في: {html_path} و {png_path}")
    return png_path

def save_dataframe(df, filename, output_dir=default_processed_data_dir):
    """
    دالة لحفظ إطار البيانات كملف CSV.
    
    Args:
        df (pandas.DataFrame): إطار البيانات.
        filename (str): اسم الملف (بدون الامتداد).
        output_dir (str): مسار مجلد الإخراج.
    """
    os.makedirs(output_dir, exist_ok=True)
    date_suffix = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(output_dir, f"{filename}_{date_suffix}.csv")
    df.to_csv(output_path, index=False)
    print(f"تم حفظ البيانات في: {output_path}")

def save_report(figures, title, filename, output_dir=default_reports_dir):
    """
    دالة لحفظ تقرير PDF مرتب باللغة العربية.
    
    Args:
        figures (list): قائمة من كائنات Plotly.
        title (str): عنوان التقرير.
        filename (str): اسم الملف (بدون الامتداد).
        output_dir (str): مسار مجلد الإخراج.
    """
    os.makedirs(output_dir, exist_ok=True)
    date_suffix = datetime.now().strftime("%Y%m%d")
    output_path = os.path.join(output_dir, f"{filename}_{date_suffix}.pdf")
    
    doc = SimpleDocTemplate(output_path, pagesize=A4, rightMargin=inch, leftMargin=inch, topMargin=inch, bottomMargin=inch)
    styles = getSampleStyleSheet()
    
    arabic_style = ParagraphStyle(
        name='Arabic',
        parent=styles['Normal'],
        fontName='Helvetica',  # يمكن استخدام خط Amiri إذا تم تثبيته
        fontSize=12,
        leading=14,
        alignment=2,  # محاذاة يمين
        spaceAfter=12
    )
    
    def reshape_arabic(text):
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    
    elements = []
    elements.append(Paragraph(reshape_arabic(title), ParagraphStyle(name='Title', fontSize=16, alignment=2)))
    elements.append(Spacer(1, 0.2 * inch))
    
    intro_text = """
    هذا التقرير يحتوي على تحليل بيانات إنتاج النفط، بما في ذلك الرسوم البيانية التي توضح العلاقات بين المتغيرات المختلفة.
    يتضمن التقرير هيستوغرامات، رسوم مبعثرة، رسوم صندوقية، خرائط حرارية، وسلاسل زمنية لتحليل البيانات.
    """
    elements.append(Paragraph(reshape_arabic(intro_text), arabic_style))
    elements.append(Spacer(1, 0.2 * inch))
    
    for i, fig in enumerate(figures):
        temp_png = save_figure(fig, f"temp_fig_{i}", output_dir=os.path.join(base_dir, "outputs", "figures"))
        fig_title = reshape_arabic(fig.layout.title.text)
        elements.append(Paragraph(fig_title, arabic_style))
        img = Image(temp_png, width=6*inch, height=4*inch)
        elements.append(img)
        elements.append(Spacer(1, 0.2 * inch))
    
    doc.build(elements)
    print(f"تم حفظ التقرير في: {output_path}")

def create_histogram(df, column):
    """
    دالة لإنشاء هيستوغرام.
    
    Args:
        df (pandas.DataFrame): إطار البيانات.
        column (str): العمود المراد رسمه.
    
    Returns:
        plotly.graph_objects.Figure: الرسم البياني.
    """
    fig = px.histogram(df, x=column, title=f"توزيع {column}",
                       labels={column: column}, nbins=30)
    fig.update_layout(xaxis_title=column, yaxis_title="العدد", title_x=0.5)
    return fig

def create_scatter(df, x_col, y_col, color_col=None):
    """
    دالة لإنشاء رسم مبعثر.
    
    Args:
        df (pandas.DataFrame): إطار البيانات.
        x_col (str): العمود للمحور السيني.
        y_col (str): العمود للمحور الصادي.
        color_col (str): العمود للتلوين (اختياري).
    
    Returns:
        plotly.graph_objects.Figure: الرسم البياني.
    """
    fig = px.scatter(df, x=x_col, y=y_col, color=color_col,
                     title=f"{y_col} مقابل {x_col}",
                     labels={x_col: x_col, y_col: y_col})
    fig.update_layout(title_x=0.5)
    return fig

def create_boxplot(df, column, group_by=None):
    """
    دالة لإنشاء رسم صندوقي.
    
    Args:
        df (pandas.DataFrame): إطار البيانات.
        column (str): العمود المراد رسمه.
        group_by (str): العمود للتجميع (اختياري).
    
    Returns:
        plotly.graph_objects.Figure: الرسم البياني.
    """
    fig = px.box(df, x=group_by, y=column, title=f"صندوقي لـ {column}",
                 labels={column: column, group_by: group_by})
    fig.update_layout(title_x=0.5)
    return fig

def create_heatmap(df, numeric_cols):
    """
    دالة لإنشاء خريطة حرارية للارتباطات.
    
    Args:
        df (pandas.DataFrame): إطار البيانات.
        numeric_cols (list): قائمة الأعمدة الرقمية.
    
    Returns:
        plotly.graph_objects.Figure: الرسم البياني.
    """
    corr = df[numeric_cols].corr()
    fig = go.Figure(data=go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.columns,
        colorscale='Viridis'))
    fig.update_layout(title="خريطة حرارية للارتباطات", title_x=0.5)
    return fig

def create_timeseries(df, date_col, value_col):
    """
    دالة لإنشاء سلسلة زمنية.
    
    Args:
        df (pandas.DataFrame): إطار البيانات.
        date_col (str): عمود التاريخ.
        value_col (str): العمود المراد رسمه.
    
    Returns:
        plotly.graph_objects.Figure: الرسم البياني.
    """
    fig = px.line(df, x=date_col, y=value_col, title=f"سلسلة زمنية لـ {value_col}",
                  labels={date_col: "التاريخ", value_col: value_col})
    fig.update_layout(title_x=0.5)
    return fig