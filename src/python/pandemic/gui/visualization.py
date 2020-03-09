# libraries
from tkinter import *
from typing import Dict

import cartopy.crs as ccrs
import matplotlib
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.text import Text

from pandemic.gui.autocomplete_entry import AutocompleteEntry
from pandemic.model.enums import PlayerColor, Virus
from pandemic.model.location import Location
from pandemic.state import CONNECTIONS
from pandemic.state import LOCATIONS

FONT = {
    "family": "serif",
    "color": "white",
    "weight": "bold",
    "size": 6,
    # "backgroundcolor": "black"
}

FONT_VIRUS = {
    "size": 6,
    "backgroundcolor": "white"
}


matplotlib.use("TkAgg")


class Visualization:

    _canvas: FigureCanvasTkAgg
    _toolbar: NavigationToolbar2Tk
    _txt: Dict[str, Text]
    _player: Dict[PlayerColor, Line2D]
    _ax: Axes

    def __init__(self):
        self._window = Tk()
        self._txt = {}
        self._player = {}
        self._text_var = StringVar()
        # start plotting
        self.plot()
        self._window.mainloop()

    def plot(self):
        fig = matplotlib.figure.Figure(frameon=False)
        ax = fig.add_subplot(projection=ccrs.PlateCarree())
        ax.axis("off")
        ax.stock_img()
        self._canvas = FigureCanvasTkAgg(fig, master=self._window)
        self._canvas.draw()
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._window)
        e1 = AutocompleteEntry(self.update_plot, self._window)
        e1.pack(side=TOP, fill=X, expand=0)

        state = e1.simulation.state

        frame = Frame(self._window)
        frame.pack(side=TOP)
        player_cards_label = Label(frame, text="[%s]" % " ".join(state.get_player_cards()))
        player_cards_label.pack(side=LEFT)
        state_label = Label(frame, text=state.report())
        state_label.pack(side=LEFT)
        self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self._toolbar.update()



        # Add a connections
        for conn in CONNECTIONS:
            start = LOCATIONS[conn[0]]
            end = LOCATIONS[conn[1]]

            ax.plot(
                [start.get_lon(), end.get_lon()],
                [start.get_lat(), end.get_lat()],
                color="gray",
                linestyle="--",
                transform=ccrs.Geodetic(),
            )

        for city_id, location in LOCATIONS.items():
            ax.plot(
                location.get_lon(),
                location.get_lat(),
                "o",
                color=location.get_display_color(),
                transform=ccrs.Geodetic(),
            )

            self.draw_virus_state(location, ax)

            self._txt[city_id] = ax.text(
                location.get_lon() + 0.5,
                location.get_lat() + 0.5,
                Visualization.text_for_location(location),
                fontdict=FONT,
                transform=ccrs.Geodetic(),
            )
            self._txt[city_id].set_path_effects(
                [patheffects.withStroke(linewidth=2, foreground="black")]
            )

        for color, player in state.get_players().items():
            location = state.get_location(player.get_city())
            self._player[color] = ax.plot(
                location.get_lon(),
                location.get_lat(),
                "v",
                color=color.name.lower(),
                transform=ccrs.Geodetic(),
            )[0]

    def draw_virus_state(self, location: Location, ax: Axes):
        lon = location.get_lon()
        lat = location.get_lat() - 8

        for idx, (virus, count) in enumerate(location.get_viral_state().items()):
            if count > 0:
                m = ax.text(lon, lat, count, color=virus.name.lower(), transform=ccrs.Geodetic(), horizontalalignment="center", fontdict=FONT_VIRUS, bbox={"pad": 1.5, "color": "white"})
                m.set_path_effects(
                    [patheffects.withStroke(linewidth=1, foreground="black")])

    @staticmethod
    def text_for_location(location: Location) -> str:
        return f"{location.get_name()} {location.format_infection_state()}"

    def update_plot(self, state):
        for city_id, location in state.get_locations().items():
            text = Visualization.text_for_location(location)
            self._txt[city_id].set_text(text)

        for color, player in state.get_players().items():
            location = state.get_location(player.get_city())
            print(self._player[color])
            self._player[color].set_xdata(location.get_lon())
            self._player[color].set_ydata(location.get_lat())

        self._canvas.draw()
