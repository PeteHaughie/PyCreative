import skia
from core.io.replay_to_skia import replay_to_skia_canvas


def test_replay_applies_stroke_cap_and_join(monkeypatch):
    # Capture calls to setStrokeCap/setStrokeJoin
    caps = {}

    orig_setStrokeCap = skia.Paint.setStrokeCap
    orig_setStrokeJoin = skia.Paint.setStrokeJoin

    def spy_setStrokeCap(self, val):
        caps['cap'] = val
        return orig_setStrokeCap(self, val)

    def spy_setStrokeJoin(self, val):
        caps['join'] = val
        return orig_setStrokeJoin(self, val)

    monkeypatch.setattr(skia.Paint, 'setStrokeCap', spy_setStrokeCap)
    monkeypatch.setattr(skia.Paint, 'setStrokeJoin', spy_setStrokeJoin)

    # Build commands: set stroke properties, then draw rect with stroke
    cmds = [
        {'op': 'stroke', 'args': {'color': (10, 20, 30)}},
        {'op': 'stroke_weight', 'args': {'weight': 5}},
        {'op': 'stroke_cap', 'args': {'cap': 'PROJECT'}},
        {'op': 'stroke_join', 'args': {'join': 'BEVEL'}},
        {'op': 'rect', 'args': {'x': 5, 'y': 5, 'w': 10, 'h': 10, 'stroke': (10,20,30), 'stroke_weight': 5}}
    ]

    # Create a small CPU-backed Skia surface and canvas
    surf = skia.Surface(32, 32)
    canvas = surf.getCanvas()

    # Replay commands; our spies should capture cap/join values
    replay_to_skia_canvas(cmds, canvas)

    assert 'cap' in caps and 'join' in caps
    assert caps['cap'] in (skia.Paint.kSquare_Cap, skia.Paint.kButt_Cap, skia.Paint.kRound_Cap)
    assert caps['join'] in (skia.Paint.kMiter_Join, skia.Paint.kBevel_Join, skia.Paint.kRound_Join)
