import json
import collections

import flask
import jinja2

import tournament


web_app = flask.Flask(__name__)

template_loader = jinja2.FileSystemLoader('templates')
web_app.jinja_loader = template_loader


@web_app.route('/')
def index():
    return flask.redirect(flask.url_for('table'))


@web_app.route('/table')
def table():
    args = flask.request.args
    results_filename = args.get('results_filename')

    if results_filename:
        with open(results_filename) as fin:
            results = json.load(fin)
        results = map(tournament.Result.from_json, results)
    else:
        results = []

    maps = sorted(set(result.map for result in results))
    ghostss = sorted(set(tuple(result.ghost_specs) for result in results))

    # ignore different packman_specs for now

    by_map_and_ghosts = collections.defaultdict(list)
    for result in results:
        ghosts = tuple(result.ghost_specs)
        by_map_and_ghosts[result.map, ghosts].append(result)

    return flask.render_template(
        'table.html',
        **locals())


def main():
    web_app.debug = True
    web_app.run()


if __name__ == '__main__':
    main()
