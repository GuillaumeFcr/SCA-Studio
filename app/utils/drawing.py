from PySide6 import QtGui
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGraphicsEllipseItem

from app.utils.logging import log
from app.utils.positioning import dist, point_on_line

DRAW_SIZE = 5


def draw_point(scene, paths, point):
    """Draw a point"""
    x, y = point
    item = QGraphicsEllipseItem(0, 0, 2 * DRAW_SIZE, 2 * DRAW_SIZE)
    item.setPos(x - DRAW_SIZE, y - DRAW_SIZE)
    item.setPen(QtGui.QPen(QtGui.QColor(0, 255, 0), DRAW_SIZE / 5, Qt.SolidLine))
    item.setBrush(Qt.NoBrush)
    scene.addItem(item)
    paths.append(
        scene.addPath(
            QtGui.QPainterPath(),
            QtGui.QPen(QtGui.QColor(0, 255, 0), DRAW_SIZE / 5, Qt.SolidLine),
        )
    )
    return item


def draw_line(paths, point1, point2):
    """Draw a line between 2 points"""
    if paths:
        path = QtGui.QPainterPath()
        path.moveTo(*point1)
        path.lineTo(*point2)
        paths[-1].setPath(path)


def select_point(points, coord):
    """Select a point at specified coordinates"""
    for i, (_, p) in enumerate(points):
        if dist(coord, p) < DRAW_SIZE:
            return i


def move_point(points, paths, i, point):
    """Move the i-th point to a new position"""
    if not len(points) == 4:
        return
    x, y = point
    points[i][0].setPos(x - DRAW_SIZE, y - DRAW_SIZE)
    for p, p1, p2 in [(0, 0, 1), (-1, -1, 0)]:
        path = QtGui.QPainterPath()
        point1, point2 = points[(i + p1) % 4][0], points[(i + p2) % 4][0]
        path.moveTo(point1.x() + DRAW_SIZE, point1.y() + DRAW_SIZE)
        path.lineTo(point2.x() + DRAW_SIZE, point2.y() + DRAW_SIZE)
        paths[(i + p) % 4].setPath(path)


def clear_draw(scene, points, paths):
    """Clear points and lines"""
    for item, _ in points:
        scene.removeItem(item)
    for item in paths:
        scene.removeItem(item)
    points.clear()
    paths.clear()


def draw_marker(scene, marker, x, y):
    """Draw a marker"""
    clear_marker(scene, marker)
    draw_size = 2 * DRAW_SIZE

    circle = QGraphicsEllipseItem(0, 0, 2 * draw_size, 2 * draw_size)
    circle.setPos(x - draw_size, y - draw_size)
    circle.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), draw_size / 5, Qt.SolidLine))
    circle.setBrush(Qt.NoBrush)

    line1 = QtGui.QPainterPath()
    line1.moveTo(x - draw_size, y - draw_size)
    line1.lineTo(x + draw_size, y + draw_size)

    line2 = QtGui.QPainterPath()
    line2.moveTo(x + draw_size, y - draw_size)
    line2.lineTo(x - draw_size, y + draw_size)

    scene.addItem(circle)
    path1 = scene.addPath(line1, QtGui.QPen(QtGui.QColor(255, 0, 0), draw_size / 5, Qt.SolidLine))
    path2 = scene.addPath(line2, QtGui.QPen(QtGui.QColor(255, 0, 0), draw_size / 5, Qt.SolidLine))

    marker.extend((circle, path1, path2))


def clear_marker(scene, marker):
    """Clear a marker"""
    for item in marker:
        scene.removeItem(item)
    marker.clear()


def draw_grid(scene, points, n, grid):
    """Draw a grid of size n defined by 4 points"""

    def line(point1, point2):
        path = QtGui.QPainterPath()
        path.moveTo(*point1)
        path.lineTo(*point2)
        item = scene.addPath(
            path,
            QtGui.QPen(QtGui.QColor(0, 255, 0), DRAW_SIZE / 5, Qt.SolidLine),
        )
        grid.append(item)

    for i in range(n - 1):
        p1, p2, p3, p4 = (
            points[0],
            points[1],
            points[2],
            points[3],
        )
        point1 = point_on_line(p1, p2, (i + 1) / n)
        point2 = point_on_line(p4, p3, (i + 1) / n)
        point3 = point_on_line(p2, p3, (i + 1) / n)
        point4 = point_on_line(p1, p4, (i + 1) / n)
        line(point1, point2)
        line(point3, point4)

    log(f"Area of interest - added grid(points={points}, n={n})")


def clear_grid(scene, grid):
    """Clear the grid"""
    for item in grid:
        scene.removeItem(item)
    grid.clear()

    log("Area of interest - removed grid")


def display_data(scene, data, displayed_data):
    """Draw measures summary"""
    points = data.keys()
    if not len(points):
        return

    minval = min(data.values())
    maxval = max(data.values())
    for i, (x, y) in enumerate(points):
        draw_size = DRAW_SIZE

        coords = list(data.keys())[:i] + list(data.keys())[i + 1 :]
        dists = [dist(coord, (x, y)) for coord in coords]
        if len(dists) > 0:
            max_draw_size = min(dists) / 4
            if draw_size > max_draw_size:
                draw_size = max_draw_size

        val = 0
        if maxval - minval > 0:
            val = (data[(x, y)] - minval) / (maxval - minval)

        circle = QGraphicsEllipseItem(0, 0, 2 * draw_size, 2 * draw_size)
        circle.setPos(x - draw_size, y - draw_size)
        circle.setPen(QtGui.QPen(QtGui.QColor(255, 0, 0), draw_size / 5, Qt.SolidLine))
        circle.setBrush(QtGui.QColor(255, int(255 * (1 - val)), 0))
        circle.setOpacity(0.2 + 0.6 * val)

        scene.addItem(circle)
        displayed_data.append(circle)


def hide_data(scene, displayed_data):
    """Clear measures summary"""
    try:
        for item in displayed_data:
            scene.removeItem(item)
    except RuntimeError:
        # Handle "Internal C++ object already deleted." (if displayed_data has not been cleaned)
        # This exception can be raised after taking a new photo
        pass
    displayed_data.clear()
