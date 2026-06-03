import os
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier, StackingClassifier

def train_pipeline():
    cols = ['bedrooms', 'bathrooms', 'sqft_living', 'floors', 'view', 
            'grade', 'sqft_above', 'sqft_basement', 'lat', 'sqft_living15', 'price']
    feature_cols = ['bedrooms', 'bathrooms', 'sqft_living', 'floors', 
                    'grade', 'sqft_above', 'sqft_basement', 'lat', 'sqft_living15']

    if not os.path.exists("kc_house_data.csv"):
        print("❌ Dataset missing!")
        return

    print("📊 Loading authentic King County real-estate dataset...")
    df = pd.read_csv("kc_house_data.csv")
    df.columns = df.columns.str.strip()

    # Outlier Removal via your original IQR logic bounds
    df_sub = df[cols].copy()
    q1, q3 = df_sub.quantile(0.25), df_sub.quantile(0.75)
    iqr = q3 - q1
    condition = ~((df_sub < (q1 - 1.5 * iqr)) | (df_sub > (q3 + 1.5 * iqr))).any(axis=1)
    df_clean = df_sub[condition].dropna()

    # 1. Unsupervised Target Label Generation using KMeans (4 Valuation Tiers)
    print("🎯 Segmenting properties into valuation classes using KMeans...")
    km = KMeans(n_clusters=4, random_state=0)
    df_clean['Price Class'] = km.fit_predict(df_clean[cols])

    X = df_clean[feature_cols]
    Y_class = df_clean['Price Class']
    Y_reg = df_clean['price'] # Target for exact pricing regression calculation

    # Data segmentation splits
    X_train, _, y_train_c, _ = train_test_split(X, Y_class, test_size=0.3, random_state=131)
    _, _, y_train_r, _ = train_test_split(X, Y_reg, test_size=0.3, random_state=131)

    # Scaler transformation isolation to strictly prevent data leakage
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    # 2. Train Core Regression Model (Multiple Linear Regression)
    print("📈 Training valuation regression core framework engine...")
    reg_model = LinearRegression()
    reg_model.fit(X_train_scaled, y_train_r)

    # 3. Train Core Strategy Routing Classification Engines
    print("🧠 Training distributed modeling strategy core classification engines...")
    models = {
        'knn': KNeighborsClassifier(n_neighbors=11).fit(X_train_scaled, y_train_c),
        'svm': SVC(kernel='linear', probability=True).fit(X_train_scaled, y_train_c),
        'rf': RandomForestClassifier(n_estimators=10, max_depth=5).fit(X_train_scaled, y_train_c)
    }

    # High-Impact Ensemble Hybrid Stacking Classifier
    print("⛓️ Assembling Stacking Classifier hybrid ensemble...")
    models['hybrid'] = StackingClassifier(
        estimators=[('knn', models['knn']), ('svm', models['svm'])],
        final_estimator=LogisticRegression(max_iter=20000)
    ).fit(X_train_scaled, y_train_c)

    # Save all structural operational components
    joblib.dump(models, "best_models.joblib")
    joblib.dump(reg_model, "reg_model.joblib")
    joblib.dump(scaler, "scaler.joblib")
    print("🎯 Models and scalers successfully serialized to disk. Backend operational.")

if __name__ == "__main__":
    train_pipeline()
