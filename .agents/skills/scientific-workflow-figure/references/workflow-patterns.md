# Workflow Patterns

Use this reference to classify the workflow before drawing. Classification
controls direction, grouping, edge visibility and layout engine choice.

## Linear

Pattern:

```text
A -> B -> C -> D
```

Use for ordered processing where each step depends on the previous step.
Typical direction is left-to-right (`LR`) for README figures or top-to-bottom
(`TB`) for narrow documents.

Avoid using linear layouts for independently accessible modules.

## Branched

Pattern:

```text
A -> B
     -> C
     -> D
```

Use when one upstream stage produces multiple downstream analyses or outputs.
Keep branches visually balanced and label optional branches when needed.

## Convergent

Pattern:

```text
A
B -> Integration
C
```

Use when multiple evidence layers, assays or data resources feed a shared
integration step. Align inputs and make convergence visually clear without
overloading the integration node with arrows.

## Modular

Pattern:

```text
Module A
Module B
Module C
        -> shared schemas / outputs
```

Use when users can enter at different analysis modules, analyses can be run
independently, or outputs are reusable between steps. Prefer grouped cards,
shared evidence-table layers and labelled zones. Do not imply one-command
execution or strict sequential dependency.

## Layered

Pattern:

```text
inputs -> analyses -> integration -> outputs
```

Use for architecture-like diagrams where semantic layers matter more than exact
execution order. Use ranks or horizontal bands for each layer.

## Cyclic

Pattern:

```text
model -> evaluate -> review -> refine -> model
```

Use for iterative QC, review, model refinement or analysis feedback loops. Keep
the cycle visually simple and label review/refinement steps so the loop does
not look accidental.

## Layout Engine Guidance

Use direct SVG for at most five nodes and at most three simple connectors.

Use Graphviz DOT for:

- hierarchical workflows;
- branched workflows;
- convergent workflows;
- modular maps;
- layered diagrams.

Consider ELK/elkjs for compound graphs with nested groups or persistent routing
problems.

Do not hand-code complex connector paths when a routing engine can place them.
