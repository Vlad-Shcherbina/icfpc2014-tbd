import logging
import sys

sys.path.append('../production/')

import tournament


def main():
    logging.basicConfig(level=logging.WARNING)
    tournament.logger.setLevel(logging.INFO)
    results = tournament.play_tournament(
        # maps=[
        #     'default_map.txt',
        #     'gen/hz.txt',
        #     '../../twigil_scratch/map_91_91_100_10.txt',
        # ],
        maps=tournament.all_rotations(tournament.all_maps(max_size=1500)),
        lm_specs=[
            #'py:lm_ai.NearestPill(straight=True)',
            'py:lm_ai.TunnelDigger()',
            'py:lm_wave.Wavy(50)',
            'py:lm_ff.ForceField()',
        ],
        ghost_team_specs=[
            #['py:GhostAI_Random', 'ghc:miner.ghc', 'ghc:fickle.ghc', 'ghc:flipper.ghc'],  # degenerate scum
            #['py:GhostAI_Shortest'],
            #['py:GhostAI_Red', 'py:GhostAI_Pink'],
            #['py:GhostAI_Red'],
            #['py:RedSplitter'],
            #['py:GhostAI_Red', 'py:Splitters'],
            #['py:GhostAI_Red', 'py:Splitters', 'py:Splitters'],
            #['py:GhostAI_Red', 'py:Splitters', 'py:Splitters', 'py:Splitters'],
            #['ghosthon:../data/ghosts/red.ghy'],
            ['ghc:red.ghc'],
            ['ghosthon:../data/ghosts/redsplitt.ghy'],
            #['py:Hunter'],
        ],
        parallel=True)

    tournament.save_results(results, '../data/some_results.json')


if __name__ == '__main__':
    main()
