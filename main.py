from config.config import configure
from pages import scenario_page
from pages.root import root, selected_scenario, selected_data_node, content

import taipy as tp
from taipy import Core, Gui, Config


def on_init(state):
    ...


def on_change(state, var, val):
    if var == "selected_scenario" and val:
        state.selected_scenario = val  # BUG
        state.selected_data_node = None
    if var == "selected_data_node" and val:
        state.selected_data_node = val  # BUG
        state["scenario"].manage_data_node_partial(state)


pages = {
    "/": root,
    "scenario": scenario_page,
}


if __name__ == "__main__":
    # Instantiate, configure and run the Core
    scenario_cfg = configure()
    tp.Core().run()
    scenario = tp.create_scenario(scenario_cfg)
    tp.submit(scenario)
    print(scenario.prediction.read())

    # Instantiate, configure and run the GUI
    gui = Gui(pages=pages)
    data_node_partial = gui.add_partial("")
    gui.run(title="Yearly Sales Prediction")
