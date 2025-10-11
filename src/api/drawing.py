def line(x1, y1, x2, y2):
	return {"type": "line", "x1": x1, "y1": y1, "x2": x2, "y2": y2}


def square(x, y, s):
	return {"type": "square", "x": x, "y": y, "s": s}


def rect(x, y, w, h):
	return {"type": "rect", "x": x, "y": y, "w": w, "h": h}


def circle(x, y, r):
	return {"type": "circle", "x": x, "y": y, "r": r}


def ellipse(x, y, w, h):
	return {"type": "ellipse", "x": x, "y": y, "w": w, "h": h}


def triangle(x1, y1, x2, y2, x3, y3):
	return {"type": "triangle", "points": [(x1, y1), (x2, y2), (x3, y3)]}


def quad(x1, y1, x2, y2, x3, y3, x4, y4):
	return {"type": "quad", "points": [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]}


def polygon(points):
	return {"type": "polygon", "points": list(points)}


def polyline(points):
	return {"type": "polyline", "points": list(points)}


def arc(x, y, w, h, start, stop):
	return {"type": "arc", "x": x, "y": y, "w": w, "h": h, "start": start, "stop": stop}


def bezier(x1, y1, cx1, cy1, cx2, cy2, x2, y2):
	return {"type": "bezier", "points": [(x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2)]}


def text(txt, x, y):
	return {"type": "text", "text": txt, "x": x, "y": y}
