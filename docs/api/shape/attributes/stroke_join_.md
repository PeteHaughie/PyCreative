[docs](/docs/)→[api](/docs/api)→[shape](/docs/api/shape/)→[attributes](/docs/api/shape/attributes/)→[stroke_join()](/docs/api/shape/attributes/stroke_join_/)

# stroke_join()

## Description

Sets the style of the joints which connect line segments. These joints are either mitered, beveled, or rounded and specified with the corresponding parameters `MITER`, `BEVEL`, and `ROUND`. The default joint is `MITER`.

Examples

```py
"""
size(400, 400);
noFill();
strokeWeight(40.0);
strokeJoin(MITER);
beginShape();
vertex(140, 80);
vertex(260, 200);
vertex(140, 320);
endShape();
"""
```

```py
"""
size(400, 400);
noFill();
strokeWeight(40.0);
strokeJoin(BEVEL);
beginShape();
vertex(140, 80);
vertex(260, 200);
vertex(140, 320);
endShape();
"""
```

```py
"""
size(400, 400);
noFill();
strokeWeight(40.0);
strokeJoin(ROUND);
beginShape();
vertex(140, 80);
vertex(260, 200);
vertex(140, 320);
endShape();
"""
```

## Syntax

stroke_join(join)	

## Parameters

| Inputs | Description |
|--------|-------------|
| join	(int) | either `MITER`, `BEVEL`, or `ROUND` |

## Return

None	

## Related

- [stroke()](/docs/api/shape/attributes/stroke_.md)
- [stroke_weight()](/docs/api/shape/attributes/stroke_weight_.md)
- [stroke_cap()](/docs/api/shape/attributes/stroke_cap_.md)