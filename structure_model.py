"""Editable design state and starter-tower layout."""

from dataclasses import dataclass, field
from typing import Literal

from calculations import CANVAS_WIDTH, TABLE_TOP_Y, PIXELS_PER_FOOT, snap, point_in_canvas, segment_length

MemberKind = Literal["column", "beam", "brace"]


@dataclass
class Member:
    kind: MemberKind
    x1: float
    y1: float
    x2: float
    y2: float
    member_id: str

    @property
    def endpoints(self) -> tuple[float, float, float, float]:
        return self.x1, self.y1, self.x2, self.y2

    @property
    def length_ft(self) -> float:
        return segment_length(*self.endpoints)


@dataclass
class FloorMass:
    x: float
    y: float
    width: float
    height: float
    mass_id: str

    @property
    def bounds(self) -> tuple[float, float, float, float]:
        return self.x, self.y, self.x + self.width, self.y + self.height


@dataclass
class DesignState:
    members: list[Member] = field(default_factory=list)
    masses: list[FloorMass] = field(default_factory=list)
    moment_nodes: set[tuple[float, float]] = field(default_factory=set)
    next_member_id: int = 1
    next_mass_id: int = 1

    def clear(self) -> None:
        self.members.clear()
        self.masses.clear()
        self.moment_nodes.clear()
        self.next_member_id = 1
        self.next_mass_id = 1

    def load_starter_tower(self) -> None:
        self.clear()
        for x in (180.0, 420.0):
            self.add_member("column", x, 460, x, 340)
            self.add_member("column", x, 340, x, 220)
        self.add_member("beam", 180, 220, 420, 220)
        self.add_member("beam", 180, 340, 420, 340)
        self.add_member("beam", 180, 460, 420, 460)
        self.add_member("brace", 180, 220, 420, 340)
        self.add_member("brace", 180, 460, 420, 340)
        self.add_mass(200, 200, 220, 20)
        self.add_mass(200, 320, 220, 20)

    def add_member(self, kind: MemberKind, x1: float, y1: float, x2: float, y2: float) -> Member | None:
        x1, y1 = snap(x1), snap(y1)
        x2, y2 = snap(x2), snap(y2)
        if not point_in_canvas(x1, y1) or not point_in_canvas(x2, y2):
            return None
        if segment_length(x1, y1, x2, y2) < 1.0:
            return None
        if kind == "beam" and y1 != y2:
            x2, y2 = x2, y1
        if kind == "column" and x1 != x2:
            x2, y2 = x1, y2
        member = Member(kind, x1, y1, x2, y2, f"m{self.next_member_id}")
        self.next_member_id += 1
        self.members.append(member)
        return member

    def add_mass(self, x: float, y: float, width: float, height: float) -> FloorMass | None:
        x, y = snap(x), snap(y)
        width = snap(width)
        height = snap(height)
        if width < PIXELS_PER_FOOT or height < PIXELS_PER_FOOT:
            return None
        if not point_in_canvas(x, y) or not point_in_canvas(x + width, y + height):
            return None
        mass = FloorMass(x, y, width, height, f"q{self.next_mass_id}")
        self.next_mass_id += 1
        self.masses.append(mass)
        return mass

    def remove_member(self, member_id: str) -> None:
        self.members[:] = [m for m in self.members if m.member_id != member_id]
        self._prune_moment_nodes()

    def remove_mass(self, mass_id: str) -> None:
        self.masses[:] = [m for m in self.masses if m.mass_id != mass_id]

    def connected_nodes(self) -> list[tuple[float, float]]:
        nodes: set[tuple[float, float]] = set()
        for member in self.members:
            nodes.add((member.x1, member.y1))
            nodes.add((member.x2, member.y2))
        # Brace anchors that lie in the interior of a beam or column are nodes too.
        for brace in (m for m in self.members if m.kind == "brace"):
            for x, y in ((brace.x1, brace.y1), (brace.x2, brace.y2)):
                anchors = [n for n in nodes if n != (x, y)]
                nodes.add((x, y))
        return sorted(nodes)

    def toggle_joint(self, x: float, y: float) -> None:
        node = (snap(x), snap(y))
        if node in self.moment_nodes:
            self.moment_nodes.remove(node)
        else:
            self.moment_nodes.add(node)

    def _prune_moment_nodes(self) -> None:
        live = set(self.connected_nodes())
        self.moment_nodes.intersection_update(live)
