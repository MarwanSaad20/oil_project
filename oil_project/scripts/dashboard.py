# dashboard.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import os
from oil_project.scripts.utils import load_data, create_histogram, create_scatter, create_boxplot, create_heatmap, create_timeseries

# تحديد seed للتكرارية
np.random.seed(42)

def main(input_path=None):
    """
    الدالة الرئيسية لتشغيل لوحة التحكم التفاعلية.

    Args:
        input_path (str, optional): مسار ملف البيانات المنظفة. إذا لم يُحدد، يتم استخدام المسار الافتراضي.
    """
    # تحديد مسار المشروع الرئيسي
    base_dir = os.path.dirname(os.path.abspath(__file__))
    if input_path is None:
        input_path = os.path.join(base_dir, "data", "processed", "cleaned_oil_field_production_data_20250731.csv")

    # تهيئة تطبيق Dash مع قالب Flatly من Bootstrap
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

    # تحميل البيانات
    try:
        df = load_data(input_path)
    except Exception as e:
        print(f"خطأ أثناء تحميل البيانات: {e}")
        return

    # تحديد الأعمدة الرقمية
    numeric_cols = ['oil_production_bbl', 'gas_production_mcf', 'water_production_bbl', 
                    'wellhead_pressure_psi', 'tubing_pressure_psi', 'choke_size_in', 'pump_efficiency__']

    # تحويل عمود التاريخ إلى datetime
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    # إعداد خيارات التصفية
    field_options = [{'label': field, 'value': field} for field in df['field_name'].unique()]
    date_range = pd.date_range(start=df['date'].min(), end=df['date'].max(), freq='D')

    # تصميم الشريط الجانبي
    sidebar = html.Div(
        [
            html.H3("خيارات التصفية", className="display-4", style={'textAlign': 'right'}),
            html.Hr(),
            html.Label("اختر الحقل النفطي:", style={'textAlign': 'right'}),
            dcc.Dropdown(
                id='field-filter',
                options=[{'label': 'الكل', 'value': 'all'}] + field_options,
                value='all',
                style={'textAlign': 'right'},
            ),
            html.Br(),
            html.Label("اختر الفترة الزمنية:", style={'textAlign': 'right'}),
            dcc.DatePickerRange(
                id='date-picker',
                min_date_allowed=df['date'].min(),
                max_date_allowed=df['date'].max(),
                initial_visible_month=df['date'].max(),
                start_date=df['date'].min(),
                end_date=df['date'].max(),
                style={'direction': 'rtl'}
            ),
        ],
        style={
            'padding': '20px',
            'backgroundColor': '#f8f9fa',
            'height': '100vh',
            'textAlign': 'right'
        }
    )

    # تصميم المقاييس الرئيسية (KPIs)
    def create_kpis(df_filtered):
        """
        دالة لإنشاء المقاييس الرئيسية (KPIs) بناءً على البيانات المصفاة.

        Args:
            df_filtered (pandas.DataFrame): إطار البيانات بعد التصفية.

        Returns:
            dash.html.Div: عنصر يحتوي على المقاييس الرئيسية.
        """
        total_oil = df_filtered['oil_production_bbl'].sum()
        avg_daily_oil = df_filtered['oil_production_bbl'].mean()
        active_wells = df_filtered[df_filtered['status'] == 'Active']['well_id'].nunique()
        
        return html.Div([
            dbc.Row([
                dbc.Col(html.Div([
                    html.H5("إجمالي إنتاج النفط (برميل)", style={'textAlign': 'center'}),
                    html.H3(f"{total_oil:,.2f}", style={'textAlign': 'center', 'color': '#007bff'})
                ], className="border rounded p-3")),
                dbc.Col(html.Div([
                    html.H5("متوسط الإنتاج اليومي (برميل)", style={'textAlign': 'center'}),
                    html.H3(f"{avg_daily_oil:,.2f}", style={'textAlign': 'center', 'color': '#28a745'})
                ], className="border rounded p-3")),
                dbc.Col(html.Div([
                    html.H5("عدد الآبار النشطة", style={'textAlign': 'center'}),
                    html.H3(f"{active_wells}", style={'textAlign': 'center', 'color': '#dc3545'})
                ], className="border rounded p-3")),
            ])
        ])

    # تصميم صفحة التحليل الوصفي (Insights)
    def create_insights(df_filtered):
        """
        دالة لإنشاء صفحة الرؤى التحليلية بناءً على البيانات المصفاة.

        Args:
            df_filtered (pandas.DataFrame): إطار البيانات بعد التصفية.

        Returns:
            dash.html.Div: عنصر يحتوي على الرؤى التحليلية.
        """
        insights = [
            f"إجمالي إنتاج النفط: {df_filtered['oil_production_bbl'].sum():,.2f} برميل",
            f"متوسط إنتاج النفط اليومي: {df_filtered['oil_production_bbl'].mean():,.2f} برميل",
            f"عدد الآبار النشطة: {df_filtered[df_filtered['status'] == 'Active']['well_id'].nunique()}",
            f"أعلى حقل إنتاجي: {df_filtered.groupby('field_name')['oil_production_bbl'].sum().idxmax()}",
            f"الارتباط بين الضغط وإنتاج النفط: {df_filtered['wellhead_pressure_psi'].corr(df_filtered['oil_production_bbl']):.2f}"
        ]
        return html.Div([
            html.H3("رؤى تحليلية", style={'textAlign': 'right'}),
            html.Ul([html.Li(insight, style={'textAlign': 'right'}) for insight in insights])
        ])

    # تصميم التخطيط الرئيسي
    app.layout = dbc.Container([
        dbc.Row([
            # الشريط الجانبي (25% من العرض)
            dbc.Col(sidebar, width=3),
            # المحتوى الرئيسي
            dbc.Col([
                html.H1("لوحة تحكم تحليل بيانات الحقل النفطي", style={'textAlign': 'center'}),
                html.Hr(),
                # المقاييس الرئيسية
                html.Div(id='kpis'),
                html.Hr(),
                # الرسوم البيانية
                dbc.Row([
                    dbc.Col(dcc.Graph(id='histogram'), width=6),
                    dbc.Col(dcc.Graph(id='scatter'), width=6),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='boxplot'), width=6),
                    dbc.Col(dcc.Graph(id='heatmap'), width=6),
                ]),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='timeseries'), width=12),
                ]),
                html.Hr(),
                # صفحة الرؤى
                html.Div(id='insights')
            ], width=9)
        ])
    ], fluid=True)

    # رد الفعل لتحديث الرسوم بناءً على التصفية
    @app.callback(
        [
            Output('histogram', 'figure'),
            Output('scatter', 'figure'),
            Output('boxplot', 'figure'),
            Output('heatmap', 'figure'),
            Output('timeseries', 'figure'),
            Output('kpis', 'children'),
            Output('insights', 'children')
        ],
        [
            Input('field-filter', 'value'),
            Input('date-picker', 'start_date'),
            Input('date-picker', 'end_date')
        ]
    )
    def update_dashboard(field, start_date, end_date):
        """
        دالة رد الفعل لتحديث الرسوم البيانية والمقاييس بناءً على التصفية.

        Args:
            field (str): الحقل النفطي المختار.
            start_date (str): تاريخ بداية الفترة.
            end_date (str): تاريخ نهاية الفترة.

        Returns:
            tuple: الرسوم البيانية والمقاييس والرؤى.
        """
        # تصفية البيانات
        df_filtered = df.copy()
        if field != 'all':
            df_filtered = df_filtered[df_filtered['field_name'] == field]
        df_filtered = df_filtered[
            (df_filtered['date'] >= start_date) & 
            (df_filtered['date'] <= end_date)
        ]
        
        # إنشاء الرسوم البيانية
        fig_hist = create_histogram(df_filtered, "oil_production_bbl")
        fig_scatter = create_scatter(df_filtered, "wellhead_pressure_psi", "oil_production_bbl", color_col="field_name")
        fig_box = create_boxplot(df_filtered, "oil_production_bbl", group_by="field_name")
        fig_heatmap = create_heatmap(df_filtered, numeric_cols)
        fig_timeseries = create_timeseries(df_filtered, "date", "oil_production_bbl")
        
        # إنشاء المقاييس الرئيسية والرؤى
        kpis = create_kpis(df_filtered)
        insights = create_insights(df_filtered)
        
        return fig_hist, fig_scatter, fig_box, fig_heatmap, fig_timeseries, kpis, insights

    # تشغيل الخادم
    print(f"تشغيل لوحة التحكم التفاعلية على: http://127.0.0.1:8050")
    app.run(debug=False) # استخدام app.run بدلاً من app.run_server

if __name__ == "__main__":
    main()