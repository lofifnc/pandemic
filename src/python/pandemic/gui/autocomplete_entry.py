from tkinter import *
import re
from typing import List, Callable

from pandemic.gui.gui_simulation import Simulation
from pandemic.gui.trie import Trie
from pandemic.state import State


class AutocompleteEntry(Entry):
    def __init__(self, callback: Callable[[State], None], *args, **kwargs):

        Entry.__init__(self, *args, **kwargs)
        self._callback = callback
        self.simulation = Simulation()
        self.trie = Trie()
        self.trie.insert_set(self.simulation.get_possible_moves())
        self.var = self["textvariable"]
        if self.var == "":
            self.var = self["textvariable"] = StringVar()

        self.var.trace("w", self.changed)
        self.bind("<Right>", self.selection)
        self.bind("<Up>", self.up)
        self.bind("<Down>", self.down)
        self.bind("<Return>", self.submit)

        self.lb_up = False

    def changed(self, name, index, mode):

        if self.var.get() == "":
            self.lb.destroy()
            self.lb_up = False
        else:
            words = self.comparison()
            if words:
                if not self.lb_up:
                    self.lb = Listbox()
                    self.lb.bind("<Double-Button-1>", self.selection)
                    self.lb.bind("<Right>", self.selection)
                    self.lb.place(x=self.winfo_x(), y=self.winfo_y() + self.winfo_height())
                    self.lb_up = True

                self.lb.delete(0, END)
                for w in words:
                    self.lb.insert(END, w)
            else:
                if self.lb_up:
                    self.lb.destroy()
                    self.lb_up = False

    def selection(self, event):

        if self.lb_up:
            self.var.set(self.lb.get(ACTIVE))
            self.lb.destroy()
            self.lb_up = False
            self.icursor(END)

    def up(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = "0"
            else:
                index = self.lb.curselection()[0]
            if index != "0":
                self.lb.selection_clear(first=index)
                index = str(int(index) - 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def down(self, event):

        if self.lb_up:
            if self.lb.curselection() == ():
                index = "0"
            else:
                index = self.lb.curselection()[0]
            if index != END:
                self.lb.selection_clear(first=index)
                index = str(int(index) + 1)
                self.lb.selection_set(first=index)
                self.lb.activate(index)

    def submit(self, event):
        self.selection(event)
        command = self.var.get()
        self.simulation.perform_action(command)
        self.var.set("")
        self._callback(self.simulation.state)
        self.trie.clear()
        self.trie.insert_set(self.simulation.get_possible_moves())
        print("changed next round")

    def comparison(self) -> List[str]:
        pattern = re.compile(".*" + self.var.get() + ".*")
        return self.trie.all_words_beginning_with_prefix(self.var.get())
