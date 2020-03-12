# libraries
from tkinter import *
from typing import Dict, List

import cartopy.crs as ccrs
import matplotlib
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib import transforms
from collections import defaultdict

from pandemic.gui.autocomplete_entry import AutocompleteEntry
from pandemic.model.enums import PlayerColor, Virus
from pandemic.model.location import Location
from pandemic.state import CONNECTIONS, State
from pandemic.state import LOCATIONS

FONT = {
    "family": "serif",
    "color": "white",
    "weight": "bold",
    "size": 6,
    # "backgroundcolor": "black"
}

FONT_VIRUS = {"size": 6, "backgroundcolor": "white", "weight": "bold"}

matplotlib.use("TkAgg")


class Visualization:
    _canvas: FigureCanvasTkAgg
    _toolbar: NavigationToolbar2Tk
    _txt: Dict[str, Text]
    _player: Dict[PlayerColor, Line2D]
    _ax: Axes
    _player_cards_label: Label
    _state_label: Label

    def __init__(self):
        self._window = Tk()
        self._txt = {}
        self._player = {}
        self._text_var = StringVar()
        self._virus_marker: Dict[str, List[Line2D]] = defaultdict(list)
        # == start plotting ==
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
        self._player_cards_label = Label(
            frame, text="[%s]" % " ".join(state.get_player_cards())
        )
        self._player_cards_label.pack(side=LEFT)
        self._state_label = Label(frame, text=state.report())
        self._state_label.pack(side=LEFT)
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
            city: Line2D = ax.plot(
                location.get_lon(),
                location.get_lat(),
                "o",
                color=location.get_display_color(),
                transform=ccrs.Geodetic(),
            )[0]

            Visualization.add_path_effect(city)
            t = transforms.offset_copy(
                city.get_transform(), x=location.get_text_offset(), y=2, units="dots"
            )

            self._txt[city_id] = ax.text(
                location.get_lon(),
                location.get_lat(),
                location.get_name(),
                fontdict=FONT,
                transform=t,
                horizontalalignment=location.text_alignment,
            )
            Visualization.add_path_effect(self._txt[city_id])

            self.draw_virus_state(city_id, location, city, ax)

        for color, player in state.get_players().items():
            location = state.get_location(player.get_city())
            self._player[color] = ax.plot(
                location.get_lon(),
                location.get_lat(),
                "v",
                color=color.name.lower(),
                transform=ccrs.Geodetic(),
            )[0]

    @staticmethod
    def add_path_effect(line):
        color = "black" if line.get_color() != "black" else "white"
        line.set_path_effects([patheffects.withStroke(linewidth=2, foreground=color)])

    def draw_virus_state(
        self, city_id: str, location: Location, city: Line2D, ax: Axes
    ):
        lon = location.get_lon()
        lat = location.get_lat()

        for idx, virus in enumerate(location.get_viral_state().keys()):
            for i in range(0, 3):
                t = transforms.offset_copy(
                    city.get_transform(), x=-8 + i * 8, y=-10 + idx * -8, units="dots"
                )
                vm = ax.plot(lon, lat, "x", transform=t, visible=False)[0]
                Visualization.add_path_effect(vm)
                self._virus_marker[city_id].append(vm)

        self.update_virus_state(city_id, location)

    def update_virus_state(self, city_id: str, location: Location):

        city_marker = self._virus_marker[city_id]
        [m.set_visible(False) for m in city_marker]
        i = 0
        for virus, count in location.get_viral_state().items():
            for _ in range(0, count):
                city_marker[i].set_visible(True)
                city_marker[i].set_color(virus.name.lower())
                i += 1

    @staticmethod
    def text_for_location(location: Location) -> str:
        return f"{location.get_name()} {location.format_infection_state()}"

    def update_plot(self, state: State):
        self._player_cards_label["text"] = "[%s]" % " ".join(state.get_player_cards())
        self._state_label["text"] = state.report()

        for city_id, location in state.get_locations().items():
            self.update_virus_state(city_id, location)

        for color, player in state.get_players().items():
            location = state.get_location(player.get_city())
            self._player[color].set_xdata(location.get_lon())
            self._player[color].set_ydata(location.get_lat())

        self._canvas.draw()
