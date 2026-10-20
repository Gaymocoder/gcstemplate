import os, sys
import json

FRESH_BINARIES = ('Build', 'Download', 'Update')

def main():
    graph_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join('build', 'graph.json')
    with open(graph_path, 'r', encoding = 'utf-8') as graph_file:
        nodes = json.load(graph_file)['graph']['nodes'].values()

    fresh = [node['ref'] for node in nodes if node.get('binary') in FRESH_BINARIES]
    for ref in fresh:
        print(f"Not from cache: {ref}")
    print(f"Conan cache {'is stale, saving' if fresh else 'is up to date'}")

    with open(os.environ['GITHUB_OUTPUT'], 'a', encoding = 'utf-8') as output:
        output.write(f"save={'true' if fresh else 'false'}\n")

if __name__ == '__main__':
    main()
