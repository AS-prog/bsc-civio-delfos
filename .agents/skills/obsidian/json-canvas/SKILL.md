---
name: json-canvas
description: Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian.
---

# JSON Canvas Skill

## File Structure

A canvas file (`.canvas`) contains two top-level arrays following the [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/):

```json
{
  "nodes": [],
  "edges": []
}
```

- `nodes` (optional): Array of node objects
- `edges` (optional): Array of edge objects connecting nodes

## Common Workflows

### 1. Create a New Canvas

1. **Sketch the layout first.** Before writing any JSON, list the major regions (groups), how many children each region holds, and which edges connect across regions. Decide the canvas's overall width by adding region widths + gaps; pick group sizes from this budget, not from defaults.
2. Create a `.canvas` file with the base structure `{"nodes": [], "edges": []}`
3. Generate unique 16-character hex IDs for each node (e.g., `"6f0ad84f44ce9c17"`)
4. **Place groups first**, with their final `x/y/width/height`. Then place children inside each group respecting the padding rules in "Groups: padding and label space".
5. Size every text node to its content using the budgets in "Sizing text nodes to their content".
6. Add edges referencing valid node IDs via `fromNode` and `toNode`. Pick `fromSide`/`toSide` per "Choosing `fromSide` / `toSide`".
7. **Validate** both structure (JSON parses, edge IDs resolve) and layout (run the "Layout" checks in the Validation Checklist).

### 2. Add a Node to an Existing Canvas

1. Read and parse the existing `.canvas` file
2. Generate a unique ID that does not collide with existing node or edge IDs
3. Choose position (`x`, `y`) that avoids overlapping existing nodes (leave 50-100px spacing)
4. Append the new node object to the `nodes` array
5. Optionally add edges connecting the new node to existing nodes
6. **Validate**: Confirm all IDs are unique and all edge references resolve to existing nodes

### 3. Connect Two Nodes

1. Identify the source and target node IDs
2. Generate a unique edge ID
3. Set `fromNode` and `toNode` to the source and target IDs
4. Optionally set `fromSide`/`toSide` (top, right, bottom, left) for anchor points
5. Optionally set `label` for descriptive text on the edge
6. Append the edge to the `edges` array
7. **Validate**: Confirm both `fromNode` and `toNode` reference existing node IDs

### 4. Edit an Existing Canvas

1. Read and parse the `.canvas` file as JSON
2. Locate the target node or edge by `id`
3. Modify the desired attributes (text, position, color, etc.)
4. Write the updated JSON back to the file
5. **Validate**: Re-check all ID uniqueness and edge reference integrity after editing

## Nodes

Nodes are objects placed on the canvas. Array order determines z-index: first node = bottom layer, last node = top layer.

### Generic Node Attributes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `id` | Yes | string | Unique 16-char hex identifier |
| `type` | Yes | string | `text`, `file`, `link`, or `group` |
| `x` | Yes | integer | X position in pixels |
| `y` | Yes | integer | Y position in pixels |
| `width` | Yes | integer | Width in pixels |
| `height` | Yes | integer | Height in pixels |
| `color` | No | canvasColor | Preset `"1"`-`"6"` or hex (e.g., `"#FF0000"`) |

### Text Nodes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `text` | Yes | string | Plain text with Markdown syntax |

```json
{
  "id": "6f0ad84f44ce9c17",
  "type": "text",
  "x": 0,
  "y": 0,
  "width": 400,
  "height": 200,
  "text": "# Hello World\n\nThis is **Markdown** content."
}
```

**Newline pitfall**: Use `\n` for line breaks in JSON strings. Do **not** use the literal `\\n` -- Obsidian renders that as the characters `\` and `n`.

### File Nodes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `file` | Yes | string | Path to file within the system |
| `subpath` | No | string | Link to heading or block (starts with `#`) |

```json
{
  "id": "a1b2c3d4e5f67890",
  "type": "file",
  "x": 500,
  "y": 0,
  "width": 400,
  "height": 300,
  "file": "Attachments/diagram.png"
}
```

### Link Nodes

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `url` | Yes | string | External URL |

```json
{
  "id": "c3d4e5f678901234",
  "type": "link",
  "x": 1000,
  "y": 0,
  "width": 400,
  "height": 200,
  "url": "https://obsidian.md"
}
```

### Group Nodes

Groups are visual containers for organizing other nodes. Position child nodes inside the group's bounds.

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `label` | No | string | Text label for the group |
| `background` | No | string | Path to background image |
| `backgroundStyle` | No | string | `cover`, `ratio`, or `repeat` |

```json
{
  "id": "d4e5f6789012345a",
  "type": "group",
  "x": -50,
  "y": -50,
  "width": 1000,
  "height": 600,
  "label": "Project Overview",
  "color": "4"
}
```

## Edges

Edges connect nodes via `fromNode` and `toNode` IDs.

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `id` | Yes | string | - | Unique identifier |
| `fromNode` | Yes | string | - | Source node ID |
| `fromSide` | No | string | - | `top`, `right`, `bottom`, or `left` |
| `fromEnd` | No | string | `none` | `none` or `arrow` |
| `toNode` | Yes | string | - | Target node ID |
| `toSide` | No | string | - | `top`, `right`, `bottom`, or `left` |
| `toEnd` | No | string | `arrow` | `none` or `arrow` |
| `color` | No | canvasColor | - | Line color |
| `label` | No | string | - | Text label |

```json
{
  "id": "0123456789abcdef",
  "fromNode": "6f0ad84f44ce9c17",
  "fromSide": "right",
  "toNode": "a1b2c3d4e5f67890",
  "toSide": "left",
  "toEnd": "arrow",
  "label": "leads to"
}
```

## Colors

The `canvasColor` type accepts either a hex string or a preset number:

| Preset | Color |
|--------|-------|
| `"1"` | Red |
| `"2"` | Orange |
| `"3"` | Yellow |
| `"4"` | Green |
| `"5"` | Cyan |
| `"6"` | Purple |

Preset color values are intentionally undefined -- applications use their own brand colors.

## ID Generation

Generate 16-character lowercase hexadecimal strings (64-bit random value):

```
"6f0ad84f44ce9c17"
"a3b2c1d0e9f8a7b6"
```

## Layout Guidelines

- Coordinates can be negative (canvas extends infinitely)
- `x` increases right, `y` increases down; position is the top-left corner
- Space nodes 50-100px apart; leave 20-50px padding inside groups
- Align to grid (multiples of 10 or 20) for cleaner layouts

| Node Type | Suggested Width | Suggested Height |
|-----------|-----------------|------------------|
| Small text | 200-300 | 80-150 |
| Medium text | 300-450 | 150-300 |
| Large text | 400-600 | 300-500 |
| File preview | 300-500 | 200-400 |
| Link preview | 250-400 | 100-200 |

### Sizing text nodes to their content

A node that is too short truncates its Markdown content. Estimate height **before** placing the node:

| Element | Vertical budget |
|---------|-----------------|
| `# H1` line | ~45px |
| `## H2` line | ~36px |
| Paragraph / list line | ~22-26px |
| Blank line between blocks | ~14-18px |
| Top + bottom inner padding | ~24-32px total |

Sum the budget for every line in `text` (count `\n` splits, plus headings) and round up to the next multiple of 10. For file nodes the title bar consumes ~24-30px on top of the preview area; budget 50-70px minimum so the filename is not clipped.

### Avoiding overlaps (bounding-box check)

Each node occupies the rectangle `[x, x+width] × [y, y+height]`. Before writing a node, mentally compute `right = x + width` and `bottom = y + height` and confirm:

1. No other node's rectangle intersects this one.
2. The node fits inside any group that should contain it, **with** padding for the group label (see below).
3. Edge labels along the path between connected nodes will not land on top of a third node — leave a clear corridor (~80-120px) between any node and the segment of an edge that carries a label.

When in doubt, prefer extra whitespace; a sparse canvas is readable, a dense one is not.

### Groups: padding and label space

Group nodes are visual containers, not auto-layout. The label is rendered **inside the top of the group**, consuming roughly 40-50px of vertical space. To keep child nodes from colliding with the label or the group border, follow:

- Child `x` ≥ group `x` + 30
- Child `y` ≥ group `y` + 50 (label clearance)
- Child `x + width` ≤ group `x + width` − 30
- Child `y + height` ≤ group `y + height` − 30

If a child node must sit edge-to-edge with another, enlarge the group instead of shrinking the gap.

### Choosing `fromSide` / `toSide`

Pick anchors that produce the shortest straight (or single-bend) path and that do **not** cross over a third node. Quick rules:

- Target is directly below source → `bottom` → `top`
- Target is to the right → `right` → `left`
- Target is below-and-right and you want an L-shaped path → `bottom` → `left` (or `right` → `top`)
- Two parallel siblings of a parent → fan out from `bottom` of the parent into `top` of each child; Obsidian auto-spreads the anchors along the side
- Avoid mixing sides on the same source for edges that should look parallel (e.g., a parent connecting to several siblings should use the same `fromSide` for all of them)

If an edge has a `label`, prefer the side that gives the longest straight segment so the label sits on the line, not on top of a node.

### Edge labels

Edge labels render as a chip floating on the line midpoint. They consume horizontal space proportional to their text length. Guidelines:

- Keep labels under ~20 characters when possible
- Do not place a labelled edge across the body of a third node — re-route via different sides or remove the label
- If the same semantic relation repeats across many edges (e.g., `parent → child` for ten siblings), label only one representative edge instead of all of them
- Redundant labels (e.g., labelling an edge "Dominio X" when the target group is already titled "X") add noise; omit them and rely on edge color to convey the relationship

### Grid layouts for many siblings

When a parent node fans out to >6 children of similar weight, arrange the children in a grid rather than a single row or column. A 3×3 grid with cell `170×50` and 15px gaps fits inside a 580-wide group with room to spare. Keep all cells the same width/height for visual rhythm.

### File paths in `file` nodes

`file` is resolved **relative to the vault root**, not to the canvas file. If a canvas at `vault/notes/board.canvas` references `images/foo.png`, Obsidian looks for `vault/images/foo.png`. When the canvas displays "Crear un nuevo archivo" / "Create new file" for an existing target, the path is wrong: rebuild it from the vault root, including any intermediate folders (`subdir/foo.md`, not `./foo.md`).

## Validation Checklist

After creating or editing a canvas file, verify:

### Structural
1. All `id` values are unique across both nodes and edges
2. Every `fromNode` and `toNode` references an existing node ID
3. Required fields are present for each node type (`text` for text nodes, `file` for file nodes, `url` for link nodes)
4. `type` is one of: `text`, `file`, `link`, `group`
5. `fromSide`/`toSide` values are one of: `top`, `right`, `bottom`, `left`
6. `fromEnd`/`toEnd` values are one of: `none`, `arrow`
7. Color presets are `"1"` through `"6"` or valid hex (e.g., `"#FF0000"`)
8. JSON is valid and parseable

### Layout
9. No two non-group nodes have overlapping bounding boxes
10. Every node intended to belong to a group sits **inside** the group's box with the padding from "Groups: padding and label space"
11. Every text node's `height` is large enough for its content (count lines and headings)
12. No edge with a `label` runs through the body of a third node
13. Edges connecting one parent to multiple children use a consistent `fromSide`
14. `file` paths resolve from the vault root, not from the canvas's folder

If structural validation fails, check for duplicate IDs, dangling edge references, or malformed JSON strings (especially unescaped newlines in text content). If layout validation fails, the typical fixes are: (a) increase the offending node's `width`/`height`, (b) shift it 40-80px away from the conflict, (c) re-anchor the problematic edge to a different side, or (d) drop a redundant edge label.

## Common Pitfalls

These are bugs that have actually shipped in canvases produced by this skill. Check for them after every edit.

- **Header nodes overlap fan-out edges.** Placing reference notes directly below a central node, with the three "domain" group edges also fanning out from that same `bottom` anchor, causes the edges to cross the reference notes. Move reference notes to a side anchor (`left`/`right`) or above the central node.
- **Sub-grid children collide with the descriptive caption above them.** When a caption node ends at `y=Y` and the first row of sub-children starts at `y=Y`, the row visually fuses with the caption. Leave 20-30px between the caption's bottom and the first child's top.
- **Edge labels stack on the destination node.** When a labelled edge has a very short horizontal run (source and target nearly aligned), the label chip lands on the target. Either lengthen the run by re-anchoring, or remove the label and rely on color.
- **Text node truncated because height was guessed.** Headings (`#`, `##`) and code blocks add vertical pixels not visible in a glance at the source string. When in doubt, oversize by ~20% — empty space is harmless, truncated content is not.
- **Group label hidden behind a child node.** A child placed at `y = group.y + 0..40` covers the group label. Always start the first row at `group.y + 50` or below.
- **Long cross-canvas edge with a label.** An edge that spans most of the canvas width with a `label` produces a chip floating in the middle of unrelated content. Either split the relationship into a closer intermediate node or drop the label.
- **`file` path written relative to the canvas instead of the vault root.** Obsidian shows "Create new file" even though the file exists. Rebuild the path from the vault root.

## Complete Examples

See [references/EXAMPLES.md](references/EXAMPLES.md) for full canvas examples including mind maps, project boards, research canvases, and flowcharts.

## References

- [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/)
- [JSON Canvas GitHub](https://github.com/obsidianmd/jsoncanvas)
