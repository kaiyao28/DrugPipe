---
name: scientific-workflow-figure
description: Create or revise scientific and technical workflow figures from a text description, existing SVG or workflow specification. Use for pipelines, analysis maps, method schematics, modular workflows and data-processing diagrams. Interpret workflow structure, choose an appropriate layout pattern, route connectors with Graphviz or ELK when needed, render the result and fix clipping, overlap or disconnected arrows. Do not use for statistical charts such as bar plots, Manhattan plots, PCA or volcano plots.
---

# Scientific Workflow Figure

Convert a scientific or technical workflow concept into a visually correct
workflow figure.

Use this skill for reusable scientific/technical diagrams across repositories
and domains: data-cleaning workflows, post-GWAS analysis maps, method
schematics, modular evidence maps, computational pipelines and review loops.

## Core Workflow

1. Understand the workflow before drawing.
2. Classify the workflow pattern.
3. Build or update a semantic YAML workflow specification.
4. Choose direct SVG, Graphviz or ELK-style routing based on complexity.
5. Generate DOT/SVG when using Graphviz.
6. Render full-size and approximately 1000 px previews.
7. Inspect for clipping, overlap, floating arrows and false dependencies.
8. Iterate by changing the semantic spec, layout constraints, Graphviz settings,
   node sizes or text wrapping.

Preserve scientific meaning. Do not make a figure symmetrical by inventing
dependencies, implying sequential execution for independent modules, or implying
causality when the workflow only supports association.

## Understand The Workflow

Extract:

- nodes or stages;
- semantic groups;
- inputs and outputs;
- dependencies;
- branches;
- convergence points;
- optional or independently accessible modules.

If the description is ambiguous, infer the simplest scientifically defensible
structure from repository context. Ask for clarification only when the ambiguity
would materially change scientific meaning.

## Classify The Pattern

Use `references/workflow-patterns.md` when deciding between:

- `linear`;
- `branched`;
- `convergent`;
- `modular`;
- `layered`;
- `cyclic`.

Use pattern classification to choose direction, grouping, edge visibility and
Graphviz settings.

## Choose The Layout Engine

For at most five nodes and at most three simple connectors, direct SVG editing
is acceptable.

For hierarchical, modular, branched or convergent workflows, prefer Graphviz
DOT. Use `scripts/spec_to_dot.py` to convert a semantic YAML specification into
DOT, then `scripts/render_graphviz.py` to render DOT to SVG.

For complex compound graphs or persistent routing problems, consider ELK/elkjs
if available in the workspace.

Do not manually hard-code complex Bezier edge paths when an automatic graph
routing engine is appropriate. Do not manually patch Graphviz edge paths in a
generated SVG.

## Semantic Specification

Build a simple YAML specification before generating the figure:

```yaml
figure:
  title: Data-cleaning workflow
  subtitle: From raw tables to reviewed analysis-ready data
  pattern: linear
  direction: LR

nodes:
  - id: raw
    title: Raw data
    subtitle: imported tables
    theme: input

  - id: schema
    title: Schema validation
    subtitle: columns and types
    theme: analysis

edges:
  - source: raw
    target: schema

groups:
  - id: qc
    label: Quality control
    nodes: [schema]
```

Users should normally edit YAML node titles, subtitles, groups and semantic
edges. They should not need to edit SVG coordinates.

## Usage Examples

Example 1:

```text
$scientific-workflow-figure

Create a workflow for data cleaning:

raw data
-> schema validation
-> missingness QC
-> duplicate removal
-> type harmonisation
-> cleaned data
-> QC report

Output:
docs/assets/data-cleaning-workflow.svg
```

Example 2:

```text
$scientific-workflow-figure

Create a modular analysis map showing:
GWAS QC, fine-mapping, QTL colocalisation, expression, pathway analysis, MR and
druggability feeding standard evidence tables, with figures, interpretation and
target integration as downstream uses.
```

Example 3:

```text
$scientific-workflow-figure

Review the existing workflow SVG and fix text clipping and disconnected arrows
without changing the scientific topology.
```

## Bundled Resources

- `scripts/spec_to_dot.py`: validate a YAML workflow specification and generate
  Graphviz DOT without manual SVG coordinates or edge geometry.
- `scripts/render_graphviz.py`: render DOT to SVG, validate SVG XML, check
  expected node/edge labels and optionally create a PNG preview.
- `references/layout-guidance.md`: layout QA rules for padding, wrapping,
  connector attachment, rendering and inspection.
- `references/workflow-patterns.md`: supported workflow patterns and their
  scientific meaning.
- `assets/themes.yaml`: default semantic themes for nodes.

Read the relevant reference files when a task needs those details. For Graphviz
figures, inspect and adapt `assets/themes.yaml` before generating DOT.

## Output Handling

For repository figures:

- save the semantic spec near the figure or under `docs/assets`;
- generate DOT as an intermediate artifact when useful;
- generate SVG as the displayed artifact;
- document the generation command when the repo does not already have one;
- keep source specs and scripts as the maintainable editing surface.

For one-off figures, temporary YAML and DOT files may be removed after
successful SVG generation unless the user requests reproducibility.

When given an existing SVG or image, inspect the scientific content,
reconstruct the semantic workflow, preserve approved content, and convert to
the semantic graph specification where useful. Do not redraw blindly.

## Visual QA

Always render after edits. Inspect:

- full-size preview;
- approximately 1000 px wide preview.

Check:

- no text outside boxes;
- no clipped text;
- no card overlap;
- no disconnected or floating arrows;
- connectors visibly terminate at intended nodes;
- no connector crosses unrelated labels;
- equal semantic cards align consistently;
- sufficient canvas margins;
- figure remains readable at README width;
- decorative elements do not imply false connections.

Iterate until layout defects are resolved.
