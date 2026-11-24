"""Pymunk-backed fixed-step simulation for the tower."""

from dataclasses import dataclass
from math import pi

import pymunk

from calculations import (
    CANVAS_WIDTH,
    PIXELS_PER_FOOT,
    TABLE_TOP_Y,
    GRAVITY_MODES,
    table_acceleration,
    table_motion,
)
from structure_model import DesignState


@dataclass
class JointState:
    point: tuple[float, float]
    member_ids: list[str]
    constraints: list[pymunk.Constraint]
    demand_kips: float = 0.0
    state: str = "normal"
    failed: bool = False
    fatigue_damage: float = 0.0
    fatigue_half_cycles: float = 0.0
    max_bending_deg: float = 0.0
    fatigue_angle_previous: float | None = None
    fatigue_slope_previous: float = 0.0
    fatigue_peak: float = 0.0


class TestSimulation:
    def __init__(
        self,
        design: DesignState,
        gravity_name: str,
        amplitude: float,
        frequency: float,
        duration_seconds: float | None = None,
    ):
        self.design = design
        self.gravity_name = gravity_name
        self.amplitude = amplitude
        self.frequency = frequency
        self.duration_seconds = duration_seconds
        self.space = pymunk.Space()
        self.space.gravity = (0, -GRAVITY_MODES[gravity_name] * PIXELS_PER_FOOT)
        self.elapsed = 0.0
        self.accumulator = 0.0
        self.fixed_step = 1.0 / 60.0
        self.result: str | None = None
        self.result_time: float | None = None
        self.duration_reached = False
        self.table_motion_stopped = False
        self.joints: dict[tuple[float, float], JointState] = {}
        self.member_bodies: dict[str, pymunk.Body] = {}
        self.member_initial_poses: dict[str, tuple[pymunk.Vec2d, float]] = {}
        self.member_shapes: dict[str, pymunk.Shape] = {}
        self.mass_bodies: dict[str, pymunk.Body] = {}
        self.mass_supported: set[str] = set()
        self.mass_free_fall_started: dict[str, float | None] = {}
        self.mass_free_fall_previous_y: dict[str, float] = {}
        self.mass_wild_motion_started: dict[str, float | None] = {}
        self.table_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.table_body.position = (CANVAS_WIDTH / 2, -10)
        self.table_shape = pymunk.Poly.create_box(self.table_body, (360, 20))
        self.table_shape.sensor = False
        self.table_shape.collision_type = 10
        self.table_shape.friction = 0.9
        self.table_shape.elasticity = 0.05
        self.space.add(self.table_body, self.table_shape)
        def ignore_collision(arbiter, _space, _data):
            arbiter.process_collision = False
        self.space.on_collision(1, 1, begin=ignore_collision)
        self._build_structure()

    def to_physics(self, x: float, y: float) -> tuple[float, float]:
        return x - CANVAS_WIDTH / 2, TABLE_TOP_Y - y

    def to_canvas(self, x: float, y: float) -> tuple[float, float]:
        return x + CANVAS_WIDTH / 2, TABLE_TOP_Y - y

    def _build_structure(self) -> None:
        for member in self.design.members:
            if member.kind == "brace":
                continue
            p1 = self.to_physics(member.x1, member.y1)
            p2 = self.to_physics(member.x2, member.y2)
            length_px = ((p2[0] - p1[0]) ** 2 + (p2[1] - p1[1]) ** 2) ** 0.5
            length_ft = length_px / PIXELS_PER_FOOT
            mass = max(length_ft * 0.20, 0.05)
            body = pymunk.Body()
            body.position = ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2)
            angle = __import__("math").atan2(p2[1] - p1[1], p2[0] - p1[0])
            body.angle = angle
            shape = pymunk.Poly.create_box(body, (length_px, 12))
            shape.mass = mass
            shape.friction = 0.8
            shape.collision_type = 1
            shape.elasticity = 0.05
            self.space.add(body, shape)
            self.member_bodies[member.member_id] = body
            self.member_initial_poses[member.member_id] = (pymunk.Vec2d(*body.position), float(body.angle))
            self.member_shapes[member.member_id] = shape

        for mass in self.design.masses:
            center_px = mass.x + mass.width / 2 - CANVAS_WIDTH / 2
            center_y = TABLE_TOP_Y - (mass.y + mass.height / 2)
            body = pymunk.Body(1.0, pymunk.moment_for_box(1.0, (mass.width, mass.height)))
            body.position = (center_px, center_y)
            shape = pymunk.Poly.create_box(body, (mass.width, mass.height))
            shape.friction = 0.7
            shape.collision_type = 2
            shape.elasticity = 0.05
            if not self._is_mass_supported(mass):
                shape.sensor = False
            else:
                shape.sensor = False
                self.mass_supported.add(mass.mass_id)
            self.space.add(body, shape)
            self.mass_bodies[mass.mass_id] = body
            self.mass_free_fall_started[mass.mass_id] = None
            self.mass_free_fall_previous_y[mass.mass_id] = body.position.y
            self.mass_wild_motion_started[mass.mass_id] = None

        self._build_joint_constraints()
        self._build_brace_constraints()
        self._constrain_supported_masses()
        self._constrain_base_members()

    def _build_brace_constraints(self) -> None:
        for brace in (m for m in self.design.members if m.kind == "brace"):
            hosts: list[tuple[object, tuple[float, float]]] = []
            for point in ((brace.x1, brace.y1), (brace.x2, brace.y2)):
                for host in (h for h in self.design.members if h.kind in ("beam", "column")):
                    if self._point_on_segment(point, host):
                        hosts.append((host, point))
                        break
            if len(hosts) != 2:
                continue
            host1, point1 = hosts[0]
            host2, point2 = hosts[1]
            body1 = self.member_bodies[host1.member_id]
            body2 = self.member_bodies[host2.member_id]
            phys1 = pymunk.Vec2d(*self.to_physics(*point1))
            phys2 = pymunk.Vec2d(*self.to_physics(*point2))
            local1 = (phys1 - body1.position).rotated(-body1.angle)
            local2 = (phys2 - body2.position).rotated(-body2.angle)
            distance = (phys2 - phys1).length
            # A distance joint keeps the brace ends fixed apart when attached to member bodies.
            distance_joint = pymunk.SlideJoint(body1, body2, local1, local2, distance, distance)
            self.space.add(distance_joint)

    def _is_mass_supported(self, mass) -> bool:
        left = mass.x
        right = mass.x + mass.width
        bottom_edge = mass.y + mass.height
        for beam in (m for m in self.design.members if m.kind == "beam"):
            beam_y = beam.y1
            if abs(bottom_edge - beam_y) < 2 and left >= min(beam.x1, beam.x2) - 1 and right <= max(beam.x1, beam.x2) + 1:
                return True
        return False

    def _build_joint_constraints(self) -> None:
        node_to_members: dict[tuple[float, float], list[str]] = {}
        for member in self.design.members:
            for point in ((member.x1, member.y1), (member.x2, member.y2)):
                node_to_members.setdefault(point, []).append(member.member_id)
            if member.kind in ("beam", "column"):
                continue

        # Brace endpoints and ordinary beam/column endpoints create coincident joint groups.
        for brace in (m for m in self.design.members if m.kind == "brace"):
            for host in (h for h in self.design.members if h.kind in ("beam", "column")):
                for point in ((brace.x1, brace.y1), (brace.x2, brace.y2)):
                    if self._point_on_segment(point, host):
                        node = point
                        node_to_members.setdefault(node, []).append(brace.member_id)
                        if host.member_id not in node_to_members[node]:
                            node_to_members[node].append(host.member_id)

        for point, member_ids in node_to_members.items():
            structural_ids = [
                member_id for member_id in member_ids
                if member_id in self.member_bodies
            ]
            if len(structural_ids) < 2:
                continue
            constraints: list[pymunk.Constraint] = []
            physical = self.to_physics(*point)
            first_body = self.member_bodies[structural_ids[0]]
            for member_id in structural_ids[1:]:
                body = self.member_bodies[member_id]
                local1 = pymunk.Vec2d(*physical) - first_body.position
                local1 = local1.rotated(-first_body.angle)
                local2 = pymunk.Vec2d(*physical) - body.position
                local2 = local2.rotated(-body.angle)
                pin = pymunk.PivotJoint(first_body, body, local1, local2)
                pin.damping = 0.8
                self.space.add(pin)
                constraints.append(pin)
                if point in self.design.moment_nodes:
                    lever = 1.25 * PIXELS_PER_FOOT
                    motor = pymunk.RotaryLimitJoint(first_body, body, first_body.angle - lever / 100, first_body.angle + lever / 100)
                    motor.max_force = 100000
                    self.space.add(motor)
                    constraints.append(motor)
            self.joints[point] = JointState(point, member_ids, constraints)

    def _point_on_segment(self, point, member) -> bool:
        x, y = point
        ax, ay, bx, by = member.x1, member.y1, member.x2, member.y2
        if abs((bx - ax) * (y - ay) - (by - ay) * (x - ax)) > 2:
            return False
        return min(ax, bx) - 2 <= x <= max(ax, bx) + 2 and min(ay, by) - 2 <= y <= max(ay, by) + 2

    def _constrain_supported_masses(self) -> None:
        for mass in self.design.masses:
            if mass.mass_id not in self.mass_supported:
                continue
            body = self.mass_bodies[mass.mass_id]
            left_node = (mass.x, mass.y + mass.height)
            right_node = (mass.x + mass.width, mass.y + mass.height)
            supporting_beam = None
            for beam in (m for m in self.design.members if m.kind == "beam"):
                if abs(mass.y + mass.height - beam.y1) < 2:
                    if mass.x >= min(beam.x1, beam.x2) and mass.x + mass.width <= max(beam.x1, beam.x2):
                        supporting_beam = beam
                        break
            if supporting_beam is None:
                continue
            beam_body = self.member_bodies[supporting_beam.member_id]
            for node in (left_node, right_node):
                phys = pymunk.Vec2d(*self.to_physics(*node))
                mass_local = (phys - body.position).rotated(-body.angle)
                beam_local = phys - beam_body.position
                beam_local = beam_local.rotated(-beam_body.angle)
                pin = pymunk.PivotJoint(body, beam_body, mass_local, beam_local)
                self.space.add(pin)

    def _constrain_base_members(self) -> None:
        for member in self.design.members:
            if member.kind != "column":
                continue
            for point in ((member.x1, member.y1), (member.x2, member.y2)):
                if abs(point[1] - TABLE_TOP_Y) < 2:
                    body = self.member_bodies[member.member_id]
                    phys = pymunk.Vec2d(*self.to_physics(*point))
                    local = phys - body.position
                    local = local.rotated(-body.angle)
                    table_local = phys - self.table_body.position
                    pin = pymunk.PivotJoint(self.table_body, body, table_local, local)
                    self.space.add(pin)

    def set_table_motion(self) -> None:
        if self.table_motion_stopped:
            center_y = -10
            self.table_body.position = (CANVAS_WIDTH / 2, center_y)
            self.table_body.velocity = (0, 0)
            return
        displacement_px, velocity_ftps = table_motion(self.elapsed, self.amplitude, self.frequency)
        center_y = -10
        self.table_body.position = (CANVAS_WIDTH / 2 + displacement_px, center_y)
        velocity_pxps = velocity_ftps * PIXELS_PER_FOOT
        self.table_body.velocity = (velocity_pxps, 0)

    def step(self, dt: float) -> None:
        self.accumulator += dt
        while self.accumulator >= self.fixed_step:
            self.elapsed += self.fixed_step
            self.set_table_motion()
            self.space.step(self.fixed_step)
            self._keep_bodies_above_table()
            self._update_joint_stress()
            if self._structural_collapse_detected():
                if self.result is None:
                    self.result = "failure"
                    self.result_time = self.elapsed
            if self._floor_mass_ground_collision():
                if self.result is None:
                    self.result = "failure"
                    self.result_time = self.elapsed
            if self.duration_seconds is not None and self.elapsed >= self.duration_seconds:
                if self.result is None:
                    self.result = "success"
                    self.result_time = self.duration_seconds
                self.duration_reached = True
                self.table_motion_stopped = True
            self.accumulator -= self.fixed_step

    def _update_joint_stress(self) -> None:
        horizontal = table_acceleration(self.elapsed, self.amplitude, self.frequency)
        for node, joint in list(self.joints.items()):
            if joint.failed:
                continue
            self._update_fatigue(joint)
            tributary_mass = 0.0
            for member in self.design.members:
                if member.member_id not in joint.member_ids:
                    continue
                length_ft = member.length_ft
                tributary_mass += length_ft * 0.10
            for mass in self.design.masses:
                if mass.mass_id in self.mass_supported:
                    if self._point_supports_mass(node, mass):
                        tributary_mass += 0.5
            resultant = ((GRAVITY_MODES[self.gravity_name]) ** 2 + horizontal ** 2) ** 0.5
            demand = tributary_mass * resultant * 0.01
            joint.demand_kips = demand
            if demand > 15 or joint.fatigue_damage >= 100:
                joint.failed = True
                joint.state = "failed"
                for constraint in joint.constraints:
                    if constraint in self.space.constraints:
                        self.space.remove(constraint)
            elif demand >= 10:
                joint.state = "elevated"
            else:
                joint.state = "normal"

    def _point_supports_mass(self, node: tuple[float, float], mass) -> bool:
        return node in ((mass.x, mass.y + mass.height), (mass.x + mass.width, mass.y + mass.height))

    def _update_fatigue(self, joint: JointState) -> None:
        connected_bodies = [
            self.member_bodies[member_id]
            for member_id in joint.member_ids
            if member_id in self.member_bodies
        ]
        if len(connected_bodies) < 2:
            return
        bending_deg = abs(
            (connected_bodies[1].angle - connected_bodies[0].angle) * 180.0 / 3.141592653589793
        )
        bending_deg = min(bending_deg, 180.0)
        joint.max_bending_deg = max(joint.max_bending_deg, bending_deg)
        if joint.fatigue_angle_previous is None:
            joint.fatigue_angle_previous = bending_deg
            return
        difference = bending_deg - joint.fatigue_angle_previous
        slope = 1 if difference > 0 else (-1 if difference < 0 else 0)
        if (
            joint.fatigue_slope_previous != 0
            and slope != 0
            and slope != joint.fatigue_slope_previous
            and abs(joint.fatigue_peak - bending_deg) >= 0.5
        ):
            amplitude = abs(bending_deg - joint.fatigue_peak)
            if amplitude >= 1.0:
                if amplitude >= 10.0:
                    damage_increment = 20.0
                elif amplitude >= 6.0:
                    damage_increment = 100.0 / 15.0
                elif amplitude >= 3.0:
                    damage_increment = 2.5
                else:
                    damage_increment = 1.0
                joint.fatigue_damage = min(100.0, joint.fatigue_damage + damage_increment)
                joint.fatigue_half_cycles += 1.0
                joint.fatigue_peak = bending_deg
        elif slope != 0:
            joint.fatigue_peak = max(joint.fatigue_peak, bending_deg) if slope > 0 else min(joint.fatigue_peak, bending_deg)
        joint.fatigue_angle_previous = bending_deg
        joint.fatigue_slope_previous = slope

    def _floor_mass_ground_collision(self) -> bool:
        for mass in self.design.masses:
            body = self.mass_bodies[mass.mass_id]
            canvas_bottom = TABLE_TOP_Y - body.position.y + mass.height / 2
            if canvas_bottom >= TABLE_TOP_Y - 1:
                return True
        return False

    def _structural_collapse_detected(self) -> bool:
        if not self.design.masses:
            return False

        for mass in self.design.masses:
            body = self.mass_bodies[mass.mass_id]
            mass_canvas = mass
            cx = body.position.x + CANVAS_WIDTH / 2
            cy = TABLE_TOP_Y - body.position.y
            mass_left = cx - mass.width / 2
            mass_right = cx + mass.width / 2
            mass_bottom = cy + mass.height / 2

            supported = False
            for beam in (member for member in self.design.members if member.kind == "beam"):
                beam_left = min(beam.x1, beam.x2)
                beam_right = max(beam.x1, beam.x2)
                beam_y = beam.y1
                vertical_aligned = abs(mass_bottom - beam_y) < 30
                within_span = mass_left >= beam_left - 8 and mass_right <= beam_right + 8
                if vertical_aligned and within_span:
                    supported = True
                    break

            speed = (body.velocity.x * body.velocity.x + body.velocity.y * body.velocity.y) ** 0.5
            angular_speed = abs(body.angular_velocity)
            outside_support = not supported
            wildly_moving = (
                outside_support
                and (
                    speed > 220
                    and (angular_speed > 0.8 or abs(body.velocity.y) > 180)
                )
            )

            if wildly_moving:
                if self.mass_wild_motion_started[mass.mass_id] is None:
                    self.mass_wild_motion_started[mass.mass_id] = self.elapsed
            else:
                self.mass_wild_motion_started[mass.mass_id] = None

            started = self.mass_wild_motion_started[mass.mass_id]
            if started is not None and self.elapsed - started >= 0.35:
                return True
        return False

    def _keep_bodies_above_table(self) -> None:
        table_top_physics_y = 0.0
        for body in list(self.member_bodies.values()) + list(self.mass_bodies.values()):
            half_height = 6
            if body in self.mass_bodies.values():
                mass_id = next(
                    mass_id
                    for mass_id, mass_body in self.mass_bodies.items()
                    if mass_body is body
                )
                half_height = self.design.masses[
                    next(
                        index
                        for index, mass in enumerate(self.design.masses)
                        if mass.mass_id == mass_id
                    )
                ].height / 2
            minimum_center_y = table_top_physics_y + half_height
            if body.position.y < -30:
                body.position = (body.position.x, minimum_center_y)
                if body.velocity.y < 0:
                    body.velocity = (body.velocity.x, 0)

    def stop(self) -> None:
        self.space = pymunk.Space()
