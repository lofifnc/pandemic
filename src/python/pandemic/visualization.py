# libraries
from queue import Empty
from typing import Dict, Callable

import cartopy.crs as ccrs
import matplotlib
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.backend_bases import key_press_handler, KeyEvent
from matplotlib.figure import Figure

from pandemic.model.location import Location
from pandemic.state import LOCATIONS, State

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from tkinter import *
from pandemic.state import CONNECTIONS
from matplotlib.text import Text

FONT = {
    "family": "serif",
    "color": "white",
    "weight": "bold",
    "size": 6,
    # "backgroundcolor": "black"
}


matplotlib.use("TkAgg")


class Visualization:

    _canvas: FigureCanvasTkAgg
    _toolbar: NavigationToolbar2Tk
    _txt: Dict[str, Text]
    _ax: Axes

    def __init__(self, simulation: Callable[[State], State], start_state: State):
        self._window = Tk()
        self._txt = {}
        self._simulation = simulation
        self._state = start_state
        self.plot()
        self._canvas.mpl_connect("key_press_event", self.on_key_event)

        self._window.mainloop()

    def on_key_event(self, event: KeyEvent):
        print(event)
        print("you pressed %s" % event.key)
        if event.key == "n":
            self._state = self._simulation(self._state)
            self.update_plot()
        key_press_handler(event, self._canvas, self._toolbar)

    def plot(self):
        fig = matplotlib.figure.Figure()
        ax = fig.add_subplot(projection=ccrs.PlateCarree())
        ax.stock_img()

        self._canvas = FigureCanvasTkAgg(fig, master=self._window)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self._canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=1)
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._window)
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

        for color, player in self._state.get_players().items():
            location = self._state.get_location(player.get_city())
            ax.plot(
                location.get_lon(),
                location.get_lat(),
                "o",
                color=color.name.lower(),
                transform=ccrs.Geodetic(),
            )

    @staticmethod
    def text_for_location(location: Location) -> str:
        return f"{location.get_name()} {location.format_infection_state()}"

    def update_plot(self):
        for city_id, location in self._state.get_locations().items():
            text = Visualization.text_for_location(location)
            self._txt[city_id].set_text(text)

        self._canvas.draw()
