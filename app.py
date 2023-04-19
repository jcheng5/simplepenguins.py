from pathlib import Path
from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
import shinyswatch
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sns.set_theme()

df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
species = df["Species"].unique().tolist()

app_ui = ui.page_bootstrap(
    {"class": "p-3"},
    shinyswatch.theme.minty(),
    ui.tags.style("html, body { height: 100%; }"),
    ui.div(
        {"class": "card h-100 p-3 d-flex flex-row"},
        ui.div(
            {"class": "p-3", "style": "flex: 1 1 0"},
            ui.input_selectize(
                "xvar", "X variable", df.columns.tolist(), selected="Bill Length (mm)"
            ),
            ui.input_selectize(
                "yvar", "Y variable", df.columns.tolist(), selected="Bill Depth (mm)"
            ),
            ui.input_checkbox_group(
                "species", "Filter by species", species, selected=species
            ),
            ui.hr(),
            ui.input_switch("by_species", "Show species", value=True),
            ui.input_switch("show_margins", "Show marginal plots", value=True),
        ),
        ui.div(
            {"class": "p-3", "style": "flex: 3 3 0"},
            ui.output_plot("scatter", height="100%"),
        ),
    ),
)


def server(input: Inputs, output: Outputs, session: Session):
    @reactive.Calc
    def filtered_df() -> pd.DataFrame:
        """Returns a Polars data frame that includes only the desired rows"""

        # This calculation "req"uires that at least one species is selected
        req(len(input.species()) > 0)
        # Filter the rows so we only include the desired species
        return df[df["Species"].isin(input.species())]

    @output
    @render.plot
    def scatter():
        """Generates a plot for Shiny to display to the user"""

        # The plotting function to use depends on whether margins are desired
        plotfunc = sns.jointplot if input.show_margins() else sns.scatterplot

        plotfunc(
            data=filtered_df(),
            x=input.xvar(),
            y=input.yvar(),
            hue="Species" if input.by_species() else None,
            hue_order=species,
        )
        plt.legend(loc="lower right")

app = App(app_ui, server)
