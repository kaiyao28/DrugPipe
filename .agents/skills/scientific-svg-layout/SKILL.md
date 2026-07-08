---
name: scientific-svg-layout
description: Create or revise scientific SVG workflow diagrams, analysis maps and method schematics with strict layout QA. Use when SVG figures have text overflow, clipping, card overlap, inconsistent alignment, or disconnected/floating arrows. Do not use for ordinary statistical plots.
---

# Scientific SVG Layout

Use this skill when creating or revising scientific workflow diagrams, analysis
maps, method schematics or architecture figures in SVG.

The skill has one job: scientific SVG layout quality. It is not for ordinary
statistical plots such as scatter plots, forest plots, heatmaps or PCA plots.

Priority order:

1. semantic correctness;
2. geometric correctness;
3. readability;
4. visual hierarchy;
5. aesthetics.

Do not place SVG elements by visual guesswork alone. Treat every card, label and
connector as a geometric object with explicit bounds and anchors.

## Default Approach

Prefer direct SVG editing for simpler figures.

For complex figures with repeated nodes or persistent coordinate/layout errors,
consider programmatic SVG generation. Prefer direct SVG editing for simpler
figures.

Before finalising any SVG:

1. define layout regions;
2. define card dimensions, padding and alignment;
3. wrap text deliberately;
4. verify text fits inside cards;
5. place connectors from source/target anchors;
6. render the SVG;
7. inspect at full size and approximately 1000 px README width;
8. iterate until layout defects are resolved.

## Cards

Every card must have explicit internal padding.

Recommended minimum padding:

- horizontal padding: at least 28 px;
- top padding: at least 22 px;
- bottom padding: at least 18 px;
- title-to-subtitle spacing: at least 12 px.

Text must not touch or cross card boundaries.

Cards in the same semantic group should share:

- width;
- height;
- corner radius;
- title baseline;
- subtitle baseline;
- row and column spacing.

Do not resize one card casually because its text is longer. First check whether
the whole group needs a larger shared card size or whether the text should wrap.

## Text Wrapping And Fit

SVG text does not reliably wrap automatically. Use explicit `<tspan>` elements
for wrapped lines.

Example:

```svg
<text class="card-title" x="220" y="180">
  <tspan x="220" dy="0">Expression +</tspan>
  <tspan x="220" dy="26">cell context</tspan>
</text>
```

Before finalising:

- estimate or measure rendered text width;
- compare it with usable card width;
- wrap text deliberately;
- increase shared card dimensions where necessary;
- check title/subtitle vertical spacing after wrapping.

Recommended minimum font sizes for README-width SVGs:

- figure title: 34-42 px;
- figure subtitle: 18-22 px;
- card title: 19-24 px;
- card subtitle: 14-17 px;
- small labels: 13-15 px.

Do not reduce font size below readability just to force a label into a card.

## Grid Alignment

Use a defined alignment grid for repeated cards.

For module grids, define:

- column x positions;
- row y positions;
- shared card width and height;
- column and row gaps.

Avoid arbitrary one-off nudges. If an element needs nudging, first check whether
the grid constants or text wrapping rules are wrong.

## Connectors

Every connector should use source and target anchors derived from the connected
objects.

Useful anchors include:

- `top`;
- `bottom`;
- `left`;
- `right`;
- `top_left`;
- `top_right`;
- `bottom_left`;
- `bottom_right`.

Arrowheads must visibly attach to targets:

- the shaft should reach the target boundary;
- the arrowhead should terminate at or immediately before the card edge;
- the arrow must not float in whitespace;
- the arrow must not penetrate deep into the target card;
- the arrow must not cross text.

Use simple connector topology:

1. straight line;
2. orthogonal connector;
3. one gentle curve.

Avoid long bus lines, decorative curves, crossing connectors and dense DAG-like
layouts unless they are scientifically necessary.

For modular scientific analysis maps, prefer grouping, brackets, shared layers
and labelled zones over forcing every dependency into a separate arrow.

## Validation

Before finalising, check:

- card overlap;
- text outside cards;
- text clipping;
- title/subtitle collisions;
- card bounds against safe canvas margins;
- connector source/target anchors;
- visible arrow attachment;
- connector crossings through unrelated cards or text;
- bottom content margin.

Use safe canvas margins. Recommended:

- left: at least 50 px;
- right: at least 50 px;
- top: at least 30 px;
- bottom: at least 40 px.

If content exceeds the canvas, increase the canvas. Do not crop content to keep
a predetermined size.

## Rendering

Always render after edits. Inspect:

- full-size output;
- approximately 1000 px wide output to simulate GitHub README display.

Use whatever renderer is available in the workspace, such as `rsvg-convert`,
`inkscape`, browser automation, `sharp`, or an equivalent SVG renderer.

Do not claim the layout is correct based only on SVG source inspection.

## QA Checklist

- [ ] no text outside a card;
- [ ] no text clipped;
- [ ] no card overlap;
- [ ] no arrow floating away from its source or target;
- [ ] no arrow crossing text;
- [ ] no connector crossing an unrelated card;
- [ ] same-group cards have consistent dimensions;
- [ ] section headings align with their regions;
- [ ] bottom content is inside the canvas;
- [ ] the diagram remains readable at approximately 1000 px width;
- [ ] decorative elements do not imply false connections.

Iterate until all relevant checks pass.
