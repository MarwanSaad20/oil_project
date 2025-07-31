import os
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import plotly.express as px
import plotly.graph_objects as go
from oil_project.scripts.utils import load_data, save_figure, save_report

# تحديد seed للتكرارية
np.random.seed(42)

# تحديد مسار المشروع الرئيسي بشكل ديناميكي
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
figures_dir = os.path.join(base_dir, "outputs", "figures")  # تغيير إلى figures
reports_dir = os.path.join(base_dir, "outputs", "reports")  # للتقارير

def preprocess_for_modeling(df):
    """
    دالة لتحضير البيانات للنمذجة (إزالة الأعمدة غير الضرورية وترميز المتغيرات الفئوية).
    """
    features = ['gas_production_mcf', 'water_production_bbl', 'wellhead_pressure_psi', 
                'tubing_pressure_psi', 'choke_size_in', 'pump_efficiency__', 'field_name']
    target = 'oil_production_bbl'
    
    features = [col for col in features if col in df.columns]
    if target not in df.columns:
        raise ValueError(f"العمود المستهدف {target} غير موجود في البيانات!")
    
    df_model = df[features + [target]].copy()
    
    # إضافة ميزة جديدة: نسبة إنتاج النفط إلى الماء
    if 'water_production_bbl' in df_model.columns:
        df_model['oil_to_water_ratio'] = df_model['oil_production_bbl'] / (df_model['water_production_bbl'] + 1e-6)
    
    if 'field_name' in features:
        df_model = pd.get_dummies(df_model, columns=['field_name'], drop_first=True)
    
    print("تم تحضير البيانات للنمذجة بنجاح.")
    return df_model, target

def train_model(X, y):
    """
    دالة لتدريب نموذج Random Forest.
    """
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    metrics = {"MSE": mse, "R2": r2}
    print(f"\n--- أداء النموذج ---")
    print(f"Mean Squared Error: {mse:.2f}")
    print(f"R² Score: {r2:.2f}")
    
    return model, X_test, y_test, y_pred, metrics

def create_predictions_plot(y_test, y_pred):
    """
    دالة لإنشاء رسم مبعثر لمقارنة القيم الفعلية والمتوقعة.
    """
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y_test, y=y_pred, mode='markers',
                             name='التنبؤ مقابل الفعلي'))
    fig.add_trace(go.Scatter(x=[y_test.min(), y_test.max()], 
                             y=[y_test.min(), y_test.max()],
                             mode='lines', name='الخط المثالي',
                             line=dict(color='red', dash='dash')))
    fig.update_layout(title="القيم المتوقعة مقابل الفعلية",
                      xaxis_title="القيم الفعلية (oil_production_bbl)",
                      yaxis_title="القيم المتوقعة")
    return fig

def create_feature_importance_plot(model, feature_names):
    """
    دالة لإنشاء رسم لأهمية المتغيرات.
    """
    importances = model.feature_importances_
    fig = px.bar(x=feature_names, y=importances,
                 title="أهمية المتغيرات في نموذج Random Forest",
                 labels={'x': 'المتغير', 'y': 'الأهمية'})
    return fig

def main(input_path=None):
    """
    الدالة الرئيسية للنمذجة وإنشاء التقارير.
    """
    if input_path is None:
        input_path = os.path.join(base_dir, "data", "processed", "cleaned_oil_field_production_data_20250731.csv")
    
    print(f"\n--- تحميل البيانات من: {input_path} ---")
    df = load_data(input_path)
    
    df_model, target = preprocess_for_modeling(df)
    
    X = df_model.drop(columns=[target])
    y = df_model[target]
    
    model, X_test, y_test, y_pred, metrics = train_model(X, y)
    
    fig_predictions = create_predictions_plot(y_test, y_pred)
    save_figure(fig_predictions, "predictions_vs_actual", output_dir=figures_dir)
    
    fig_importance = create_feature_importance_plot(model, X.columns)
    save_figure(fig_importance, "feature_importance", output_dir=figures_dir)
    
    report_title = "تقرير نمذجة إنتاج النفط"
    figures = [fig_predictions, fig_importance]
    save_report(figures, report_title, "modeling_report", output_dir=reports_dir)

if __name__ == "__main__":
    main()