"""Editable design state and starter-tower layout."""

from dataclasses import dataclass, field
from typing import Literal

from calculations import CANVAS_WIDTH, TABLE_TOP_Y, PIXELS_PER_FOOT, snap, point_in_canvas, segment_length
import math
import hashlib
import json

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

    def structural_anchor_points(self) -> list[tuple[float, float]]:
        points: set[tuple[float, float]] = set()
        for member in self.members:
            if member.kind not in ("column", "beam"):
                continue
            points.add((snap(member.x1), snap(member.y1)))
            points.add((snap(member.x2), snap(member.y2)))
            dx = member.x2 - member.x1
            dy = member.y2 - member.y1
            length = math.hypot(dx, dy)
            if length > 0:
                steps = int(length // PIXELS_PER_FOOT)
                for step in range(1, steps):
                    t = step * PIXELS_PER_FOOT / length
                    points.add((snap(member.x1 + dx * t), snap(member.y1 + dy * t)))
        unique = list(points)
        return unique

    def snap_structural_node(self, x: float, y: float) -> tuple[float, float]:
        sx = max(0.0, min(float(CANVAS_WIDTH), float(snap(x))))
        sy = max(0.0, min(float(TABLE_TOP_Y), float(snap(y))))
        nearest = (sx, sy)
        nearest_distance = 26.0
        for px, py in self.structural_anchor_points():
            distance = math.hypot(px - sx, py - sy)
            if distance < nearest_distance:
                nearest = (px, py)
                nearest_distance = distance
        return nearest

    def resize_member_endpoint(
        self,
        member_id: str,
        endpoint: str,
        x: float,
        y: float,
    ) -> bool:
        member = next((item for item in self.members if item.member_id == member_id), None)
        if member is None:
            return False
        if member.kind == "beam":
            nx = snap(x)
            ny = member.y1 if endpoint == "start" else member.y2
        elif member.kind == "column":
            nx = member.x1 if endpoint == "start" else member.x2
            ny = snap(y)
        else:
            nx, ny = self.snap_structural_node(x, y)
        nx = max(0.0, min(float(CANVAS_WIDTH), nx))
        ny = max(0.0, min(float(TABLE_TOP_Y), ny))
        old_x1, old_y1 = member.x1, member.y1
        old_x2, old_y2 = member.x2, member.y2
        if endpoint == "start":
            member.x1, member.y1 = nx, ny
        else:
            member.x2, member.y2 = nx, ny
        if segment_length(*member.endpoints) < 1.0:
            member.x1, member.y1 = old_x1, old_y1
            member.x2, member.y2 = old_x2, old_y2
            return False
        self._prune_moment_nodes()
        return True

    def move_member(self, member_id: str, new_start_x: float, new_start_y: float) -> bool:
        member = next((item for item in self.members if item.member_id == member_id), None)
        if member is None:
            return False
        dx = member.x2 - member.x1
        dy = member.y2 - member.y1
        nx1 = snap(new_start_x)
        ny1 = snap(new_start_y)
        if member.kind == "beam":
            ny1 = snap(member.y1)
        elif member.kind == "column":
            dx = 0
        nx2 = nx1 + dx
        ny2 = ny1 + dy
        if min(nx1, nx2) < 0 or max(nx1, nx2) > CANVAS_WIDTH:
            return False
        if min(ny1, ny2) < 0 or max(ny1, ny2) > TABLE_TOP_Y:
            return False
        member.x1, member.y1 = nx1, ny1
        member.x2, member.y2 = nx2, ny2
        self._prune_moment_nodes()
        return True

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

    def resize_mass(self, mass_id: str, handle: str, x: float, y: float) -> bool:
        mass = next((item for item in self.masses if item.mass_id == mass_id), None)
        if mass is None:
            return False
        nx = max(0.0, min(float(CANVAS_WIDTH), float(snap(x))))
        ny = max(0.0, min(float(TABLE_TOP_Y), float(snap(y))))
        left, top, right, bottom = mass.x, mass.y, mass.x + mass.width, mass.y + mass.height
        if handle == "start":
            left, top = nx, ny
        else:
            right, bottom = nx, ny
        if right < left:
            left, right = right, left
        if bottom < top:
            top, bottom = bottom, top
        width = snap(right - left)
        height = snap(bottom - top)
        if width < PIXELS_PER_FOOT or height < PIXELS_PER_FOOT:
            return False
        if right > CANVAS_WIDTH or bottom > TABLE_TOP_Y:
            return False
        mass.x, mass.y = left, top
        mass.width, mass.height = width, height
        return True

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
        # Brace anchors and intersections along continuous host members are nodes too.
        for brace in (m for m in self.members if m.kind == "brace"):
            for x, y in ((brace.x1, brace.y1), (brace.x2, brace.y2)):
                nodes.add((x, y))
                for host in (m for m in self.members if m.kind in ("beam", "column")):
                    ax, ay, bx, by = host.endpoints
                    dx = bx - ax
                    dy = by - ay
                    length_squared = dx * dx + dy * dy
                    if length_squared <= 0:
                        continue
                    t = ((x - ax) * dx + (y - ay) * dy) / length_squared
                    if 0 <= t <= 1:
                        px = ax + t * dx
                        py = ay + t * dy
                        if math.hypot(px - x, py - y) <= 1:
                            nodes.add((snap(px), snap(py)))
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

    def to_dict(self) -> dict:
        return {
            "format": "earthquake-shake-down-design",
            "version": 1,
            "members": [
                {
                    "id": member.member_id,
                    "kind": member.kind,
                    "x1": member.x1,
                    "y1": member.y1,
                    "x2": member.x2,
                    "y2": member.y2,
                }
                for member in self.members
            ],
            "masses": [
                {
                    "id": mass.mass_id,
                    "x": mass.x,
                    "y": mass.y,
                    "width": mass.width,
                    "height": mass.height,
                }
                for mass in self.masses
            ],
            "moment_nodes": [
                {"x": x, "y": y}
                for x, y in sorted(self.moment_nodes)
            ],
        }

    def fingerprint(self) -> str:
        payload = self.to_dict()
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    @classmethod
    def from_dict(cls, data: dict) -> "DesignState":
        if not isinstance(data, dict):
            raise ValueError("Design file must contain a JSON object.")
        if data.get("format") != "earthquake-shake-down-design":
            raise ValueError("Unsupported design file format.")
        if data.get("version") != 1:
            raise ValueError("Unsupported design file version.")
        members_data = data.get("members")
        masses_data = data.get("masses")
        moment_data = data.get("moment_nodes", [])
        if not isinstance(members_data, list) or not isinstance(masses_data, list):
            raise ValueError("Design file is missing member or floor-mass lists.")

        state = cls()
        member_ids: set[str] = set()
        mass_ids: set[str] = set()
        for item in members_data:
            if not isinstance(item, dict):
                raise ValueError("Invalid member entry.")
            kind = item.get("kind")
            if kind not in ("column", "beam", "brace"):
                raise ValueError("Invalid structural member type.")
            try:
                x1 = float(item["x1"])
                y1 = float(item["y1"])
                x2 = float(item["x2"])
                y2 = float(item["y2"])
            except (KeyError, TypeError, ValueError):
                raise ValueError("Invalid structural member coordinates.")
            if not all(math.isfinite(value) for value in (x1, y1, x2, y2)):
                raise ValueError("Structural member coordinates must be finite.")
            member = state.add_member(kind, x1, y1, x2, y2)
            if member is None:
                raise ValueError("A structural member is outside bounds or below 1 foot.")
            if isinstance(item.get("id"), str):
                imported_id = item["id"].strip()
                if not imported_id or imported_id in member_ids:
                    raise ValueError("Member IDs must be unique and nonempty.")
                member.member_id = imported_id
            member_ids.add(member.member_id)

        for item in masses_data:
            if not isinstance(item, dict):
                raise ValueError("Invalid floor-mass entry.")
            try:
                x = float(item["x"])
                y = float(item["y"])
                width = float(item["width"])
                height = float(item["height"])
            except (KeyError, TypeError, ValueError):
                raise ValueError("Invalid floor-mass dimensions.")
            if not all(math.isfinite(value) for value in (x, y, width, height)):
                raise ValueError("Floor-mass dimensions must be finite.")
            mass = state.add_mass(x, y, width, height)
            if mass is None:
                raise ValueError("A floor mass is outside bounds or below 1 foot.")
            if isinstance(item.get("id"), str):
                imported_id = item["id"].strip()
                if not imported_id or imported_id in mass_ids:
                    raise ValueError("Mass IDs must be unique and nonempty.")
                mass.mass_id = imported_id
            mass_ids.add(mass.mass_id)

        if not isinstance(moment_data, list):
            raise ValueError("Invalid moment-node list.")
        live_nodes = set(state.connected_nodes())
        for item in moment_data:
            if not isinstance(item, dict):
                raise ValueError("Invalid moment-node entry.")
            try:
                node = (snap(float(item["x"])), snap(float(item["y"])))
            except (KeyError, TypeError, ValueError):
                raise ValueError("Invalid moment-node coordinates.")
            if node not in live_nodes:
                raise ValueError("A moment node does not match a connected structural node.")
            state.moment_nodes.add(node)
        return state
