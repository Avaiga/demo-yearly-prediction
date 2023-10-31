import pandas as pd
import statsmodels.api as sm
from sklearn.linear_model import LinearRegression


def clean_data(historical_data: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms sales data into total sales per month

    Args:
        historical_data: historical sales dataframe (date, store, item, sales)

    Returns:
        monthly sales dataframe (date, sales)
    """
    historical_data["date"] = pd.to_datetime(historical_data["date"])
    historical_data["date"] = (
        historical_data["date"].dt.year.astype("str")
        + "-"
        + historical_data["date"].dt.month.astype("str")
        + "-01"
    )
    historical_data["date"] = pd.to_datetime(historical_data["date"])
    historical_data = historical_data.groupby("date").sales.sum().reset_index()
    return historical_data


def filter_data(cleaned_data: pd.DataFrame, prediction_year: str) -> pd.DataFrame:
    """
    Filters data to include only data from the two years before the prediction year

    Args:
        cleaned_data: monthly sales dataframe (date, sales)
        prediction_year: year to predict

    Returns:
        filtered dataframe (date, sales)
    """
    start_date = str(int(prediction_year) - 2) + "-01-01"
    end_date = str(int(prediction_year) - 1) + "-12-01"
    filtered_data = cleaned_data[
        (cleaned_data["date"] >= start_date) & (cleaned_data["date"] <= end_date)
    ]
    return filtered_data


def predict(
    last_two_years: pd.DataFrame,
    model: str,
    historical_data: pd.DataFrame,
    prediction_year: str,
) -> pd.DataFrame:
    """
    Predicts sales for the prediction year according to the model

    Args:
        last_two_years: filtered dataframe (date, sales)
        model: model to use for prediction (linear, arima)

    Returns:
        predicted sales for the prediction year (date, sales)
    """
    predicted_data = pd.DataFrame()

    if model == "linear":
        X = last_two_years.index.values.reshape(-1, 1)
        y = last_two_years["sales"].values.reshape(-1, 1)
        model = LinearRegression()
        model.fit(X, y)
        predicted_data["date"] = pd.date_range(
            start=f"{prediction_year}-01-01", end=f"{prediction_year}-12-01", freq="MS"
        )
        predicted_data["sales"] = model.predict(
            pd.DataFrame(
                {"date": predicted_data["date"].astype("str")}
            ).index.values.reshape(-1, 1)
        )
    elif model == "arima":
        train_data = last_two_years.copy()
        train_data.set_index("date", inplace=True)
        model = sm.tsa.statespace.SARIMAX(
            last_two_years["sales"], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12)
        )
        results = model.fit()
        predicted_data = results.predict(12)
        predicted_data = predicted_data[1:]
        predicted_data = pd.DataFrame(
            {
                "date": pd.date_range(
                    start=f"{prediction_year}-02-01",
                    end=f"{prediction_year}-12-01",
                    freq="MS",
                ),
                "sales": predicted_data.values,
            }
        )
    else:
        raise ValueError("Model not supported")

    # Combine last_two_years and predicted_data with columns: date, actual, predicted
    combined_data = pd.DataFrame()
    combined_data["date"] = pd.date_range(
        start=f"{int(prediction_year)-2}-01-01",
        end=f"{prediction_year}-12-01",
        freq="MS",
    )
    combined_data = combined_data.merge(
        last_two_years, how="left", on="date", suffixes=("", "_actual")
    )
    combined_data = combined_data.merge(
        predicted_data, how="left", on="date", suffixes=("", "_predicted")
    )
    return combined_data
