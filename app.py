"""Tkinter desktop entry point for the earthquake shake-down simulator."""

from copy import deepcopy
import json
import os
from pathlib import Path
import time
import tkinter as tk
from tkinter import messagebox, ttk
from tkinter import filedialog

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
        self._joint_badges: dict[tuple[float, float], tuple[float, float]] = {}
        self.saved_design: DesignState | None = None
        self.amplitude = 4.0
        self.frequency = 3.0
        self.duration_seconds: float | None = 10.0
        self.gravity_name = "Earth"
        self.result_text = "Ready"
        self.elapsed = 0.0
        self.peak_g = peak_acceleration_g(self.amplitude, self.frequency)
        self.scores = {"Earth": 0.0, "Mars": 0.0, "Moon": 0.0}
        self.last_animation_time = time.perf_counter()

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
        self.tool_buttons = {}
        for label, tool in (
            ("Column", "column"),
            ("Beam", "beam"),
            ("Brace", "brace"),
            ("Floor Mass", "mass"),
        ):
            button = tk.Button(left, text=label, width=12, relief="raised", borderwidth=2,
                               command=lambda t=tool: self._select_tool(t))
            button.pack(pady=2)
            self.tool_buttons[tool] = button
        self._update_tool_button_states()

        canvas_frame = ttk.Frame(main)
        canvas_frame.pack(side="left", fill="both")
        self.figure = Figure(figsize=(6, 5), dpi=100)
        self.figure.patch.set_facecolor("#eef4f8")
        self.ax = self.figure.add_subplot(111)
        self.ax.set_position([0.0, 0.0, 1.0, 1.0])
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
        self.amplitude_var.trace_add("write", lambda *_args: self._set_amplitude(None))
        self.frequency_var.trace_add("write", lambda *_args: self._set_frequency(None))
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
        ttk.Label(sidebar, text="Duration").pack(pady=(6, 2))
        self.duration_var = tk.StringVar(value="10")
        duration_values = [str(value) for value in range(1, 21)] + ["Indefinite"]
        self.duration_box = ttk.Combobox(
            sidebar,
            textvariable=self.duration_var,
            values=duration_values,
            state="readonly",
            width=12,
        )
        self.duration_box.pack(fill="x")
        self.duration_box.bind("<<ComboboxSelected>>", self._set_duration)
        ttk.Button(sidebar, text="Clear Structure", command=self._clear_structure).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Load Starter Tower", command=self._load_starter).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Save Design", command=self._save_design).pack(fill="x", pady=2)
        ttk.Button(sidebar, text="Import Design", command=self._import_design).pack(fill="x", pady=2)

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
                           format="%.1f", command=lambda: callback(None), width=10)
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
        self._update_tool_button_states()
        self._draw()

    def _cancel_tool(self) -> None:
        self.active_tool = None
        self.pending_point = None
        self.selected_member_endpoint = None
        self._update_tool_button_states()
        self._draw()

    def _update_tool_button_states(self) -> None:
        for tool, button in self.tool_buttons.items():
            selected = tool == self.active_tool
            button.configure(
                state="disabled" if self.testing else "normal",
                relief="sunken" if selected else "raised",
                bg="#dcecff" if selected else "#e7e7e7",
                fg="#1f4f78" if selected else "#333333",
                borderwidth=3 if selected else 2,
            )

    def _canvas_position(self, event) -> tuple[float, float]:
        width = self.canvas.get_tk_widget().winfo_width()
        height = self.canvas.get_tk_widget().winfo_height()
        display_x = min(max(event.x, 0), width)
        display_y = min(max(event.y, 0), height)
        x = display_x * CANVAS_WIDTH / max(width, 1)
        y = display_y * CANVAS_HEIGHT / max(height, 1)
        snapped_x = round(x / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
        snapped_y = round(y / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
        return (
            max(0.0, min(float(CANVAS_WIDTH), float(snapped_x))),
            max(0.0, min(float(TABLE_TOP_Y), float(snapped_y))),
        )

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
                x, y = self._canvas_position(event)
                nx = max(0.0, min(float(CANVAS_WIDTH), float(round(x / PIXELS_PER_FOOT) * PIXELS_PER_FOOT)))
                ny = max(0.0, min(float(TABLE_TOP_Y), float(round(y / PIXELS_PER_FOOT) * PIXELS_PER_FOOT)))
                if self.pending_point is None:
                    self.pending_point = (nx, ny)
                else:
                    start_x, start_y = self.pending_point
                    left, right = sorted((start_x, nx))
                    top, bottom = sorted((start_y, ny))
                    width = round((right - left) / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                    height = round((bottom - top) / PIXELS_PER_FOOT) * PIXELS_PER_FOOT
                    if width >= PIXELS_PER_FOOT and height >= PIXELS_PER_FOOT:
                        self.design.add_mass(left, top, width, height)
                        self._cancel_tool()
                        self._refresh_readouts()
                    else:
                        self.pending_point = None
                        self._draw()
            else:
                anchor_x, anchor_y = self.design.snap_structural_node(x, y)
                if self.pending_point is None:
                    self.pending_point = (anchor_x, anchor_y)
                else:
                    x1, y1 = self.pending_point
                    if self.active_tool == "beam":
                        end_x, _ = self.design.snap_structural_node(anchor_x, y1)
                        member = self.design.add_member("beam", x1, y1, end_x, y1)
                    elif self.active_tool == "column":
                        member = self.design.add_member("column", x1, y1, x1, anchor_y)
                    else:
                        member = self.design.add_member("brace", x1, y1, anchor_x, anchor_y)
                    self.pending_point = None
                    self.active_tool = None
                    self._refresh_readouts()
            self._draw()
            return

        for node, badge_center in self._joint_badges.items():
            if ((badge_center[0] - x) ** 2 + (badge_center[1] - y) ** 2) ** 0.5 <= 12:
                self.design.toggle_joint(node[0], node[1])
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
            for endpoint_name, px, py in (
                ("start", mass.x, mass.y),
                ("end", mass.x + mass.width, mass.y + mass.height),
            ):
                if ((px - x) ** 2 + (py - y) ** 2) ** 0.5 <= 10:
                    self.selected_member_id = f"mass:{mass.mass_id}"
                    self.selected_member_endpoint = endpoint_name
                    self.drag_offset = None
                    self._draw()
                    return
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
                if self.selected_member_endpoint:
                    self.design.resize_mass(mass.mass_id, self.selected_member_endpoint, x, y)
                    self._draw()
                    return
                if not self.drag_offset:
                    return
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
                    self.design.resize_member_endpoint(
                        member.member_id,
                        self.selected_member_endpoint,
                        x,
                        y,
                    )
                    self._draw()
                    return
                if not self.drag_offset:
                    return
                dx = x - (member.x1 + self.drag_offset[0])
                dy = y - (member.y1 + self.drag_offset[1])
                self.design.move_member(member.member_id, member.x1 + dx, member.y1 + dy)
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
        value = round(max(0.0, min(12.0, float(value))) * 10.0) / 10.0
        self.amplitude = value
        if abs(self.amplitude_var.get() - value) > 1e-9:
            self.amplitude_var.set(value)
        if self.testing and self.test is not None:
            self.test.amplitude = value
            self.peak_g = peak_acceleration_g(value, self.frequency)
        else:
            self.peak_g = peak_acceleration_g(value, self.frequency)
        self._refresh_readouts()

    def _set_frequency(self, value) -> None:
        if value is None:
            value = self.frequency_var.get()
        value = round(max(0.1, min(10.0, float(value))) * 10.0) / 10.0
        self.frequency = value
        if abs(self.frequency_var.get() - value) > 1e-9:
            self.frequency_var.set(value)
        if self.testing and self.test is not None:
            self.test.frequency = value
            self.peak_g = peak_acceleration_g(self.amplitude, value)
        else:
            self.peak_g = peak_acceleration_g(self.amplitude, value)
        self._refresh_readouts()

    def _set_duration(self, _event=None) -> None:
        if self.testing:
            return
        selected = self.duration_var.get()
        self.duration_seconds = None if selected == "Indefinite" else float(selected)

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

    def _save_design(self) -> None:
        if self.testing:
            return
        path = filedialog.asksaveasfilename(
            title="Save Design",
            defaultextension=".json",
            filetypes=[("Earthquake design", "*.json"), ("JSON files", "*.json")],
            initialfile="earthquake-design.json",
        )
        if not path:
            return
        payload = self.design.to_dict()
        payload.update({
            "gravity": self.gravity_name,
            "amplitude": round(self.amplitude, 1),
            "frequency": round(self.frequency, 1),
            "duration_seconds": self.duration_seconds,
        })
        try:
            Path(path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
            messagebox.showinfo("Design Saved", f"Design saved to:\n{path}")
        except OSError as error:
            messagebox.showerror("Save Error", f"Could not save the design:\n{error}")

    def _import_design(self) -> None:
        if self.testing:
            return
        path = filedialog.askopenfilename(
            title="Import Design",
            filetypes=[("Earthquake design", "*.json"), ("JSON files", "*.json")],
        )
        if not path:
            return
        try:
            payload = json.loads(Path(path).read_text(encoding="utf-8"))
            imported = DesignState.from_dict(payload)
        except (json.JSONDecodeError, OSError, ValueError) as error:
            messagebox.showerror("Import Error", f"Could not import the design:\n{error}")
            return

        gravity = payload.get("gravity", "Earth")
        if gravity not in ("Earth", "Mars", "Moon"):
            messagebox.showerror("Import Error", "The saved gravity mode is invalid.")
            return
        try:
            amplitude = round(max(0.0, min(12.0, float(payload.get("amplitude", 4.0)))) * 10.0) / 10.0
            frequency = round(max(0.1, min(10.0, float(payload.get("frequency", 3.0)))) * 10.0) / 10.0
        except (TypeError, ValueError):
            messagebox.showerror("Import Error", "The saved amplitude or frequency is invalid.")
            return
        duration_value = payload.get("duration_seconds", 10.0)
        if duration_value is None:
            duration_seconds = None
        else:
            try:
                duration_seconds = float(duration_value)
            except (TypeError, ValueError):
                messagebox.showerror("Import Error", "The saved shaking duration is invalid.")
                return
            if not 1.0 <= duration_seconds <= 20.0 or not duration_seconds.is_integer():
                messagebox.showerror("Import Error", "The saved shaking duration must be a whole number from 1 to 20.")
                return
            duration_seconds = float(int(duration_seconds))

        self.design = imported
        self.gravity_name = gravity
        self.amplitude = amplitude
        self.frequency = frequency
        self.duration_seconds = duration_seconds
        self.duration_var.set("Indefinite" if duration_seconds is None else str(int(duration_seconds)))
        self.amplitude_var.set(amplitude)
        self.frequency_var.set(frequency)
        self.active_tool = None
        self.pending_point = None
        self.selected_member_id = None
        self.selected_member_endpoint = None
        self.result_text = "Ready"
        self.elapsed = 0.0
        self.peak_g = peak_acceleration_g(amplitude, frequency)
        self.scores = {name: 0.0 for name in ("Earth", "Mars", "Moon")}
        self._save_scores()
        self._update_gravity_button_states()
        self._update_tool_button_states()
        self._refresh_readouts()
        self._draw()

    def _toggle_test(self) -> None:
        if self.testing:
            self._stop_test()
        else:
            self._start_test()

    def _start_test(self) -> None:
        self.saved_design = deepcopy(self.design)
        self.test = TestSimulation(
            deepcopy(self.design),
            self.gravity_name,
            self.amplitude,
            self.frequency,
            self.duration_seconds,
        )
        self.testing = True
        self.last_animation_time = time.perf_counter()
        self.active_tool = None
        self.pending_point = None
        self._update_tool_button_states()
        self.elapsed = 0.0
        self.peak_g = peak_acceleration_g(self.amplitude, self.frequency)
        self.result_text = "Testing"
        self.start_button.configure(text="Stop Test")
        self.duration_box.configure(state="disabled")
        self._update_gravity_button_states()
        for member in self.design.members:
            pass
        self._refresh_readouts()
        self._draw()

    def _finish_duration_test(self) -> None:
        if not self.testing:
            return
        final_result = "Pass" if self.test and self.test.result == "success" else "Failure"
        if self.saved_design is not None:
            self.design = self.saved_design
        self.saved_design = None
        self.test = None
        self.testing = False
        self.last_animation_time = time.perf_counter()
        self.start_button.configure(text="Start Test")
        self.duration_box.configure(state="readonly")
        self._update_gravity_button_states()
        self._update_tool_button_states()
        self.result_text = final_result
        self._refresh_readouts()
        self._draw()

    def _stop_test(self) -> None:
        if self.saved_design is not None:
            self.design = self.saved_design
        self.saved_design = None
        self.test = None
        self.testing = False
        self.last_animation_time = time.perf_counter()
        self.start_button.configure(text="Start Test")
        self.duration_box.configure(state="readonly")
        self._update_gravity_button_states()
        self._update_tool_button_states()
        self.result_text = "Stopped"
        self._refresh_readouts()
        self._draw()

    def _animation_tick(self) -> None:
        now = time.perf_counter()
        real_delta = max(0.0, now - self.last_animation_time)
        self.last_animation_time = now
        if self.testing and self.test:
            self.test.step(min(real_delta, 0.25))
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
                if self.test.duration_seconds is not None:
                    self._finish_duration_test()
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
        self._joint_badges.clear()
        for member in self.design.members:
            color = {"beam": "#3a76a8", "column": "#4e5f6b", "brace": "#b56a28"}[member.kind]
            is_selected = member.member_id == self.selected_member_id
            if is_selected:
                color = "#ff9f1c"
            width = 12 if member.kind != "brace" else 7
            self.ax.plot([member.x1, member.x2], [member.y1, member.y2], color=color, linewidth=width, solid_capstyle="round", zorder=3)
            mx = (member.x1 + member.x2) / 2
            my = (member.y1 + member.y2) / 2
            length_text = f"{member.length_ft:.1f} ft"
            self.ax.text(mx, my - 14 if member.kind == "beam" else my,
                         length_text, ha="center", va="center", fontsize=8,
                         color="#17233b", rotation=0, zorder=6,
                         bbox={"boxstyle": "round,pad=0.2", "facecolor": "white", "edgecolor": "#d7e1ed"})
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
            is_selected = self.selected_member_id == f"mass:{mass.mass_id}"
            self.ax.add_patch(Rectangle((mass.x, mass.y), mass.width, mass.height,
                                        facecolor="#ffb703" if is_selected else "#9b6b43",
                                        edgecolor="#ff5a1f" if is_selected else "#5a3d28",
                                        linewidth=4 if is_selected else 2, zorder=1))
            for px, py in ((mass.x, mass.y), (mass.x + mass.width, mass.y + mass.height)):
                selected = (
                    self.selected_member_id == f"mass:{mass.mass_id}"
                    and (
                        (px, py) == (mass.x, mass.y) and self.selected_member_endpoint == "start"
                        or (px, py) == (mass.x + mass.width, mass.y + mass.height) and self.selected_member_endpoint == "end"
                    )
                )
                self.ax.add_patch(Rectangle((px - 5, py - 5), 10, 10,
                                            facecolor="#ffffff" if selected else "#5a3d28",
                                            edgecolor="#ffffff", linewidth=1.5, zorder=7))

        for x, y in self.design.connected_nodes():
            is_moment = (x, y) in self.design.moment_nodes
            badge = "M" if is_moment else "P"
            badge_x = x + 6
            badge_y = y - 8
            self._joint_badges[(x, y)] = (badge_x, badge_y)
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
            self.ax.text(cx + 9, cy - 9,
                         f"{joint.fatigue_damage:.0f}% fat.",
                         fontsize=7, color="#2b1b18", fontweight="bold",
                         ha="left", va="bottom", zorder=10,
                         bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": color})

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
            if self.pending_point is None:
                left = min(CANVAS_WIDTH - PIXELS_PER_FOOT, max(0.0, x))
                top = min(TABLE_TOP_Y - PIXELS_PER_FOOT, max(0.0, y))
                width = height = PIXELS_PER_FOOT
            else:
                start_x, start_y = self.pending_point
                left, right = sorted((start_x, x))
                top, bottom = sorted((start_y, y))
                width = max(PIXELS_PER_FOOT, right - left)
                height = max(PIXELS_PER_FOOT, bottom - top)
            valid = left + width <= CANVAS_WIDTH and top + height <= TABLE_TOP_Y
            self.ax.add_patch(Rectangle((left, top), width, height, facecolor="#9b6b4388",
                                        edgecolor="#2f8f4e" if valid else "#c43a3a", linestyle="--", zorder=10))
            return
        if self.pending_point is None:
            x, y = self.design.snap_structural_node(x, y)
            if self.active_tool == "beam":
                width = 3 * PIXELS_PER_FOOT
                valid = x + width <= CANVAS_WIDTH
                self.ax.plot([x, x + width], [y, y], color="#2f8f4e" if valid else "#c43a3a",
                             linewidth=6, linestyle="--", zorder=11)
            elif self.active_tool == "column":
                height = 6 * PIXELS_PER_FOOT
                top = max(0.0, y - height)
                valid = top >= 0
                self.ax.plot([x, x], [top, y], color="#2f8f4e" if valid else "#c43a3a",
                             linewidth=8, linestyle="--", zorder=11)
            else:
                end_x = min(CANVAS_WIDTH, x + 6 * PIXELS_PER_FOOT)
                end_y = min(TABLE_TOP_Y, y + 6 * PIXELS_PER_FOOT)
                end_x, end_y = self.design.snap_structural_node(end_x, end_y)
                valid = ((end_x - x) ** 2 + (end_y - y) ** 2) ** 0.5 >= PIXELS_PER_FOOT
                self.ax.plot([x, end_x], [y, end_y], color="#2f8f4e" if valid else "#c43a3a",
                             linewidth=4, linestyle="--", zorder=11)
                self.ax.add_patch(Rectangle((x - 5, y - 5), 10, 10,
                                            facecolor="#2563eb88", edgecolor="#2563eb",
                                            linestyle="--", zorder=12))
            return
        if self.pending_point is not None:
            x1, y1 = self.pending_point
            if self.active_tool == "beam":
                x2, _ = self.design.snap_structural_node(x, y1)
                y2 = y1
            elif self.active_tool == "column":
                x2, y2 = x1, y
            else:
                x2, y2 = self.design.snap_structural_node(x, y)
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
