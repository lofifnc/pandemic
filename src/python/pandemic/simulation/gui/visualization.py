# libraries
from tkinter import *
from typing import Dict, List

import cartopy.crs as ccrs
import cartopy
import matplotlib
from matplotlib import patheffects
from matplotlib.axes import Axes
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib import transforms
from collections import defaultdict

from pandemic.simulation.gui.autocomplete_entry import AutocompleteEntry
from pandemic.simulation.model.enums import Character
from pandemic.simulation.model.citystate import CityState
from pandemic.simulation.state import CONNECTIONS, State
from pandemic.simulation.state import City

RESEARCH_LAT = -50

RESEARCH_LON = 0

FONT = {
    "family": "serif",
    "color": "white",
    "weight": "bold",
    "size": 6,
    # "backgroundcolor": "black"
}

FONT_VIRUS = {"size": 6, "backgroundcolor": "white", "weight": "bold"}
FONT_RESEARCH = {"size": 10, "backgroundcolor": "white", "weight": "bold"}

matplotlib.use("TkAgg")


class Visualization:
    _canvas: FigureCanvasTkAgg
    _toolbar: NavigationToolbar2Tk
    _txt: Dict[City, Text]
    _player: Dict[Character, Line2D]
    _ax: Axes
    _player_cards_label: Label
    _state_label: Label

    def __init__(self):
        self._window = Tk()
        self._txt = {}
        self._player = {}
        self._text_var = StringVar()
        self._virus_marker: Dict[City, List[Line2D]] = defaultdict(list)
        # == start plotting ==
        self.plot()
        self._window.mainloop()

    def plot(self):
        fig = matplotlib.figure.Figure(frameon=False, figsize=(100, 100))
        self._ax = fig.add_axes([0, 0, 1, 1], projection=ccrs.PlateCarree())
        self._ax.background_patch.set_visible(False)
        self._ax.outline_patch.set_visible(False)
        self._ax.axis("off")

        self._ax.add_feature(cartopy.feature.OCEAN)
        self._ax.add_feature(cartopy.feature.LAND)
        self._canvas = FigureCanvasTkAgg(fig, master=self._window)
        self._canvas.draw()
        self._toolbar = NavigationToolbar2Tk(self._canvas, self._window)
        e1 = AutocompleteEntry(self.update_plot, self._window)
        e1.pack(side=TOP, fill=X, expand=0)

        state = e1.gui_simulation.simulation.state

        frame = Frame(self._window)
        frame.pack(side=TOP)
        self._player_cards_label = Label(frame, text=state.players[state.active_player].cards_to_string())
        self._player_cards_label.pack(side=LEFT)
        self._state_label = Label(frame, text=state.report())
        self._state_label.pack(side=LEFT)
        self._canvas.get_tk_widget().pack(side=TOP, fill=BOTH, expand=1)
        self._toolbar.update()

        research_text = self._ax.text(
            RESEARCH_LON,
            RESEARCH_LAT,
            "Research Stations",
            fontdict=FONT_RESEARCH,
            transform=ccrs.Geodetic(),
            horizontalalignment="center",
        )
        # Visualization.add_path_effect(research_text)

        # Add connections
        for conn in CONNECTIONS:
            start = state.cities[conn[0]]
            end = state.cities[conn[1]]

            self._ax.plot(
                [start.lon, end.lon], [start.lat, end.lat], color="gray", linestyle="--", transform=ccrs.Geodetic()
            )

        for city_id, location in state.cities.items():
            city: Line2D = self._ax.plot(
                location.lon, location.lat, "o", color=location.color, transform=ccrs.Geodetic()
            )[0]

            # Visualization.add_path_effect(city)
            t = transforms.offset_copy(city.get_transform(), x=location.text_offset, y=2, units="dots")

            self._txt[city_id] = self._ax.text(
                location.lon,
                location.lat,
                location.name,
                fontdict=FONT,
                transform=t,
                horizontalalignment=location.text_alignment,
            )
            # Visualization.add_path_effect(self._txt[city_id])

            self.draw_virus_state(city_id, location, city)
            self.mark_research_station(location)

        for character, player in state.players.items():
            location = state.cities[player.city]
            self._player[character] = self._ax.plot(
                location.lon, location.lat, "d", markersize=9, color=character.color, transform=ccrs.Geodetic()
            )[0]

    @staticmethod
    def add_path_effect(line):
        color = "black" if line.color != "black" else "white"
        line.set_path_effects([patheffects.withStroke(linewidth=2, foreground=color)])

    def draw_virus_state(self, city: City, city_state: CityState, city_plot: Line2D):
        lon = city_state.lon
        lat = city_state.lat

        for idx, virus in enumerate(city_state.get_viral_state().keys()):
            for i in range(0, 3):
                t = transforms.offset_copy(city_plot.get_transform(), x=-8 + i * 8, y=-10 + idx * -8, units="dots")
                vm = self._ax.plot(lon, lat, "x", transform=t, visible=False)[0]
                # Visualization.add_path_effect(vm)
                self._virus_marker[city].append(vm)

        self.update_virus_state(city, city_state)

    def update_virus_state(self, city_id: City, location: CityState):

        city_marker = self._virus_marker[city_id]
        [m.set_visible(False) for m in city_marker]
        i = 0
        for virus, count in location.get_viral_state().items():
            for _ in range(0, count):
                city_marker[i].set_visible(True)
                city_marker[i].set_color(virus)
                i += 1

    @staticmethod
    def text_for_location(city_state: CityState) -> str:
        return f"{city_state.name} {city_state.format_infection_state()}"

    def update_plot(self, state: State):
        self._player_cards_label["text"] = state.players[state.active_player].cards_to_string()
        self._state_label["text"] = state.report()

        for city_id, city_state in state.cities.items():
            self.update_virus_state(city_id, city_state)

        for color, player in state.players.items():
            city_state = state.cities[player.city]
            self._player[color].set_xdata(city_state.lon)
            self._player[color].set_ydata(city_state.lat)
            self.mark_research_station(city_state)

        self._canvas.draw()

    def mark_research_station(self, location: CityState):
        if location.has_research_station():
            self._ax.plot(
                [location.lon, RESEARCH_LON],
                [location.lat, RESEARCH_LAT],
                color="white",
                linestyle="-",
                # transform=ccrs.Geodetic(),
            )