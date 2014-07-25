
class Result(object):
    __slots__ = [
        'map',  # path relative to data/maps
        'pacman_spec',
        'ghost_specs',  # list
        'score',
        'ticks',
    ]
    # For now pacman and ghost specs representation is not defined.
    # Let's assume they are json-able objects, strings maybe.

    # Another possible extension would be to keep count of game events
    # (how many lifes lost, how many ghosts, powerpills and fruits eaten)

    def to_json(self):
        return dict(
            map=self.map,
            pacman_spec=self.pacman_spec,
            ghost_specs=self.ghost_specs,
            score=self.score,
            ticks=self.ticks)

    @staticmethod
    def from_json(data):
        result = Result()
        for k, v in data.items():
            setattr(result, k, v)
        return result
