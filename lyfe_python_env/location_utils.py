import random
import math
from typing import List

from lyfe_python_env.datatype.send_in import (
    InLocationShapeCircle,
    InLocationShapeCircleOutline,
    InLocationShapePoint,
    InLocationShapeRect,
    InLocationShapeRectOutline,
    InSpawnLocation,
)
from lyfe_python_env.datatype.unity_transform import UnityTransform
from lyfe_python_env.datatype.unity_vector3 import UnityVector3


def random_point_in_circle(radius: float):
    """Generate a random point in a circle with a given radius."""
    angle = random.uniform(0, 2 * math.pi)
    r = math.sqrt(random.uniform(0, radius**2))
    x = r * math.cos(angle)
    z = r * math.sin(angle)
    return x, z


def random_point_on_circle(radius: float):
    """Generate a random point on the circumference of a circle with a given radius."""
    angle = random.uniform(0, 2 * math.pi)
    x = radius * math.cos(angle)
    z = radius * math.sin(angle)
    return x, z


def random_point_in_rect(x: float, z: float):
    """Generate a random point in a rectangle."""
    return random.uniform(-x / 2, x / 2), random.uniform(-z / 2, z / 2)


def random_point_on_rect(x: float, z: float):
    """Generate a random point on the outline of a rectangle."""
    which_side = random.choice(["top", "bottom", "left", "right"])
    if which_side == "top":
        return random.uniform(-x / 2, x / 2), z / 2
    if which_side == "bottom":
        return random.uniform(-x / 2, x / 2), -z / 2
    if which_side == "left":
        return -x / 2, random.uniform(-z / 2, z / 2)
    if which_side == "right":
        return x / 2, random.uniform(-z / 2, z / 2)


def pick_random_location(spawn_locations: List[InSpawnLocation]):
    """Pick a random location from the spawn locations."""
    spawn_location = random.choice(spawn_locations)
    transform = spawn_location.transform

    if isinstance(spawn_location.shape, InLocationShapeCircle):
        dx, dz = random_point_in_circle(spawn_location.shape.radius)
    elif isinstance(spawn_location.shape, InLocationShapeCircleOutline):
        dx, dz = random_point_on_circle(spawn_location.shape.radius)
    elif isinstance(spawn_location.shape, InLocationShapeRect):
        dx, dz = random_point_in_rect(spawn_location.shape.x, spawn_location.shape.z)
    elif isinstance(spawn_location.shape, InLocationShapeRectOutline):
        dx, dz = random_point_on_rect(spawn_location.shape.x, spawn_location.shape.z)
    elif isinstance(spawn_location.shape, InLocationShapePoint):
        dx, dz = 0, 0  # No need to modify, it's a single point

    # Update the UnityTransform based on the random point (dx, dz)
    transform.x += dx
    transform.z += dz

    return UnityTransform(
        position=UnityVector3(
            x=transform.x + dx,
            y=transform.y,
            z=transform.z + dy,
        ),
        rotation=UnityVector3(
            x=transform.rotation.x,
            y=random.uniform(0, 360),
            z=transform.rotation.z,
        ),
    )
