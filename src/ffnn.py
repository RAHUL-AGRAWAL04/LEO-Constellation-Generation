import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.metrics import r2_score

# Load the dataset from CSV file
data = pd.read_csv("tle.csv")

# Remove rows with NaN values
data = data.dropna()
data = data[data['Altitude'] < 2000]
data = data[data['Altitude'] > 400]


# Selecting input parameters (features) and target variable
input_params = ['Inclination', 'Eccentricity', 'Altitude', 'Mean Motion']
target_variable = ['RAAN']

# Extracting input parameters and target variable
X = data[input_params].values
y = data[target_variable].values

# Splitting the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Build feedforward neural network model
model = Sequential([
    Dense(256, input_dim=X_train_scaled.shape[1], activation='relu'),
    Dense(128, input_dim=X_train_scaled.shape[0], activation='relu'),
    Dense(64,  activation='relu'),
    Dense(32, activation='relu'),
    Dense(16, activation='relu'),
    Dense(8, activation='relu'),
    Dense(4),
    Dense(2),
    Dense(1)
])

# Compile the model
model.compile(optimizer='adam', loss='mean_absolute_error')

# Train the model
history = model.fit(X_train_scaled, y_train, epochs=1000, batch_size=32, validation_split=0.1)

# Evaluate the model
train_loss = model.evaluate(X_train_scaled, y_train, verbose=0)
test_loss = model.evaluate(X_test_scaled, y_test, verbose=0)

print("Training Loss:", train_loss)
print("Testing Loss:", test_loss)

train_pred = model.predict(X_train_scaled)
test_pred = model.predict(X_test_scaled)
print(test_pred)
test_pred = [i%360 for i in test_pred]
test_pred = np.array(test_pred)
print(test_pred)

train_r2 = r2_score(y_train, train_pred)
test_r2 = r2_score(y_test, test_pred)

print("Training R² Score:", train_r2)
print("Testing R² Score:", test_r2)


model.save('raan2.h5')