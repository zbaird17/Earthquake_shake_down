"""Tkinter desktop entry point for the earthquake shake-down simulator."""

from copy import deepcopy
import json
import os
from pathlib import Path
import tkinter as tk
from tkinter import messagebox, ttk

import matplotlib
import pymunk

matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from matplotlib.patches import Rectangle
from matplotlib.lines import Line2D

from calculations import (
    CANVAS_HEIGHT,
    CANVAS_WIDTH,
    TABLE_TOP_Y,
    PIXELS_PER_FOOT,
    GRAVITY_MODES,
    peak_acceleration_g,
)
from structure_model import DesignState, Member, FloorMass
from simulation import TestSimulation


class EarthquakeApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Earthquake Shake-Down")
        self.root.geometry("980x700")

        self.design = DesignState()
        self.design.load_starter_tower()
        self.test: TestSimulation | None = None
        self.testing = False
        self.active_tool: str | None = None
        self.pending_point: tuple[float, float] | None = None
        self.pointer = (CANVAS_WIDTH / 2, TABLE_TOP_Y / 2)
        self.selected_member_id: str | None = None
        self.selected_member_endpoint: str | None = None
        self.drag_offset: tuple[float, float] | None = None
        self.saved_design: DesignState | None = None
        self.amplitude = 4.0
        self.frequency = 3.0
        self.gravity_name = "Earth"
        self.result_text = "Ready"
        self.elapsed = 0.0
        self.peak_g = peak_acceleration_g(self.amplitude, self.frequency)
        self.scores = {"Earth": 0.0, "Mars": 0.0, "Moon": 0.0}

        self._build_ui()
        self._load_scores()
        self._bind_events()
        self._draw()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.after(16, self._animation_tick)

    def _build_ui(self) -> None:
        main = ttk.Frame(self.root, padding=8)
        main.pack(fill="both", expand=True)

        left = ttk.Frame(main)
        left.pack(side="left", fill="y", padx=(0, 8))
        ttk.Label(left, text="Tools", font=("TkDefaultFont", 10, "bold")).pack(pady=(0, 6))
        for label, tool in (
            ("Column", "column"),
            ("Beam", "beam"),
            ("Brace", "brace"),
            ("Floor Mass", "mass"),
        ):
            ttk.Button(left, text=label, width=12, command=lambda t=tool: self._select_tool(t)).pack(pady=2)

        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(side="left", fill="both")
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.figure.patch.set_facecolor("#eef4f8")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_xlim(0, CANVAS_WIDTH)
        self.ax.set_ylim(CANVAS_HEIGHT, 0)
        self.ax.set_aspect("equal")
        self.ax.set_xticks([])
        self.ax.set_yticks([])
        self.canvas = FigureCanvasTkAgg(self.figure, master=canvas_frame)
        self.canvas.get_tk_widget().configure(width=CANVAS_WIDTH, height=CANVAS_HEIGHT)
        self.canvas.get_tk_widget().pack()

        sidebar = ttk.Frame(main, width=220)
        sidebar.pack(side="right", fill="y")
        ttk.Label(sidebar, text="Seismic Controls", font=("TkDefaultFont", 10, "bold")).pack(pady=(0, 6))

        self.amplitude_var = tk.DoubleVar(value=self.amplitude)
        self.frequency_var = tk.DoubleVar(value=self.frequency)
        self._slider_section(sidebar, "Amplitude (in)", self.amplitude_var, 0, 12, 0.1, self._set_amplitude)
        self._slider_section(sidebar, "Frequency (Hz)", self.frequency_var, 0.1, 10, 0.1, self._set_frequency)

        ttk.Label(sidebar, text="Gravity", font=("TkDefaultFont", 9, "bold")).pack(pady=(12, 4))
        gravity_frame = ttk.Frame(sidebar)
        gravity_frame.pack(fill="x")
        self.gravity_buttons = {}
        for name in ("Earth", "Mars", "Moon"):
            button = tk.Button(
                gravity_frame,
                text=name,
                width=8,
                relief="raised",
                borderwidth=2,
                command=lambda n=name: self._set_gravity(n),
            )
            button.pack(side="left", padx=1)
            self.gravity_buttons[name] = button
        self._update_gravity_button_states()

        ttk.Separator(sidebar).pack(fill="x", pady=10)
        self.start_button = ttk.Button(sidebar, text="Start Test", command=self._toggle_test)
        self.start_button.pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Clear Structure", command=self._clear_structure).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Load Starter Tower", command=self._load_starter).pack(fill="x", pady=2)

        ttk.Separator(sidebar).pack(fill="x", pady=10)
        self.cost_label = ttk.Label(sidebar, text="Total Cost: $0")
        self.elapsed_label = ttk.Label(sidebar, text="Elapsed: 0.00 s")
        self.peak_label = ttk.Label(sidebar, text="Peak: 0.00 g")
        self.result_label = ttk.Label(sidebar, text="Result: Ready")
        self.cost_label.pack(anchor="w")
        self.elapsed_label.pack(anchor="w")
        self.peak_label.pack(anchor="w")
        self.result_label.pack(anchor="w")
        ttk.Label(sidebar, text="High Scores", font=("TkDefaultFont", 9, "bold")).pack(anchor="w", pady=(8, 2))
        self.score_labels = {}
        for name in ("Earth", "Mars", "Moon"):
            label = ttk.Label(sidebar, text=f"{name}: 0.00 g")
            label.pack(anchor="w")
            self.score_labels[name] = label

    def _slider_section(self, parent, title, variable, minimum, maximum, resolution, callback) -> None:
        frame = ttk.LabelFrame(parent, text=title)
        frame.pack(fill="x", pady=4)
        scale = ttk.Scale(frame, from_=minimum, to=maximum, variable=variable, command=lambda _=None: callback(None))
        scale.pack(fill="x", padx=6)
        spin = ttk.Spinbox(frame, from_=minimum, to=maximum, increment=resolution, textvariable=variable,
                           command=lambda: callback(None), width=10)
        spin.pack(pady=4)
        if title.startswith("Amplitude"):
            scale.configure(command=lambda value: self._set_amplitude(float(value)))
            spin.configure(command=lambda: self._set_amplitude(None))
        else:
            scale.configure(command=lambda value: self._set_frequency(float(value)))
            spin.configure(command=lambda: self._set_frequency(None))

    def _bind_events(self) -> None:
        widget = self.canvas.get_tk_widget()
        widget.bind("<Motion>", self._on_motion)
        widget.bind("<Button-1>", self._on_click)
        widget.bind("<B1-Motion>", self._on_drag)
        widget.bind("<ButtonRelease-1>", self._on_release)
        self.root.bind("<Escape>", lambda _event: self._cancel_tool())
        self.root.bind("<Delete>", lambda _event: self._delete_selected())
        self.root.bind("<BackSpace>", lambda _event: self._delete_selected())

    def _select_tool(self, tool: str) -> None:
        if self.testing:
            return
        self.active_tool = tool
        self.pending_point = None
        self.selected_member_id = None
        self._draw()

    def _cancel_tool(self) -> None:
        self.active_tool = None
        self.pending_point = None
        self.selected_member_endpoint = None
        self._draw()

    def _canvas_position(self, event) -> tuple[float, float]:
        width = self.canvas.get_tk_widget().winfo_width()
        height = self.canvas.get_tk_widget().winfo_height()
        x = event.x * CANVAS_WIDTH / max(width, 1)
        y = event.y * CANVAS_HEIGHT / max(height, 1)
        return round(x / PIXELS_PER_FOOT) * PIXELS_PER_FOOT, round(y / PIXELS_PER_FOOT) * PIXELS_PER_FOOT

    def _on_motion(self, event) -> None:
        self.pointer = self._canvas_position(event)
        self._draw()

    def _on_click(self, event) -> None:
        if self.testing:
            return
        x, y = self._canvas_position(event)
        if y > TABLE_TOP_Y:
            return

        if self.active_tool:
            if self.active_tool == "mass":
                self.design.add_mass(x, y, 220, 20)
                self._cancel_tool()
                self._refresh_readouts()
            else:
                if self.pending_point is None:
                    self.pending_point = (x, y)
                else:
                    x1, y1 = self.pending_point
                    if self.active_tool == "beam":
                        member = self.design.add_member("beam", x1, y1, x, y)
                    elif self.active_tool == "column":
                        member = self.design.add_member("column", x1, y1, x, y)
                    else:
                        member = self.design.add_member("brace", x1, y1, x, y)
                    self.pending_point = None
                    self.active_tool = None
                    self._refresh_readouts()
            self._draw()
            return

        for nx, ny in self.design.connected_nodes():
            if ((nx + 6 - x) ** 2 + (ny - 8 - y) ** 2) ** 0.5 <= 12:
                self.design.toggle_joint(nx, ny)
                self.selected_member_endpoint = None
                self._refresh_readouts()
                self._draw()
                return

        for member in self.design.members:
            for endpoint_name, px, py in (
                ("start", member.x1, member.y1),
                ("end", member.x2, member.y2),
            ):
                if ((px - x) ** 2 + (py - y) ** 2) ** 0.5 <= 10:
                    self.selected_member_id = member.member_id
                    self.selected_member_endpoint = endpoint_name
                    self.drag_offset = None
                    self._draw()
                    return
            if self._point_near_segment(x, y, member):
                self.selected_member_id = member.member_id
                self.selected_member_endpoint = None
                self.drag_offset = (x - member.x1, y - member.y1)
                self._draw()
                return
        for mass in self.design.masses:
            if mass.x <= x <= mass.x + mass.width and mass.y <= y <= mass.y + mass.height:
                self.selected_member_id = f"mass:{mass.mass_id}"
                self.selected_member_endpoint = None
                self.drag_offset = (x - mass.x, y - mass.y)
                self._draw()
                return
        self.selected_member_id = None
        self._draw()

    def _on_drag(self, event) -> None:
        if self.testing or not self.selected_member_id:
            return
        x, y = self._canvas_position(event)
        if self.selected_member_id.startswith("mass:"):
            mass_id = self.selected_member_id.split(":", 1)[1]
            mass = next((m for m in self.design.masses if m.mass_id == mass_id), None)
            if mass:
                dx = x - (mass.x + self.drag_offset[0])
                dy = y - (mass.y + self.drag_offset[1])
                nx = round((mass.x + dx) / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                ny = round((mass.y + dy) / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                if 0 <= nx and nx + mass.width <= CANVAS_WIDTH and 0 <= ny and ny + mass.height <= TABLE_TOP_Y:
                    mass.x, mass.y = nx, ny
        else:
            member = next((m for m in self.design.members if m.member_id == self.selected_member_id), None)
            if member:
                if self.selected_member_endpoint:
                    old_x1, old_y1 = member.x1, member.y1
                    old_x2, old_y2 = member.x2, member.y2
                    nx, ny = x, y
                    if member.kind == "beam":
                        if self.selected_member_endpoint == "start":
                            ny = member.y1
                        else:
                            ny = member.y2
                    elif member.kind == "column":
                        nx = member.x1 if self.selected_member_endpoint == "start" else member.x2
                    nx = round(nx / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                    ny = round(ny / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                    if not 0 <= nx <= CANVAS_WIDTH or not 0 <= ny <= TABLE_TOP_Y:
                        self._draw()
                        return
                    if self.selected_member_endpoint == "start":
                        member.x1, member.y1 = nx, ny
                    else:
                        member.x2, member.y2 = nx, ny
                    if ((member.x2 - member.x1) ** 2 + (member.y2 - member.y1) ** 2) ** 0.5 < PIXELS_PER_FOOT:
                        member.x1, member.y1 = old_x1, old_y1
                        member.x2, member.y2 = old_x2, old_y2
                        self._draw()
                        return
                    self._draw()
                    return
                if not self.drag_offset:
                    return
                dx = x - (member.x1 + self.drag_offset[0])
                dy = y - (member.y1 + self.drag_offset[1])
                nx1 = round((member.x1 + dx) / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                ny1 = round((member.y1 + dy) / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                nx2 = nx1 + (member.x2 - member.x1)
                ny2 = ny1 + (member.y2 - member.y1)
                if 0 <= nx1 <= CANVAS_WIDTH and 0 <= nx2 <= CANVAS_WIDTH and 0 <= ny1 <= TABLE_TOP_Y and 0 <= ny2 <= TABLE_TOP_Y:
                    member.x1, member.y1, member.x2, member.y2 = nx1, ny1, nx2, ny2
        self._draw()

    def _on_release(self, _event) -> None:
        self.drag_offset = None
        self._refresh_readouts()

    def _point_near_segment(self, x, y, member) -> bool:
        ax, ay, bx, by = member.endpoints
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            return False
        t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / (dx * dx + dy * dy)))
        px, py = ax + t * dx, ay + t * dy
        return ((px - x) ** 2 + (py - y) ** 2) ** 0.5 <= 8

    def _delete_selected(self) -> None:
        if self.testing or not self.selected_member_id:
            return
        if self.selected_member_id.startswith("mass:"):
            self.design.remove_mass(self.selected_member_id.split(":", 1)[1])
        else:
            self.design.remove_member(self.selected_member_id)
        self.selected_member_id = None
        self.selected_member_endpoint = None
        self._refresh_readouts()
        self._draw()

    def _set_amplitude(self, value) -> None:
        if value is None:
            value = self.amplitude_var.get()
        value = max(0.0, min(12.0, float(value)))
        self.amplitude = value
        self.amplitude_var.set(value)
        if not self.testing:
            self.peak_g = peak_acceleration_g(value, self.frequency)
        self._refresh_readouts()

    def _set_frequency(self, value) -> None:
        if value is None:
            value = self.frequency_var.get()
        value = max(0.1, min(10.0, float(value)))
        self.frequency = value
        self.frequency_var.set(value)
        if not self.testing:
            self.peak_g = peak_acceleration_g(self.amplitude, value)
        self._refresh_readouts()

    def _set_gravity(self, name: str) -> None:
        if self.testing:
            return
        self.gravity_name = name
        self._update_gravity_button_states()
        self._draw()

    def _update_gravity_button_states(self) -> None:
        selected_colors = {
            "Earth": "#2563a8",
            "Mars": "#a33a32",
            "Moon": "#666666",
        }
        for name, button in self.gravity_buttons.items():
            is_selected = name == self.gravity_name
            if is_selected:
                background = selected_colors[name]
                foreground = "#ffffff"
                relief = "sunken"
            else:
                background = "#e7e7e7"
                foreground = "#333333"
                relief = "raised"
            button.configure(
                bg=background,
                fg=foreground,
                activebackground=selected_colors[name],
                activeforeground="#ffffff",
                disabledforeground="#ffffff",
                relief=relief,
                borderwidth=3 if is_selected else 2,
                state="disabled" if self.testing else "normal",
            )

    def _clear_structure(self) -> None:
        if self.testing:
            return
        self.design.clear()
        self.scores = {name: 0.0 for name in ("Earth", "Mars", "Moon")}
        self.elapsed = 0.0
        self.peak_g = peak_acceleration_g(self.amplitude, self.frequency)
        self.result_text = "Ready"
        self._save_scores()
        self._refresh_readouts()
        self._draw()

    def _load_starter(self) -> None:
        if self.testing:
            return
        self.design.load_starter_tower()
        self.scores = {name: 0.0 for name in ("Earth", "Mars", "Moon")}
        self.elapsed = 0.0
        self.peak_g = peak_acceleration_g(self.amplitude, self.frequency)
        self.result_text = "Ready"
        self._save_scores()
        self._refresh_readouts()
        self._draw()

    def _toggle_test(self) -> None:
        if self.testing:
            self._stop_test()
        else:
            self._start_test()

    def _start_test(self) -> None:
        self.saved_design = deepcopy(self.design)
        self.test = TestSimulation(deepcopy(self.design), self.gravity_name, self.amplitude, self.frequency)
        self.testing = True
        self.active_tool = None
        self.pending_point = None
        self.elapsed = 0.0
        self.peak_g = peak_acceleration_g(self.amplitude, self.frequency)
        self.result_text = "Testing"
        self.start_button.configure(text="Stop Test")
        self._update_gravity_button_states()
        for member in self.design.members:
            pass
        self._refresh_readouts()
        self._draw()

    def _stop_test(self) -> None:
        if self.saved_design is not None:
            self.design = self.saved_design
        self.saved_design = None
        self.test = None
        self.testing = False
        self.start_button.configure(text="Start Test")
        self._update_gravity_button_states()
        self.result_text = "Stopped"
        self._refresh_readouts()
        self._draw()

    def _animation_tick(self) -> None:
        if self.testing and self.test:
            self.test.step(1.0 / 60.0)
            if self.test.result is None:
                self.elapsed = self.test.elapsed
            else:
                self.elapsed = self.test.result_time or self.elapsed
                if self.result_text != ("Pass" if self.test.result == "success" else "Failure"):
                    self.result_text = "Pass" if self.test.result == "success" else "Failure"
                    if self.test.result == "success":
                        score = peak_acceleration_g(self.amplitude, self.frequency)
                        if score > self.scores[self.gravity_name]:
                            self.scores[self.gravity_name] = score
                            self._save_scores()
            self._refresh_readouts()
            self._draw()
        self.root.after(16, self._animation_tick)

    def _score_path(self) -> Path:
        base = Path(os.environ.get("APPDATA", str(Path.home() / "AppData" / "Roaming")))
        folder = base / "EarthquakeShakeDown"
        folder.mkdir(parents=True, exist_ok=True)
        return folder / "high_scores.json"

    def _load_scores(self) -> None:
        path = self._score_path()
        if not path.exists():
            return
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for name in ("Earth", "Mars", "Moon"):
                self.scores[name] = float(data.get(name, 0.0))
        except (json.JSONDecodeError, OSError):
            self.scores = {name: 0.0 for name in ("Earth", "Mars", "Moon")}
        self._refresh_readouts()

    def _save_scores(self) -> None:
        try:
            self._score_path().write_text(json.dumps(self.scores), encoding="utf-8")
        except OSError:
            pass

    def _refresh_readouts(self) -> None:
        from calculations import total_member_cost
        cost = total_member_cost(self.design.members)
        cost += 600 * len(self.design.moment_nodes)
        self.cost_label.configure(text=f"Total Cost: ${cost:,.0f}")
        self.elapsed_label.configure(text=f"Elapsed: {self.elapsed:.2f} s")
        self.peak_label.configure(text=f"Peak: {self.peak_g:.2f} g")
        self.result_label.configure(text=f"Result: {self.result_text}")
        for name, label in self.score_labels.items():
            label.configure(text=f"{name}: {self.scores[name]:.2f} g")

    def _draw(self) -> None:
        self.ax.clear()
        background = {"Earth": "#dcecff", "Mars": "#f3d5d5", "Moon": "#dddddd"}[self.gravity_name]
        self.ax.set_facecolor(background)
        self.ax.set_xlim(0, CANVAS_WIDTH)
        self.ax.set_ylim(CANVAS_HEIGHT, 0)
        self.ax.set_xticks([x for x in range(0, CANVAS_WIDTH + 1, 20)])
        self.ax.set_yticks([y for y in range(0, TABLE_TOP_Y + 1, 20)])
        self.ax.grid(True, color="#b8c5cf", linewidth=0.6)
        self.ax.set_xticklabels([])
        self.ax.set_yticklabels([])

        table_x = CANVAS_WIDTH / 2 - 180
        table_y = TABLE_TOP_Y
        if self.test:
            table_x = CANVAS_WIDTH / 2 - 180 + (self.test.table_body.position.x - CANVAS_WIDTH / 2)
        table = Rectangle((table_x, table_y), 360, 40, facecolor="#7a8790", edgecolor="#44515a", linewidth=2)
        self.ax.add_patch(table)

        if self.test:
            self._draw_test_bodies()
        else:
            self._draw_design()

        if self.active_tool:
            self._draw_ghost()

        self.ax.text(CANVAS_WIDTH - 8, 18, "Top-Right Legend", ha="right", va="top", fontsize=8, bbox={"boxstyle": "round", "facecolor": "white"})
        self.canvas.draw_idle()

    def _draw_design(self) -> None:
        for member in self.design.members:
            color = {"beam": "#3a76a8", "column": "#4e5f6b", "brace": "#b56a28"}[member.kind]
            width = 12 if member.kind != "brace" else 7
            self.ax.plot([member.x1, member.x2], [member.y1, member.y2], color=color, linewidth=width, solid_capstyle="round", zorder=3)
            for px, py in ((member.x1, member.y1), (member.x2, member.y2)):
                selected = (
                    member.member_id == self.selected_member_id
                    and (
                        (px, py) == (member.x1, member.y1) and self.selected_member_endpoint == "start"
                        or (px, py) == (member.x2, member.y2) and self.selected_member_endpoint == "end"
                    )
                )
                self.ax.add_patch(Rectangle((px - 5, py - 5), 10, 10,
                                            facecolor="#ffffff" if selected else "#2d2d2d",
                                            edgecolor="#ffffff", linewidth=1.5, zorder=7))
        for mass in self.design.masses:
            self.ax.add_patch(Rectangle((mass.x, mass.y), mass.width, mass.height,
                                        facecolor="#9b6b43", edgecolor="#5a3d28", linewidth=2, zorder=1))

        for x, y in self.design.connected_nodes():
            is_moment = (x, y) in self.design.moment_nodes
            badge = "M" if is_moment else "P"
            self.ax.text(x + 6, y - 8, badge, fontsize=7, color="white", fontweight="bold",
                         ha="center", va="center", zorder=8,
                         bbox={"boxstyle": "circle,pad=0.15", "facecolor": "#b44a52" if is_moment else "#4c6c86"})

    def _draw_test_bodies(self) -> None:
        assert self.test is not None
        for member in self.design.members:
            if member.kind == "brace":
                continue
            body = self.test.member_bodies[member.member_id]
            length_px = member.length_ft * PIXELS_PER_FOOT
            import math
            dx = math.cos(body.angle) * length_px / 2
            dy = -math.sin(body.angle) * length_px / 2
            cx, cy = self.test.to_canvas(body.position.x, body.position.y)
            x1, y1 = cx - dx, cy - dy
            x2, y2 = cx + dx, cy + dy
            color = {"beam": "#3a76a8", "column": "#4e5f6b", "brace": "#b56a28"}[member.kind]
            self.ax.plot([x1, x2], [y1, y2], color=color, linewidth=12 if member.kind != "brace" else 7, zorder=3)
        for mass in self.design.masses:
            body = self.test.mass_bodies[mass.mass_id]
            cx, cy = self.test.to_canvas(body.position.x, body.position.y)
            self.ax.add_patch(Rectangle((cx - mass.width / 2, cy - mass.height / 2), mass.width, mass.height,
                                        facecolor="#9b6b43", edgecolor="#5a3d28", linewidth=2, zorder=1))
        for brace in (m for m in self.design.members if m.kind == "brace"):
            p1 = self._live_node(brace.x1, brace.y1, brace)
            p2 = self._live_node(brace.x2, brace.y2, brace)
            self.ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color="#b56a28",
                         linewidth=7, solid_capstyle="round", zorder=4)
        for node, joint in self.test.joints.items():
            cx, cy = self._live_node(node[0], node[1], None)
            color = {"normal": "#4aa96c", "elevated": "#e0b300", "failed": "#c43a3a"}[joint.state]
            self.ax.add_patch(Rectangle((cx - 5, cy - 5), 10, 10, facecolor=color, edgecolor="#333", zorder=9))

    def _live_node(self, x: float, y: float, brace=None) -> tuple[float, float]:
        assert self.test is not None
        host = None
        for member in self.design.members:
            if member.kind not in ("beam", "column"):
                continue
            ax, ay, bx, by = member.endpoints
            if abs((bx - ax) * (y - ay) - (by - ay) * (x - ax)) <= 2:
                if min(ax, bx) - 2 <= x <= max(ax, bx) + 2 and min(ay, by) - 2 <= y <= max(ay, by) + 2:
                    host = member
                    break
        if host is None:
            px, py = self.test.to_physics(x, y)
            cx, cy = self.test.to_canvas(px, py)
            return cx, cy
        body = self.test.member_bodies[host.member_id]
        initial_position, initial_angle = self.test.member_initial_poses[host.member_id]
        node_px, node_py = self.test.to_physics(x, y)
        local = (pymunk.Vec2d(node_px, node_py) - initial_position).rotated(-initial_angle)
        current = body.local_to_world(local)
        current_px, current_py = current
        return self.test.to_canvas(current_px, current_py)

    def _draw_ghost(self) -> None:
        x, y = self.pointer
        if y > TABLE_TOP_Y:
            y = TABLE_TOP_Y
        if self.active_tool == "mass":
            valid = 0 <= x <= CANVAS_WIDTH - 220 and 0 <= y <= TABLE_TOP_Y - 20
            self.ax.add_patch(Rectangle((x, y), 220, 20, facecolor="#9b6b4388",
                                        edgecolor="#2f8f4e" if valid else "#c43a3a", linestyle="--", zorder=10))
            return
        if self.pending_point is not None:
            x1, y1 = self.pending_point
            if self.active_tool == "beam":
                x2, y2 = x, y1
            elif self.active_tool == "column":
                x2, y2 = x1, y
            else:
                x2, y2 = x, y
            length_valid = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 >= PIXELS_PER_FOOT
            color = "#2f8f4e" if length_valid else "#c43a3a"
            self.ax.plot([x1, x2], [y1, y2], color=color, linewidth=6 if self.active_tool != "brace" else 4,
                         linestyle="--", zorder=11)

    def _on_close(self) -> None:
        self.root.destroy()


def pymunk_node(node: tuple[float, float]) -> tuple[float, float]:
    x, y = node
    import pymunk
    # This helper is replaced below by direct coordinate conversion when needed.
    return x, y


def main() -> None:
    root = tk.Tk()
    EarthquakeApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
