# Written by Claude (vibe-coded), not by the template's author.
"""Build time report: Ninja's log plus clang's -ftime-trace files.

    sh build.sh -p <preset> -c -bt          # clang presets write traces by default
    python3 .gcst/scripts/build_times.py [build_dir] [-n N] [-md] [--color auto|always|never]

Per translation unit (from <object>.json; without a trace only Total is known):
  Total       whole compiler run
  Frontend    parsing and semantic analysis, split into parts that add up:
    headers     inside #include'd files, with templates instantiated while parsing them
    templates   template instantiation outside headers, mostly at the end of the TU
    other       the .cpp itself, plus events shorter than the trace granularity
  Backend     optimization and code generation

clang 23 writes 'Total Source' only for some TUs, so header time is summed here
from the individual include events.
"""

import argparse
import json
import os
import re
import shutil
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import groupby
from pathlib import Path

OBJECT_SUFFIXES = ('.o', '.obj')
SCAN_SUFFIXES = ('.ddi', '.modmap', '.dd', '.json')  # C++20 module scanning jobs
TRACE_NAME = re.compile(r'\.(c|cc|cpp|cxx|c\+\+)\.json$')
TOTALS = {'Total ExecuteCompiler': 'total', 'Total Frontend': 'frontend', 'Total Backend': 'backend'}
INSTANTIATIONS = ('InstantiateFunction', 'InstantiateClass')

BOLD, DIM, YELLOW = '1', '2', '33'
# Bar segments differ by shading too, so they stay readable without colors
SEGMENTS = [('headers', '█', '34'), ('templates', '▓', '35'), ('other', '▒', '37'), ('backend', '░', '33')]
NO_TRACE_BAR = '┄'
BAR_COLORS = {char: color for _, char, color in SEGMENTS} | {NO_TRACE_BAR: DIM}
BAR_WIDTH = 24
PARALLEL_WARNING = 1.5


@dataclass
class NinjaLog:
    times: dict = field(default_factory = dict)  # latest job time per output, over all runs
    last_run: set = field(default_factory = set)
    wall: float = 0.0
    busy: float = 0.0
    runs: int = 0

    def is_full(self):
        return self.last_run == set(self.times)


@dataclass
class Trace:
    total: float
    frontend: float
    backend: float
    headers: float
    templates: float
    header_times: dict
    template_times: dict

    @property
    def other(self):
        return max(0.0, self.frontend - self.headers - self.templates)


@dataclass
class Unit:
    name: str
    output: str
    total: float | None
    trace: Trace | None
    rebuilt: bool


class Painter:
    def __init__(self, enabled):
        self.enabled = enabled

    def __call__(self, text, *codes):
        codes = [code for code in codes if code]
        if not self.enabled or not codes or not text:
            return text
        return f"\033[{';'.join(codes)}m{text}\033[0m"

    def bar(self, text):
        return ''.join(self(char * len(list(run)), BAR_COLORS.get(char, '')) for char, run in groupby(text))


# ---------------------------------------------------------------------------- reading

def read_ninja_log(build_dir):
    path = build_dir / '.ninja_log'
    if not path.is_file():
        return None

    log = NinjaLog()
    runs = [[]]
    prev_end = -1
    with open(path) as file:
        for line in file:
            if line.startswith('#'):
                continue
            start, end, _, output, *_ = line.rstrip('\n').split('\t')
            start, end = int(start), int(end)
            # Jobs are logged in completion order, so a smaller end time starts a new run
            if end < prev_end:
                runs.append([])
            prev_end = end
            runs[-1].append((output, start, end))
            log.times[output] = (end - start) / 1000

    last = runs[-1]
    log.last_run = {output for output, _, _ in last}
    log.wall = max((end for _, _, end in last), default = 0) / 1000
    log.busy = sum(end - start for _, start, end in last) / 1000
    log.runs = len(runs)
    return log


def short_header(path):
    path = path.replace('\\', '/')
    if '/include/' in path:
        path = path.rsplit('/include/', 1)[1]
    std = re.sub(r'^(?:.*/)?c\+\+/(?:v1|\d+)/', '', path)
    if std != path and '/' not in std and '.' not in std:
        return f'<{std}>'
    return std


def strip_template_args(name):
    result = []
    depth = 0
    for char in name:
        if char == '<':
            depth += 1
        elif char == '>':
            depth -= 1
        elif depth == 0:
            result.append(char)
    return ''.join(result)


def covered(intervals):
    total = 0
    reached = None
    for begin, end, *_ in sorted(intervals):
        if reached is None or begin > reached:
            total += end - begin
            reached = end
        elif end > reached:
            total += end - reached
            reached = end
    return total


def inclusive_and_self(spans):
    """spans: properly nested (begin, end, name). Returns {name: (inclusive, self)} in seconds."""
    spans = sorted(spans, key = lambda span: (span[0], -span[1]))
    own = [end - begin for begin, end, _ in spans]
    stack = []
    for index, (begin, end, _) in enumerate(spans):
        while stack and spans[stack[-1]][1] <= begin:
            stack.pop()
        if stack:
            own[stack[-1]] -= end - begin
        stack.append(index)

    result = defaultdict(lambda: [0.0, 0.0])
    for (begin, end, name), self_time in zip(spans, own):
        result[name][0] += (end - begin) / 1e6
        result[name][1] += max(0, self_time) / 1e6
    return dict(result)


def read_trace(path):
    try:
        data = json.loads(path.read_text())
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or 'traceEvents' not in data:
        return None

    totals = {}
    sources = []
    open_sources = []
    instantiations = []
    functions = []
    for event in data['traceEvents']:
        name = event.get('name', '')
        phase = event.get('ph')
        detail = event.get('args', {}).get('detail', '?')
        if name in TOTALS:
            totals[TOTALS[name]] = event['dur'] / 1e6
        elif name == 'Source' and phase == 'X':
            sources.append((event['ts'], event['ts'] + event['dur'], short_header(detail)))
        elif name == 'Source' and phase == 'b':
            # Newer clang: a begin/end pair per include, written when the include ends
            open_sources.append((event['ts'], short_header(detail)))
        elif name == 'Source' and phase == 'e' and open_sources:
            begin, header = open_sources.pop()
            sources.append((begin, event['ts'], header))
        elif name in INSTANTIATIONS:
            span = (event['ts'], event['ts'] + event['dur'], strip_template_args(detail))
            instantiations.append(span)
            if name == 'InstantiateFunction':
                functions.append(span)

    if 'total' not in totals:
        return None

    in_headers = covered(sources)
    return Trace(
        total = totals['total'],
        frontend = totals.get('frontend', 0.0),
        backend = totals.get('backend', 0.0),
        headers = in_headers / 1e6,
        templates = (covered(sources + instantiations) - in_headers) / 1e6,
        header_times = inclusive_and_self(sources),
        template_times = inclusive_and_self(functions),
    )


def source_name(output):
    name = re.sub(r'CMakeFiles/[^/]+\.dir/', '', output)
    for suffix in OBJECT_SUFFIXES:
        name = name.removesuffix(suffix)
    return name


def read_units(build_dir, log):
    times = log.times if log else {}
    traces = {}
    stale = 0

    for path in build_dir.rglob('*.json'):
        if not TRACE_NAME.search(path.name):
            continue
        stem = path.relative_to(build_dir).as_posix().removesuffix('.json')
        output = next((stem + s for s in OBJECT_SUFFIXES if stem + s in times or (build_dir / (stem + s)).exists()), None)
        if output is None:
            continue
        trace = read_trace(path)
        if trace is None:
            continue
        # The object was rebuilt later without -ftime-trace: the trace describes an older compile
        target = build_dir / output
        if target.exists() and target.stat().st_mtime > path.stat().st_mtime + 1:
            stale += 1
            continue
        traces[output] = trace

    objects = {output for output in times if output.endswith(OBJECT_SUFFIXES)} | set(traces)
    units = []
    for output in objects:
        trace = traces.get(output)
        total = trace.total if trace else times.get(output)
        rebuilt = log is None or log.runs == 1 or output in log.last_run
        units.append(Unit(source_name(output), output, total, trace, rebuilt))
    units.sort(key = lambda unit: unit.total or 0.0, reverse = True)
    return units, stale


def merge(units, attribute):
    merged = defaultdict(lambda: [0.0, 0.0, 0])
    for unit in units:
        if unit.trace is None:
            continue
        for name, (inclusive, self_time) in getattr(unit.trace, attribute).items():
            merged[name][0] += inclusive
            merged[name][1] += self_time
            merged[name][2] += 1
    return merged


# ---------------------------------------------------------------------------- rendering

def fit_text(text, width, cut):
    if len(text) <= width:
        return text
    return '…' + text[-(width - 1):] if cut == 'left' else text[:width - 1] + '…'


def terminal_width():
    return shutil.get_terminal_size((120, 24)).columns


def column_widths(columns, rows, groups):
    widths = [max([len(label)] + [len(row[i][0]) for row in rows if row]) for i, (label, _) in enumerate(columns)]
    for group in {g for g in groups if g}:
        members = [i for i, g in enumerate(groups) if g == group]
        span = sum(widths[i] for i in members) + 3 * (len(members) - 1)
        if len(group) > span:
            widths[members[-1]] += len(group) - span
    return widths


def box_table(columns, rows, paint, groups = None, shrink = None):
    """columns: (label, align); rows: lists of (text, codes) or None for a rule.
    codes == 'bar' paints the text as a bar. shrink: (column, 'left'|'right') to fit the terminal."""
    count = len(columns)
    groups = groups or [''] * count
    same = [bool(groups[i]) and groups[i] == groups[i + 1] for i in range(count - 1)]
    widths = column_widths(columns, rows, groups)

    if shrink:
        column, _ = shrink
        excess = sum(widths) + 3 * count + 1 - terminal_width()
        if excess > 0:
            widths[column] = max(16, widths[column] - excess)

    def cell(text, codes, index):
        if shrink and index == shrink[0]:
            text = fit_text(text, widths[index], shrink[1])
        align = columns[index][1]
        padded = text.ljust(widths[index]) if align == '<' else text.rjust(widths[index])
        return paint.bar(padded) if codes == 'bar' else paint(padded, *codes)

    def rule(left, mid, right, merged = None):
        parts = [left]
        for i in range(count):
            parts.append('─' * (widths[i] + 2))
            if i < count - 1:
                parts.append(merged if merged and same[i] else mid)
        return ''.join(parts) + right

    lines = [rule('┌', '┬', '┐', merged = '─')]
    if any(groups):
        parts = ['│']
        i = 0
        while i < count:
            j = i
            while j < count - 1 and same[j]:
                j += 1
            span = sum(widths[i:j + 1]) + 3 * (j - i)
            parts.append(' ' + paint(groups[i].center(span), BOLD) + ' │')
            i = j + 1
        lines.append(''.join(parts))

        parts = ['├' if groups[0] else '│']
        for i in range(count):
            parts.append(('─' if groups[i] else ' ') * (widths[i] + 2))
            if i < count - 1:
                left, right = bool(groups[i]), bool(groups[i + 1])
                parts.append('┬' if same[i] else '┼' if left and right else '┤' if left else '├' if right else '│')
        lines.append(''.join(parts) + ('┤' if groups[-1] else '│'))

    lines.append('│' + '│'.join(' ' + cell(label, (BOLD,), i) + ' ' for i, (label, _) in enumerate(columns)) + '│')
    lines.append(rule('├', '┼', '┤'))
    for row in rows:
        if row is None:
            lines.append(rule('├', '┼', '┤'))
        else:
            lines.append('│' + '│'.join(' ' + cell(text, codes, i) + ' ' for i, (text, codes) in enumerate(row)) + '│')
    lines.append(rule('└', '┴', '┘'))
    return '\n'.join(lines)


def markdown_table(columns, rows):
    rows = [row for row in rows if row is not None]
    widths = [max([len(label)] + [len(row[i][0]) for row in rows]) for i, (label, _) in enumerate(columns)]

    def line(cells):
        padded = [text.ljust(widths[i]) if columns[i][1] == '<' else text.rjust(widths[i]) for i, text in enumerate(cells)]
        return '| ' + ' | '.join(padded) + ' |'

    separator = '|' + '|'.join('-' * (widths[i] + 2) if align == '<' else '-' * (widths[i] + 1) + ':' for i, (_, align) in enumerate(columns)) + '|'
    return '\n'.join([line([label for label, _ in columns]), separator] + [line([text for text, _ in row]) for row in rows])


def seconds(value):
    return '—' if value is None else f'{value:.2f}'


def number(value, *codes):
    return (seconds(value), (DIM,) if value is None else codes)


def make_bar(unit, scale):
    if unit.total is None:
        return ''
    if unit.trace is None:
        return NO_TRACE_BAR * max(1, round(unit.total * scale))
    text = ''
    reached = 0.0
    for key, char, _ in SEGMENTS:
        reached += getattr(unit.trace, key)
        text += char * (round(reached * scale) - len(text))
    return text


# ---------------------------------------------------------------------------- report

def headline(log, units, paint, markdown):
    if log is None:
        return [paint('No .ninja_log: wall clock is unknown (it exists only with the Ninja generator)', YELLOW)]

    rebuilt = [unit for unit in units if unit.output in log.last_run]
    linked = [t for o, t in log.times.items() if o in log.last_run and not o.endswith(OBJECT_SUFFIXES + SCAN_SUFFIXES)]
    parallel = log.busy / log.wall if log.wall else 1.0
    kind = 'full build' if log.is_full() else f'incremental, {len(rebuilt)} of {len(units)} TUs rebuilt'

    rows = [('Build', f'{log.wall:.2f} s', f'{kind} · {len(log.last_run)} jobs · ×{parallel:.1f} in parallel')]
    slowest = max((unit for unit in rebuilt if unit.total is not None), key = lambda unit: unit.total, default = None)
    if slowest and log.wall:
        rows.append(('Slowest TU', f'{slowest.total:.2f} s', f'{slowest.name} · {100 * slowest.total / log.wall:.0f} % of the build'))
    if linked:
        rows.append(('Link', f'{sum(linked):.2f} s', f"{len(linked)} {'job' if len(linked) == 1 else 'jobs'}: archives and executables"))

    if markdown:
        return [f'- **{label}:** {value} — {note}' for label, value, note in rows]
    return [f'  {paint(label.ljust(10), BOLD)}  {paint(value.rjust(7), BOLD)}   {note}' for label, value, note in rows]


def units_table(units, paint, markdown):
    # Without any trace the Frontend / Backend columns would be all dashes, so they are dropped
    keys = ['frontend', 'headers', 'templates', 'other', 'backend'] if any(unit.trace for unit in units) else []
    slowest = units[0].total if units else None

    rows = []
    for unit in units:
        name = unit.name if unit.rebuilt else unit.name + ' †'
        row = [(name, () if unit.rebuilt else (DIM,)), number(unit.total, BOLD if unit.total == slowest else '')]
        rows.append(row + [number(getattr(unit.trace, key) if unit.trace else None) for key in keys])

    def column_sum(pick):
        values = [pick(unit) for unit in units]
        return None if not values or None in values else sum(values)

    def traced(key):
        return lambda unit: getattr(unit.trace, key) if unit.trace else None

    sums = [column_sum(lambda unit: unit.total)] + [column_sum(traced(key)) for key in keys]
    rows.append(None)
    rows.append([(f'Σ  {len(units)} TUs', (BOLD,))] + [number(value, BOLD) for value in sums])

    labels = ['Translation unit', 'Total', 'Σ', 'headers', 'templates', 'other', 'Backend'][:2 + len(keys)]
    aligns = ['<'] + ['>'] * (len(labels) - 1)
    if markdown:
        labels[2:6] = ['Frontend', '↳ headers', '↳ templates', '↳ other'][:len(keys)]
        return markdown_table(list(zip(labels, aligns)), rows), False

    groups = ['', '', 'Frontend', 'Frontend', 'Frontend', 'Frontend', ''][:len(labels)]
    # The bar takes what the terminal has left, between 8 and BAR_WIDTH cells.
    # It is dropped when keeping it would cut file names below 24 characters
    widths = column_widths(list(zip(labels, aligns)), rows, groups)
    left = terminal_width() - (sum(widths) + 3 * len(widths) + 1) - 3
    if left < 8 and 8 - left > widths[0] - 24:
        return box_table(list(zip(labels, aligns)), rows, paint, groups = groups, shrink = (0, 'left')), False
    bar_width = max(8, min(BAR_WIDTH, left))
    scale = bar_width / max((unit.total or 0.0 for unit in units), default = 1.0)

    rows = [row + [(make_bar(unit, scale), 'bar')] for row, unit in zip(rows, units)] + [None, rows[-1] + [('', ())]]
    columns = list(zip(labels, aligns)) + [(' ' * bar_width, '<')]
    return box_table(columns, rows, paint, groups = groups + [''], shrink = (0, 'left')), True


def notes(log, units, stale, paint, has_bar):
    lines = []
    if any(unit.trace for unit in units):
        if has_bar:
            legend = '   '.join(paint.bar(char * 2) + ' ' + key for key, char, _ in SEGMENTS)
            lines.append(f'{legend}   {paint.bar(NO_TRACE_BAR * 2)} no trace')
        lines.append(paint('Frontend Σ = headers + templates + other. Instantiations done while parsing a header count as headers.', DIM))
    else:
        lines.append(paint('No -ftime-trace data, only Total is known. Traces are written by clang presets, on a fresh build: -c', YELLOW))

    if log and log.wall and log.busy / log.wall > PARALLEL_WARNING:
        lines.append(paint(f'×{log.busy / log.wall:.1f} jobs ran at once, so every per-file time is inflated by sharing cores.', YELLOW))
        lines.append(paint('Compare rows with each other. For exact seconds build in one thread: sh build.sh -p <preset> -c -prl 1', YELLOW))
    if any(not unit.rebuilt for unit in units):
        lines.append(paint('† not rebuilt in the last run: the time is from an earlier run.', DIM))
    if stale:
        lines.append(paint(f'{stale} trace(s) older than their object files were ignored (rebuilt without -ftime-trace).', DIM))
    return lines


def top_table(title, label, merged, top, paint, markdown):
    rows = sorted(merged.items(), key = lambda item: item[1][0], reverse = True)[:top]
    rows = [[(name, ()), number(inclusive), number(self_time), (str(count), ()), number(inclusive / count)] for name, (inclusive, self_time, count) in rows]
    columns = [(label, '<'), ('incl.', '>'), ('self', '>'), ('TUs', '>'), ('avg incl.', '>')]
    if markdown:
        return f'**{title}**\n\n' + markdown_table(columns, rows)
    groups = ['', 'Σ over TUs', 'Σ over TUs', '', '']
    return paint(title, BOLD) + '\n' + box_table(columns, rows, paint, groups = groups, shrink = (0, 'right'))


def main():
    argvParser = argparse.ArgumentParser(prog = 'build_times', description = 'Build time report from .ninja_log and -ftime-trace files')
    argvParser.add_argument('build_dir', nargs = '?', default = 'build', type = Path)
    argvParser.add_argument('-n', '--top', type = int, default = 10, help = 'rows in the header and template tables')
    argvParser.add_argument('-md', '--markdown', action = 'store_true', help = 'Markdown tables, no colors and bars')
    argvParser.add_argument('--color', choices = ['auto', 'always', 'never'], default = 'auto')
    args = argvParser.parse_args()

    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding = 'utf-8')
    if not args.build_dir.is_dir():
        sys.exit(f"No build directory '{args.build_dir}'")

    color = args.color == 'always' or (
        args.color == 'auto' and not args.markdown and sys.stdout.isatty() and 'NO_COLOR' not in os.environ
        and (os.name != 'nt' or 'WT_SESSION' in os.environ)
    )
    paint = Painter(color)

    log = read_ninja_log(args.build_dir)
    units, stale = read_units(args.build_dir, log)
    if not units:
        sys.exit(f"Neither .ninja_log nor -ftime-trace files in '{args.build_dir}'")

    print('\n'.join(headline(log, units, paint, args.markdown)))
    print()
    table, has_bar = units_table(units, paint, args.markdown)
    print(table)
    print('\n'.join(notes(log, units, stale, paint, has_bar)))

    if any(unit.trace for unit in units) and args.top > 0:
        print()
        print(top_table('Headers', 'Header', merge(units, 'header_times'), args.top, paint, args.markdown))
        print(paint('incl. counts nested #includes, so rows overlap. self does not: all self values add up to the headers column.', DIM))
        print()
        print(top_table('Function templates', 'Function template', merge(units, 'template_times'), args.top, paint, args.markdown))
        print(paint('incl. counts nested instantiations, so rows overlap. self does not.', DIM))


if __name__ == '__main__':
    main()
