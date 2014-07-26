import json
import collections
import base64

import flask
import jinja2

import tournament
import stats


web_app = flask.Flask(__name__)

template_loader = jinja2.FileSystemLoader('templates')
web_app.jinja_loader = template_loader


@web_app.template_filter('data_uri')
def data_uri(s, mime='text/plain'):
    assert isinstance(s, basestring), type(s)
    return 'data:{};base64,{}'.format(mime, base64.b64encode(s))


@web_app.template_filter('render_aggregate_results')
def render_aggregate_results(results):
    #scores = [result.score for result in results]
    score = stats.Distribution()
    for result in results:
        score.add_value(result.score / result.baseline_score())
    #return '{} results'.format(len(results))
    return flask.Markup('<b>{}</b>'.format(score.to_html()))
    #assert isinstance(s, basestring), type(s)
    #return 'data:{};base64,{}'.format(mime, base64.b64encode(s))


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
    lms = sorted(set(result.lm_spec for result in results))
    ghostss = sorted(set(tuple(result.ghost_specs) for result in results))


    # ignore different packman_specs for now

    by_map_lm_ghosts = collections.defaultdict(list)
    by_lm_ghosts = collections.defaultdict(list)
    for result in results:
        ghosts = tuple(result.ghost_specs)
        by_map_lm_ghosts[result.map, result.lm_spec, ghosts].append(result)
        by_lm_ghosts[result.lm_spec, ghosts].append(result)

    return flask.render_template(
        'table.html',
        **locals())


def main():
    web_app.debug = True
    web_app.run()


if __name__ == '__main__':
    main()
