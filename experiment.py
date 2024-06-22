import mesa
import random

# Green
Green = "#2ca02c"
# Red
Red = "#d62728"
# Yellow
Yellow = "#FCFF33"
# Blue
Blue = "#337FFF"


def generate_data(model):
    return random.uniform(1, 1000)


class ChartingModel(mesa.Model):
    """
    About box information goes here...
    """

    def __init__(self, num_agents=10, num_steps=100):
        super().__init__()
        self.num_steps = num_steps

        # scheduler for the agents
        # self.schedule = mesa.time.RandomActivation(self)

        # data collection
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "A": generate_data,
                "B": generate_data,
                "X": generate_data,
                "Y": generate_data,
            }
        )

        self.running = True
        self.datacollector.collect(self)

    def step(self):
        # tell all the agents in the model to run their step function
        # self.schedule.step()
        # collect data
        self.datacollector.collect(self)

    def run_model(self):
        for i in range(self.num_steps):
            self.step()


## GRAPHICS ##

lines = mesa.visualization.ChartModule(
    [
        {"Label": "X", "Color": Red},
        {"Label": "Y", "Color": Green},
        {"Label": "A", "Color": Yellow},
        {"Label": "B", "Color": Blue},
    ],
    canvas_height=300,
)


# bar chart that shows the balance of USD and USDC
chart_element = mesa.visualization.BarChartModule(
    [
        {"Label": "A", "Color": Red},
        {"Label": "B", "Color": Green},
    ],
    canvas_height=300,
)

## UI ##

model_params = {
    "num_agents": mesa.visualization.Slider(
        "Consumers", 25, 1, 200, description="Number of Agents"
    ),
}

## SETUP ##

# create instance of Mesa ModularServer
server = mesa.visualization.ModularServer(
    ChartingModel,
    [lines, chart_element],
    "Example1",
    model_params=model_params,
)


if __name__ == "__main__":
    server.launch(open_browser=True)
