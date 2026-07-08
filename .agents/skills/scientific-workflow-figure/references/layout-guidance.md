# Layout Guidance

Use this reference when creating or revising workflow diagrams, analysis maps,
method schematics or architecture figures.

## Priorities

1. semantic correctness;
2. geometric correctness;
3. readability;
4. visual hierarchy;
5. aesthetics.

Do not place SVG elements by visual guesswork alone. Treat cards, labels and
connectors as bounded objects.

## Cards

Use explicit internal padding:

- horizontal padding: at least 28 px;
- top padding: at least 22 px;
- bottom padding: at least 18 px;
- title-to-subtitle spacing: at least 12 px.

Cards in the same semantic group should share width, height, corner radius,
title baseline, subtitle baseline and spacing. Do not casually resize one card
because its text is longer; first decide whether to wrap the text or increase
the whole group size.

## Text

SVG text does not reliably wrap automatically. Wrap deliberately with explicit
lines or `<tspan>` elements.

Check:

- estimated or measured rendered width;
- usable card width after padding;
- title/subtitle vertical spacing;
- text baseline relative to lower card boundary.

Recommended README figure font sizes:

- figure title: 34-42 px;
- figure subtitle: 18-22 px;
- card title: 19-24 px;
- card subtitle: 14-17 px;
- small labels: 13-15 px.

Do not reduce font size below readability just to force a label into a card.

## Alignment

Use a defined alignment grid for repeated cards:

- column x positions;
- row y positions;
- shared card width and height;
- row and column gaps.

Avoid arbitrary one-off nudges. If a card needs nudging, check the grid,
wrapping and grouping first.

## Connectors

Every connector should use source and target anchors derived from the connected
objects.

Useful anchors:

- `top`;
- `bottom`;
- `left`;
- `right`;
- `top_left`;
- `top_right`;
- `bottom_left`;
- `bottom_right`.

Arrowheads must visibly attach to targets:

- shaft reaches the target boundary;
- arrowhead terminates at or immediately before the card edge;
- arrow does not float in whitespace;
- arrow does not penetrate deep into the card;
- arrow does not cross text.

Prefer simple connector topology:

1. straight line;
2. orthogonal connector;
3. one gentle curve.

Avoid long bus lines, decorative curves, crossing connectors and dense DAG-like
layouts unless the workflow requires them.

For modular analysis maps, prefer grouping, brackets, shared layers and labelled
zones over forcing every relationship into a separate arrow.

## Canvas

Keep meaningful content inside safe margins:

- left: at least 50 px;
- right: at least 50 px;
- top: at least 30 px;
- bottom: at least 40 px.

If content exceeds the canvas, increase the canvas. Do not crop content to keep
a predetermined size.

## Rendering QA

Render after edits and inspect:

- full-size output;
- approximately 1000 px wide output.

Checklist:

- [ ] no text outside a card;
- [ ] no text clipped;
- [ ] no card overlap;
- [ ] no arrow floating away from source or target;
- [ ] no arrow crossing text;
- [ ] no connector crossing an unrelated card;
- [ ] same-group cards have consistent dimensions;
- [ ] section headings align with their regions;
- [ ] bottom content is inside the canvas;
- [ ] diagram remains readable at approximately 1000 px width;
- [ ] decorative elements do not imply false connections.
