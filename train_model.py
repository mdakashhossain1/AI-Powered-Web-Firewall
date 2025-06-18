
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

# Load Dataset
data = pd.read_csv("dataset/nsl_kdd.csv", header=None)

# Basic preprocessing
data.columns = list(range(data.shape[1]))  # Add numeric column names
data[41] = data[41].apply(lambda x: 0 if x == 'normal' else 1)  # 0: normal, 1: attack

# Encode categorical features
for col in [1, 2, 3]:  # protocol_type, service, flag
    le = LabelEncoder()
    data[col] = le.fit_transform(data[col])

X = data.iloc[:, :-1]
y = data.iloc[:, -1]

# Train model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
print(classification_report(y_test, model.predict(X_test)))

# Save model
joblib.dump(model, "model/firewall_model.pkl")
print("Model saved!")
