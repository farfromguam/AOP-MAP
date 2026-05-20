# Thin Vertical Slices

TL;DR:
- Build one working path before designing the category.
- A slice is narrow, not shallow.
- For AOP, the first real slice is source-led data to QGIS to print/web export.

#practice #slices #build

-----

The first implementation proves the shape.

For map work, a useful slice proves:

1. The source exists.
2. The data can be stored.
3. The map can display it.
4. The confidence and permission are visible.
5. The export path respects publish rules.

That is why the first map slice should not start with every trail. It should start with one or two representative features that travel through the whole spine:

- source register row
- raw import or trace
- core edited feature
- publish view
- QGIS style
- print export
- web export

Once that path works, broaden the layer set.

## Reversible vs. hard to unwind

Reversible: labels, first symbol styles, print layout polish, early layer grouping.

Hard to unwind: CRS policy, source schema, permission model, raw/core/publish split, observation promotion rules.

Lock the hard parts early. Let the visual polish learn.
