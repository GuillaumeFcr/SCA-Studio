import cv2
from math import dist
import numpy as np


def homography(
    img: cv2.typing.MatLike,
    boundaries: list[tuple[int, int], tuple[int, int], tuple[int, int], tuple[int, int]],
    wh_ratio: int,
) -> cv2.typing.MatLike:
    """Apply homography to a target image

    Args:
        img: original image
        boundaries: list of 4 points (x,y) of each points in the original image
        wh_ratio: width/height ratio for the new image

    Returns:
        An image array to which the homography has been applied
    """
    srcPoints = np.array(boundaries)
    dists = [dist(srcPoints[i], srcPoints[i + 1]) for i in range(3)]
    base_size = max(dists)
    if dists.index(base_size) % 2:
        w, h = int(wh_ratio * base_size), int(base_size)
    else:
        w, h = w, h = int(base_size), int(base_size / wh_ratio)
    dstPoints = np.array([(0, 0), (w, 0), (w, h), (0, h)])
    homography, _ = cv2.findHomography(srcPoints, dstPoints)
    new_img = cv2.warpPerspective(img, homography, (w, h))
    return new_img


def real_point(
    x: int, y: int, w: int, h: int, x_bounds: tuple[int, int], y_bounds: tuple[int, int], x_offset: int, y_offset: int
) -> tuple[int, int]:
    """Return real (X,Y) coordinates from image coordinates

    Args:
        x: x-coordinate of the point in the image coordinate system
        y: y-coordinate of the point in the image coordinate system
        w: image width
        h: image height
        x_bounds: tuple of (min, max) coordinate limits of x in the real coordinate system
        y_bounds: tuple of (min, max) coordinate limits of y in the real coordinate system
        x_offset: offset on the x-axis
        y_offset: offset on the y-axis

    Return:
        A tuple of (x,y) coordinates in the real coordinate system
    """
    x_rel = x / w
    y_rel = 1 - y / h  # reverse y axis
    x_real = x_rel * (x_bounds[1] - x_bounds[0]) + x_bounds[0]
    y_real = y_rel * (y_bounds[1] - y_bounds[0]) + y_bounds[0]
    return x_real + x_offset, y_real + y_offset


def img_point(
    x: int, y: int, w: int, h: int, x_bounds: tuple[int, int], y_bounds: tuple[int, int], x_offset: int, y_offset: int
) -> tuple[int, int]:
    """Return image (X,Y) coordinates from real coordinates

    Args:
        x: x-coordinate of the point in the real coordinate system
        y: y-coordinate of the point in the real coordinate system
        w: image width
        h: image height
        x_bounds: tuple of (min, max) coordinate limits of x in the real coordinate system
        y_bounds: tuple of (min, max) coordinate limits of y in the real coordinate system
        x_offset: offset on the x-axis
        y_offset: offset on the y-axis

    Return:
        A tuple of (x,y) coordinates in the image coordinate system
    """
    x -= x_offset
    y -= y_offset
    x_rel = (x - x_bounds[0]) / (x_bounds[1] - x_bounds[0])
    y_rel = (y - y_bounds[0]) / (y_bounds[1] - y_bounds[0])
    x_img = x_rel * w
    y_img = (1 - y_rel) * h  # reverse y axis
    return x_img, y_img


def point_on_line(p1: tuple[int, int], p2: tuple[int, int], x: float) -> tuple[int, int]:
    """Get coordinates of a point at a relative position on a line

    Args:
        p1: first point of the line
        p2: second point of the line
        x: relative position of the point on the line

    Return:
        The coordinates of the point on the line [p1, p2] at the relative position x
    """
    return (
        p1[0] + (p2[0] - p1[0]) * x,
        p1[1] + (p2[1] - p1[1]) * x,
    )


def xy_by_box_number(i, n, points) -> tuple[int, int]:
    """Get coordinates of a box on the grid

    Args:
        i: index of the box
        n: grid size
        points: points that define the grid

    Return:
        The (x, y) coordinates of the i-th box on the grid
    """
    ix, iy = i % n, i // n
    x1, y1 = point_on_line(points[0], points[1], (ix + 0.5) / n)
    x2, y2 = point_on_line(points[3], points[2], (ix + 0.5) / n)

    return point_on_line((x1, y1), (x2, y2), (iy + 0.5) / n)
