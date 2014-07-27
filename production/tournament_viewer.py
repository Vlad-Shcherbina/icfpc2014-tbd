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

    fruits_eaten = sum(result.fruits_eaten for result in results)
    ghosts_eaten = sum(result.ghosts_eaten for result in results)
    power_pills_eaten = sum(result.power_pills_eaten for result in results)
    #return '{} results'.format(len(results))
    return flask.Markup("""
        <big><b>{}</b><br></big>
        <span class="fruit">{} %</span>;
        <span class="ghost">{} g</span>;
        <span class="power_pill">{} o</span>
        """.format(score.to_html(), fruits_eaten, ghosts_eaten, power_pills_eaten))
    #assert isinstance(s, basestring), type(s)
    #return 'data:{};base64,{}'.format(mime, base64.b64encode(s))


@web_app.route('/')
def index():
    return flask.redirect(flask.url_for('table'))


@web_app.route('/table')
def table():
    args = flask.request.args
    results_filename = args.get('results_filename')
    by_ghosts = bool(args.get('by_ghosts'))

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

    def best_among(result):
        if not by_ghosts:
            ghosts = tuple(result.ghost_specs)
            scores = [r.score for lm in lms for r in by_map_lm_ghosts[result.map, lm, ghosts]]
            return max(scores) == result.score > min(scores)
        else:
            scores = [r.score for ghosts in ghostss for r in by_map_lm_ghosts[result.map, result.lm_spec, ghosts]]
            return min(scores) == result.score < max(scores)

    return flask.render_template(
        'table.html',
        **locals())


def main():
    web_app.debug = True
    web_app.run()


if __name__ == '__main__':
    main()
