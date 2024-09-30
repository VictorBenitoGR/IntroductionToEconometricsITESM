# -*- coding: utf-8 -*-
"""E2

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1jQiMREOF7EFJazDUVuuSooPEbhCe7it_

**Evidence 2 - Time Series Model Report**

### **Team:**

- **Alma Ivone Santiago Hernández - A00836636.**
- **Víctor Benito García Rocha - A01232580.**
- **Bruno Chavez Meza- A01737301.**

### **Context:**

The Ministry of Economy aims to estimate Mexican manufacturing exports based on the peso-dollar exchange rate.
- For this, it requires using a precise model that passes:
    - The tests of normality in the residuals.
    - Non stationarity.
    - Serial autocorrelation.

### **Please determine:**

- The existence of a cointegration relationship.
    - If it exists, apply a VECM model.
    - If it does not exist, apply a VAR model.

### **Libraries**
"""

!pip install statsmodels
!pip install --upgrade statsmodels
import locale
from statsmodels.tsa.stattools import adfuller
import pandas as pd
import seaborn as sns #plots
import numpy as np
import statistics as stats # statistics
import matplotlib.pyplot as plt #graphs
import matplotlib as mpl
import statsmodels.api as sm
import matplotlib.pyplot as plt
from scipy.stats import shapiro, boxcox
import scipy.stats as stats
from statsmodels.graphics.gofplots import qqplot
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import adfuller
from statsmodels.tools.eval_measures import rmse, aic
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.vector_ar.vecm import VECM
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf

#upload since our PC-desktop
from google.colab import files
files.upload()

"""### **Data exploratory analysis**

- **Import the data**
"""

df = pd.read_csv("/content/Evidence2.csv", encoding="latin-1", delimiter=";")
df.head(10)

"""- **Data types**"""

df.dtypes

#security copy
df0=df.copy()

"""- **Convert the date column to datetime**"""

df["date"] = pd.to_datetime(df["date"], format="%d/%m/%y %H:%M")
df.dtypes

"""- **Set the date as the index**"""

df.set_index("date", inplace=True)
df.head() # From 2000-01-01

df.tail() # To 2024-04-01

"""- **Examine data and clean data frame**"""

df.info()
#exchange= Monetary aggregate (peso-dollar exchange rate.)

"""- **See if there are missing values**"""

df.isnull().sum()

"""- **See if there are duplicated values**"""

duplicated_rows = df.duplicated()
print("Filas duplicadas:")
print(df[duplicated_rows])

num_duplicated = duplicated_rows.sum()
print(f"Número de filas duplicadas: {num_duplicated}")

"""- **Descriptive statistics**"""

df_descriptive_stats = df.describe()
df_descriptive_stats.round(1)

"""### **General data visualization**

Plot Time Series
"""

plt.figure(figsize=(16, 6))
plt.plot(df["exp_td"], label="Exports")
plt.title("Mexican Manufacturing Exports", fontsize=16)
plt.xlabel("Date", fontsize=14)
plt.ylabel("Exports", fontsize=14)
plt.legend()
plt.show()

plt.figure(figsize=(16, 6))
plt.plot(df["exchange"], label="Exchange Rate")
plt.title("Peso-Dollar Exchange Rate", fontsize=16)
plt.xlabel("Date", fontsize=14)
plt.ylabel("Exchange Rate", fontsize=14)
plt.legend()
plt.show()

"""**Outliers:**

In the exports data, there's a significant drop around 2020, likely due to the COVID-19 pandemic. This is an important event to note but not necessarily an outlier to remove.
The exchange rate shows a sharp spike around 2020 as well. Again, this is likely related to the pandemic and should be noted but not necessarily removed.

**Trends:**

Exports show a clear upward trend over time, with seasonal patterns.
The exchange rate also shows an overall upward trend, but with more abrupt changes and less clear seasonality.

For this, it requires using a precise model that passes the tests of normality in the residuals, non stationarity, and serial autocorrelation.

### **Normality test**

We started by cleaning up the 'inflation' and 'M1' data, replacing those zero values with NaNs since they were probably just missing data. Then we built a simple regression model to see the relationship between 'inflation' and 'M1'. The next step was to check if the residuals from that model looked normally distributed, which is a key assumption for a lot of the statistical analysis we might do down the line.

- **Check for normality visually and statistically**
"""

df['exp_td'] = df['exp_td'].replace(0, np.nan)
df['exchange'] = df['exchange'].replace(0, np.nan)

"""- **Regression model in levels**"""

x = 
X = sm.add_constant(df['exchange'])  # Adding a constant for the intercept
model_0 = sm.OLS(df['exp_td'], X).fit()  # OLS regression
residuals_0 = model_0.resid  # Extracting residuals

"""- **Shapiro-Wilk test on the residuals**

The p-value is less than 0.05, so we reject the null hypothesis that the residuals are normally distributed (so they are not, which is not ideal).
"""

shapiro_results_0 = stats.shapiro(residuals_0)
print(f"Shapiro-Wilk test statistic: {shapiro_results_0.statistic}, p-value: {shapiro_results_0.pvalue}")

"""- **Plot Q-Q plots**"""

fig, ax = plt.subplots(figsize=(12, 6)) # Create a figure and a single axes
sm.qqplot(residuals_0, line='45', fit=True, ax=ax) # Create the Q-Q plot on the single axes
ax.set_title('Q-Q Plot of Residuals for Model Exchange Rate - Exports') # Set the title for the plot
plt.show() # Display the plot

"""*In* this case, the p-value should be greater than 0.05 to be considered with normal residuals. Hence, the residuals do not follow a normal path.
0.00000000577493 < 0.05. It is not normally distributed.

**What to do: 1) Apply a logarithmic Transformation, 2) Apply Squared root, 3)BOX_COX transformation, 4) Difference the time series and remove seasonal effects in order to apply robust models such as VAR or VECM**

- **Apply a logarithmic Transformation.**

It is a common approach to stabilize normality, variance and potentially linearize relationships, making the data more suitable for linear modeling.
"""

df['log_exp_td'] = np.log(df['exp_td'])
df['log_exchange'] = np.log(df['exchange'])
df.head()

"""- **Regression model of log-transformed data**"""

X1 = sm.add_constant(df['log_exchange'])  # adding a constant for the intercept
model_log = sm.OLS(df['log_exp_td'], X1).fit()  # OLS regression
residuals_log = model_log.resid  # extracting residuals

"""- **Shapiro-Wilk test on the residuals**

We still reject the null hypothesis that the residuals are normally distributed.
"""

shapiro_results_log = stats.shapiro(residuals_log)
print(f"Shapiro-Wilk test statistic: {shapiro_results_log.statistic}, p-value: {shapiro_results_log.pvalue}")

"""- **Plot Q-Q plots**"""

fig, ax = plt.subplots(figsize=(12, 6))  # Create a figure and a single axes

sm.qqplot(residuals_log, line='45', fit=True, ax=ax)  # Create the Q-Q plot on the single axes
ax.set_title('Q-Q Plot of Residuals for Model_log exchange_exp_td')  # Set the title for the plot

plt.show()  # Display the plot

"""With Log transformation, The residuals of the model still don't follow



"Normality" P-value=0.00009191731078317389<0.05

While non-normal residuals are a significant concern in linear regression, they do not necessarily invalidate your model.

- **Apply Squared root transformation**
"""

df['sqrt_exchange'] = np.sqrt(df['exchange'])
df['sqrt_exp_td'] = np.sqrt(df['exp_td'])
df.head()

"""- **Regression model of squared root-transformed data**"""

# Adding a constant to the independent variable
df['const'] = 1

# Fit the time series model (e.g., Ordinary Least Squares regression)
model = sm.OLS(df['sqrt_exp_td'], df[['const', 'sqrt_exchange']])
results = model.fit()

# Print the summary of the regression
print(results.summary())

# Get the residuals
residuals_sqrt = results.resid

# Plot the residuals
plt.figure(figsize=(12, 6))
plt.plot(residuals_sqrt, label='Residuals', color='blue', linestyle='-', marker='o', markersize=4)
plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
plt.title('Residuals of the Model')
plt.xlabel('Time')
plt.ylabel('Residuals')
plt.grid(True)
plt.legend()
plt.show()

# Check for normality of residuals
# Plotting a Q-Q plot
sm.qqplot(residuals_sqrt, line='s')
plt.title('Q-Q Plot of Residuals')
plt.show()

"""- **Shapiro-Wilk test on the residuals**

We still reject the null hypothesis that the residuals are normally distributed.
"""

shapiro_results_sqrt = stats.shapiro(residuals_sqrt)
print(f"Shapiro-Wilk test statistic: {shapiro_results_sqrt.statistic}, p-value: {shapiro_results_sqrt.pvalue}")

"""- **Jarque-Bera test**

We reject the null hypothesis that the residuals are normally distributed.
"""

# Performing Jarque-Bera test for normality
jarque_bera_test = stats.jarque_bera(residuals_sqrt)
print('Jarque-Bera Test p-value:', jarque_bera_test[1])

# Summary of normality tests
if shapiro_results_sqrt.pvalue > 0.05 and jarque_bera_test[1] > 0.05:
    print("Residuals appear to be normally distributed.")
else:
    print("Residuals do not appear to be normally distributed.")

"""- **BOX_COX transformation**"""

df['exp_td_boxcox'], lambda_exp = boxcox(df['exp_td'])
df['exchange_boxcox'], lambda_ex = boxcox(df['exchange'])
df.head()

"""- **Regression model of Box-Cox transformed data**"""

X = sm.add_constant(df['exchange_boxcox'])  # Adding a constant for the intercept
model_boxcox = sm.OLS(df['exp_td_boxcox'], X).fit()  # OLS regression
residuals_boxcox = model_boxcox.resid  # Extracting residuals

"""- **Shapiro-Wilk test on the residuals**

We still reject the null hypothesis that the residuals are normally distributed, but the p-value is higher than before!
"""

shapiro_results_boxcox = stats.shapiro(residuals_boxcox)
print(f"Shapiro-Wilk test statistic: {shapiro_results_boxcox.statistic}, p-value: {shapiro_results_boxcox.pvalue}")

"""- **Jarque-Bera test**

We reject the null hypothesis that the residuals are normally distributed.
"""

jb_results_boxcox = stats.jarque_bera(residuals_boxcox)
print(f"Jarque-Bera test statistic: {jb_results_boxcox.statistic}, p-value: {jb_results_boxcox.pvalue}")

"""We could also solve stationarity using differences and a VAR model, so let's try that.

### **Stationarity and Autocorrelation**

Apply Augmented Dickey Fuller Test
In the ADF test:
Ho: Time Series is considered non-stationary
Ha: Time series is stationary when p-value of the test <0.05

- **Let's create a function to apply the ADF test**
"""

def adf_test(series, title=''):
    print(f'Augmented Dickey-Fuller Test: {title}')
    result = adfuller(series.dropna(), autolag='AIC')  # .dropna() handles differenced data
    labels = ['ADF test statistic', 'p-value', '# lags used', '# observations']
    out = pd.Series(result[0:4], index=labels)
    for key, val in result[4].items():
        out[f'critical value ({key})'] = val
    print(out.to_string())  # .to_string() removes the line "dtype: float64"

"""- **Perform the ADF test on each column.**

We fail to reject the null hypothesis that the time series is non-stationary, as the p-value is greater than 0.05 (so the time series is non-stationary, which is not ideal).
"""

adf_test(df['exp_td'], title='Exports')

adf_test(df['exchange'], title='Exchange Rate')

"""We can see that both variables (Exports and Exchange Rate), have a unit root and are "non stationary", since all p-values are  greater than 0.05 regrettably.

P_values:
- Exports: 0.99
- Exchange Rate: 0.63

### **Check for autocorrelation**

Plot Autocorrelation Function (ACF). You can do it over the variables in levels or, you can check it over the residuals of a model.

Peaks outside the confidence bands indicate significant autocorrelation. That is, the values ​​of the series are influenced by its previous values ​​in those lags.

- **Plotting the ACF for the exports**
"""

plt.figure(figsize=(12, 6))
plot_acf(df['exp_td'], lags=40, title='Exports ACF')
plt.show()

"""- **Plotting the ACF for the exchange rate**

Both series show strong autocorrelation that decays slowly, indicating non-stationarity in both series.
"""

plt.figure(figsize=(12, 6))
plot_acf(df['exchange'], lags=40, title='Exchange Rate ACF')
plt.show()

"""**To see autocorrelation in the residuals of a model, let's apply a GLS time series model with differences in the variables (transform variables).**

#### **Check for required differences to apply an GLS model in time series**

- **Function to find the number of differences necessary to make the series stationary (maximum 5)**
"""

def find_differencing(series, max_diff=5):
    diff = 0
    current_series = series.copy()

    while not adf_test(current_series) and diff < max_diff:
        if len(current_series) <= 1:
            print("The series is too short for further differencing.")
            return diff
        diff += 1
        current_series = current_series.diff().dropna()
        print(f"Differencing {diff} for the current column: ADF p-value = {adfuller(current_series)[1]}")

    return diff

df.head

#Let's make a copy to drop variables that we are not going to use, keep "logs"
df2=df.copy()
df2.drop(['log_exp_td', 'log_exchange', 'sqrt_exchange', 'sqrt_exp_td', 'const', 'exp_td_boxcox' , 'exchange_boxcox'], axis=1, inplace=True)

df2

"""- **Calculate the number of differences required for each column**

Since we need p-value < 0.05, both series only need 1 difference to be stationary.
"""

# Calculate the number of differences needed for each column (maximum 5)
# exp_td need 1 difference:  p-value = 3.859383374989132e-06 = 0.000003859383374989132 < 0.05
# exchange need 1 difference: 3.1163886997637402e-24 = 0.0000000000000000000000031163886997637402 < 0.05
resultados_diferenciacion = {}
for columna in df2.columns:
    print(f"\nAnalizando la columna {columna}...")
    num_diff = find_differencing(df2[columna], max_diff=5)
    resultados_diferenciacion[columna] = num_diff

"""exp_td need 1 difference:

exchange need 1 difference:

#### **Apply differentiation and prepare data for GLS modeling**

Differencing is a common technique used to remove trends and make the data stationary.

- **Columns that need differentiation and the number of differences required**
"""

columns_to_diff = {'exp_td': 1, 'exchange': 1}

"""- **Columns that do not need differentiation**"""

columns_no_diff = []

"""- **Apply differentiation to selected columns**"""

df_diff = df2.copy()
for col, n_diffs in columns_to_diff.items():
    for _ in range(n_diffs):
        df_diff[col] = df_diff[col].diff()
df_diff = df_diff.dropna()

"""- **Ensure all columns are aligned (here we just use an empty list as no columns are undifferentiated)**"""

if columns_no_diff:
    df_non_diff = df[columns_no_diff].iloc[max(columns_to_diff.values()):]
    # Combine differentiated and non-differentiated columns
    df_combined = pd.concat([df_diff[columns_to_diff.keys()], df_non_diff], axis=1).dropna()
else:
    df_combined = df_diff[columns_to_diff.keys()]

print("Combined Data (Differenced where needed):")
print(df_combined.head())

"""#### **Train-Test Split**
- **Split the differenced data into training and testing sets, using the last 12 observations for testing.**
"""

test_obs = 12

train = df_combined[:-test_obs]
test = df_combined[-test_obs:]

print("Train set:")
print(train.tail())

print("Test set:")
print(test.head())

"""#### **GLS Model**

- **Define the dependent and independent variables for the training set**
"""

X_train = train['exchange']
y_train = train['exp_td']

"""- **Adding a constant term for the intercept in the model**"""

X_train = sm.add_constant(X_train)

"""- **Fit the OLS model on the training set**"""

gls_model = sm.GLS(y_train, X_train).fit()

"""- **Print the model summary**

We can see that the exchange rate has a negative effect on exports, but the relationship is not statistically significant (p-value > 0.05).

- The R-squared value is very low, indicating that the model does not explain much of the variance in exports.
- The p-value for the F-statistic is greater than 0.05, indicating that the model as a whole is not statistically significant.
- The residuals are not normally distributed, as indicated by the Jarque-Bera test (p-value < 0.05).
- The Durbin-Watson statistic is close to 2, indicating that there may be autocorrelation in the residuals.
- The model is not ideal.
"""

print(gls_model.summary())

"""- **Plot the residuals to check for autocorrelation**"""

residuals_gls = gls_model.resid

plt.figure(figsize=(10, 5))
plt.plot(residuals_gls, label='Residuals', color='blue', linestyle='-', marker='o', markersize=4)
plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
plt.title('Residuals from the GLS Model')
plt.xlabel('Time')
plt.ylabel('Residuals')
plt.grid(True)
plt.legend()
plt.show()

"""- **Plot the ACF of the residuals**

We still can see autocorrelation in ACF, even with differenciated variables.
"""

plot_acf(residuals_gls, lags=20)
plt.title('ACF of the Residuals')
plt.show()

"""We still can see autocorrelation in ACF, even with differenciated variables.**

### **Stationarity**

- **Check stationarity of the variables**
"""

adf_exp_td = adfuller(df2['exp_td'])
adf_exchange = adfuller(df2['exchange'])

"""For Exports: p-value > 0.05, so the series is non-stationary."""

print('ADF test for Exports:', adf_exp_td)

"""For Exchange Rate: p-value > 0.05, so the series is non-stationary."""

print('ADF test for Exchange Rate:', adf_exchange)

"""For exp_td: p-value: 0.991540052 >0.05, we fail to reject the null hypothesis. This means that the exp_td series is non-stationary.

For exchange: P-value: 0.627903719 > 0.05,  exchange series is also non-stationary.

### **Test for cointegration**

We compare the trace statistic with the critical values (preferably 95%).  19.62>15.49(95%) ,  1.2252< 3.84(95%)

We accept Ha (alternative hypothesis) that there is at least one cointegration vector.

For example: det_order=0 (very common not deterministic trend no constant) and k_ar_diff=1 (one lagged difference)

- **Perform the Johansen cointegration test**
"""

coint_test = coint_johansen(df2[['exp_td', 'exchange']], det_order=0, k_ar_diff=1)

print(coint_test.lr1)  # Trace statistic

print(coint_test.cvt)  # Critical values

"""We compare the trace statistic with the critical values (preferably 95%)
- 19.62 < 19.93 (95%)
- 1.22  < 3.84 (95%)

We accept Ha (alternative hypothesis) that there is at least one cointegration vector and we can proceed with the VECM model.

### **Vector Error Correction Model**

**Triple solution:** Non normality in residuals, Non Stationary variables and Autocorrelation in time series.

- **Fit the VECM model**
"""

vecm = VECM(df2[['exp_td', 'exchange']], k_ar_diff=1, coint_rank=1)
vecm_result = vecm.fit()

"""- **Print summary of the VECM**

The VECM model shows that there is a cointegration relationship between the two variables.

The loading coefficients (alpha) for the equations show the relationship between the variables.

The cointegration relations for the loading-coefficients-column 1 show the cointegration vector.

The model is suitable for forecasting the variables.
"""

print(vecm_result.summary())

"""- **Plot the residuals to check for stationarity and white noise**"""

residuals_vecm = vecm_result.resid

plt.figure(figsize=(10, 5))
plt.plot(residuals_vecm[:, 0], label='Residuals for exp_td', color='blue', linestyle='-', marker='o', markersize=4)
plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
plt.title('Residuals of the VECM Model for exp_td')
plt.xlabel('Time')
plt.ylabel('Residuals')
plt.grid(True)
plt.legend()
plt.show()

"""- **Plot the residuals for the exchange rate**"""

plt.figure(figsize=(10, 5))
plt.plot(residuals_vecm[:, 1], label='Residuals for Exchange Rate', color='green', linestyle='-', marker='o', markersize=4)
plt.axhline(y=0, color='red', linestyle='--', linewidth=1)
plt.title('Residuals from the VECM Model for Exchange Rate')
plt.xlabel('Time')
plt.ylabel('Residuals')
plt.grid(True)
plt.legend()
plt.show()

"""### **Forecast**

- **Number of steps to forecast**
"""

steps = 12

"""- **Generate forecasts**"""

forecast = vecm_result.predict(steps=steps)

"""- **Convert forecast to DataFrame for better readability**"""

forecast_df = pd.DataFrame(forecast, columns=['exp_td_forecast', 'exchange_forecast'])

"""- **Add a datetime index to the forecast DataFrame**"""

last_date = pd.to_datetime('2024-04-30')  # End of historical data
forecast_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=steps, freq='M')
forecast_df.index = forecast_dates

print(forecast_df)

"""- **Combine historical data with forecast**"""

historical_data = df2[['exp_td', 'exchange']]
combined_df = pd.concat([historical_data, forecast_df], axis=0)

"""- **Plot the historical data and forecasts**"""

plt.figure(figsize=(12, 8))

# Plot historical and forecasted exports
plt.subplot(2, 1, 1)
plt.plot(combined_df.index[:len(historical_data)], combined_df['exp_td'][:len(historical_data)], label='Historical Exports', color='blue')
plt.plot(combined_df.index[len(historical_data):], combined_df['exp_td_forecast'][len(historical_data):], label='Forecasted Exports', color='red', linestyle='--')
plt.axvline(x=forecast_dates[0], color='gray', linestyle='--')
plt.title('Historical Exports and Forecast')
plt.xlabel('Date')
plt.ylabel('Exports')
plt.legend()

# Plot historical and forecasted exchange rate
plt.subplot(2, 1, 2)
plt.plot(combined_df.index[:len(historical_data)], combined_df['exchange'][:len(historical_data)], label='Historical Exchange Rate', color='green')
plt.plot(combined_df.index[len(historical_data):], combined_df['exchange_forecast'][len(historical_data):], label='Forecasted Exchange Rate', color='orange', linestyle='--')
plt.axvline(x=forecast_dates[0], color='gray', linestyle='--')
plt.title('Historical Exchange Rate and Forecast')
plt.xlabel('Date')
plt.ylabel('Exchange Rate')
plt.legend()

plt.tight_layout()
plt.show()