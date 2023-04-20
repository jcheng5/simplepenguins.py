from pathlib import Path
from shiny import Inputs, Outputs, Session, App, reactive, render, req, ui
import shinyswatch
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import bslib
from bslib import layout_sidebar, sidebar

sns.set_theme()

df = pd.read_csv(Path(__file__).parent / "penguins.csv", na_values="NA")
numeric_cols = df.select_dtypes(include=["float64"]).columns.tolist()
species = df["Species"].unique().tolist()

app_ui = bslib.page_fillable(
    layout_sidebar(
        sidebar(
            ui.input_selectize(
                "xvar",
                "X variable",
                numeric_cols,
                selected="Bill Length (mm)",
            ),
            ui.input_selectize(
                "yvar",
                "Y variable",
                numeric_cols,
                selected="Bill Depth (mm)",
            ),
            ui.input_checkbox_group(
                "species", "Filter by species", species, selected=species
            ),
            ui.hr(),
            ui.input_switch("by_species", "Show species", value=True),
            ui.input_switch("show_margins", "Show marginal plots", value=True),
        ),
        ui.output_plot("scatter", height="100%"),
        fill=True,
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
