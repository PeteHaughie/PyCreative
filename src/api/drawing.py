def line(x1, y1, x2, y2, stroke=(0, 0, 0), stroke_weight=1):
	if x1 == x2 and y1 == y2:
		raise ValueError('line has zero length')
	return {"type": "line", "args": {"x1": x1, "y1": y1, "x2": x2, "y2": y2, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def square(x, y, s, fill=(0, 0, 0), stroke=None, stroke_weight=0):
	if s <= 0:
		raise ValueError('square size must be > 0')
	return {"type": "square", "args": {"x": x, "y": y, "s": s, "fill": tuple(fill) if fill is not None else None, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def rect(x, y, w, h, fill=(0, 0, 0), stroke=None, stroke_weight=0):
	if w <= 0 or h <= 0:
		raise ValueError('rect width and height must be > 0')
	return {"type": "rect", "args": {"x": x, "y": y, "w": w, "h": h, "fill": tuple(fill) if fill is not None else None, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def circle(x, y, r, fill=(0, 0, 0), stroke=None, stroke_weight=0):
	if r <= 0:
		raise ValueError('circle radius must be > 0')
	return {"type": "circle", "args": {"x": x, "y": y, "r": r, "fill": tuple(fill) if fill is not None else None, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def ellipse(x, y, w, h, fill=(0, 0, 0), stroke=None, stroke_weight=0):
	if w <= 0 or h <= 0:
		raise ValueError('ellipse width and height must be > 0')
	return {"type": "ellipse", "args": {"x": x, "y": y, "w": w, "h": h, "fill": tuple(fill) if fill is not None else None, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def triangle(x1, y1, x2, y2, x3, y3, fill=(0, 0, 0), stroke=None, stroke_weight=0):
	# Compute signed area (shoelace). If zero, points are colinear/degenerate.
	area = x1*(y2-y3) + x2*(y3-y1) + x3*(y1-y2)
	if area == 0:
		raise ValueError('triangle is degenerate (zero area)')
	return {"type": "triangle", "args": {"points": [(x1, y1), (x2, y2), (x3, y3)], "fill": tuple(fill) if fill is not None else None, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def quad(x1, y1, x2, y2, x3, y3, x4, y4, fill=(0, 0, 0), stroke=None, stroke_weight=0):
	return {"type": "quad", "args": {"points": [(x1, y1), (x2, y2), (x3, y3), (x4, y4)], "fill": tuple(fill) if fill is not None else None, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def polygon(points, fill=(0, 0, 0), stroke=None, stroke_weight=0):
	return {"type": "polygon", "args": {"points": list(points), "fill": tuple(fill) if fill is not None else None, "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def polyline(points, stroke=(0, 0, 0), stroke_weight=1):
	return {"type": "polyline", "args": {"points": list(points), "stroke": tuple(stroke) if stroke is not None else None, "stroke_weight": int(stroke_weight)}}


def arc(x, y, w, h, start, stop):
	return {"type": "arc", "args": {"x": x, "y": y, "w": w, "h": h, "start": start, "stop": stop}}


def bezier(x1, y1, cx1, cy1, cx2, cy2, x2, y2):
	return {"type": "bezier", "args": {"points": [(x1, y1), (cx1, cy1), (cx2, cy2), (x2, y2)]}}


def text(txt, x, y):
	return {"type": "text", "args": {"text": txt, "x": x, "y": y}}


def background(r, g=None, b=None):
	"""Return a background descriptor.

	Accepts either a single tuple (r,g,b) or three numeric args.
	"""
	if g is None and b is None and isinstance(r, (tuple, list)):
		col = tuple(r)
	else:
		col = (r, g, b)
	return {"type": "background", "args": {"color": tuple(col)}}
