from taipy import Config
from taipy.config import Frequency, Scope
from algos import clean_data, filter_data, predict


def configure():
    historical_data_cfg = Config.configure_data_node(
        "historical_data",
        storage_type="csv",
        default_path="historical_data.csv",
        scope=Scope.GLOBAL,
    )
    model_cfg = Config.configure_data_node(
        "model", default_data="linear", scope=Scope.SCENARIO
    )
    prediction_year_cfg = Config.configure_data_node(
        "prediction_year", default_data="2016", scope=Scope.CYCLE
    )
    last_two_years_cfg = Config.configure_data_node("last_two_years", scope=Scope.CYCLE)
    prediction_cfg = Config.configure_data_node("prediction", scope=Scope.SCENARIO)
    cleaned_data_cfg = Config.configure_data_node("cleaned_data", scope=Scope.GLOBAL)

    clean_data_cfg = Config.configure_task(
        id="clean_data",
        function=clean_data,
        input=[historical_data_cfg],
        output=[cleaned_data_cfg],
    )
    filter_data_cfg = Config.configure_task(
        id="filter_data",
        function=filter_data,
        input=[cleaned_data_cfg, prediction_year_cfg],
        output=[last_two_years_cfg],
    )
    predict_cfg = Config.configure_task(
        id="predict",
        function=predict,
        input=[last_two_years_cfg, model_cfg, historical_data_cfg, prediction_year_cfg],
        output=[prediction_cfg],
    )

    scenario_cfg = Config.configure_scenario(
        id="prediction_scenario",
        task_configs=[clean_data_cfg, filter_data_cfg, predict_cfg],
        frequency=Frequency.YEARLY,
    )

    return scenario_cfg
