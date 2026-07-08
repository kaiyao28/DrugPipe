# Scientific SVG Layout Skill

Use this guidance when creating or revising scientific workflow diagrams,
analysis maps, method schematics or architecture figures in SVG.

Priority order:

1. semantic correctness;
2. geometric correctness;
3. readability;
4. visual hierarchy;
5. aesthetics.

Do not place SVG elements by visual guesswork alone. Treat every card, label and
connector as a geometric object with explicit bounds and anchors.

## Layout Model

Before writing SVG markup, define the layout as structured data. Rectangles,
text positions and connector anchors should be generated from the same node
definition rather than duplicated as independent hard-coded coordinates.

Each node should define:

- `x`, `y`, `width`, `height`;
- title and subtitle lines;
- semantic style;
- padding.

## Text Fitting

SVG text does not wrap automatically. Wrap text deliberately with explicit
lines, estimate rendered width, and validate text against each card's usable
width. Do not reduce text below readable size just to force it into a card.

Recommended minimum sizes for a README SVG:

- title: 34-42 px;
- subtitle: 18-22 px;
- card title: 19-24 px;
- card subtitle: 14-17 px;
- small labels: 13-15 px.

## Cards And Grids

Cards in the same semantic group should share width, height, corner radius,
title baseline and subtitle baseline. Module cards should align to a grid and
use consistent row and column gaps.

Use at least 28 px horizontal padding, 22 px top padding and 18 px bottom
padding. Text must not touch card boundaries.

## Connectors

Every node should expose calculated anchors such as `top`, `bottom`, `left`,
`right`, `top_left`, `top_right`, `bottom_left` and `bottom_right`. Connectors
must start and end at anchors derived from node geometry.

Prefer simple topology:

1. straight line;
2. orthogonal connector;
3. one gentle curve.

Avoid long bus lines, decorative connectors and multiple arrows when a bracket,
grouping boundary or shared evidence layer communicates the relationship more
clearly.

## Validation

Before finalising an SVG, validate:

- no card overlap;
- all cards are inside the canvas with safe margins;
- estimated text width fits inside each card;
- connector source and target nodes exist;
- connectors use named anchors;
- bottom content has comfortable margin.

Render the SVG to PNG and inspect both full size and a reduced README-like
width before claiming completion.

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
- [ ] the diagram remains readable at GitHub README width;
- [ ] decorative elements do not imply false connections.

For figures with more than six cards or repeated structures, prefer generating
the SVG from a small script and committing the generated SVG as the artifact.
