from math import sqrt


class Distribution(object):
    def __init__(self):
        self.n = 0
        self.sum = 0
        self.sum2 = 0
        self.max = float('-inf')
        self.min = float('+inf')

    def add_value(self, x):
        self.n += 1
        self.sum += x
        self.sum2 += x*x
        self.max = max(self.max, x)
        self.min = min(self.min, x)

    def mean(self):
        if self.n == 0:
            return 0
        return self.sum / self.n

    def sigma(self):
        if self.n < 2:
            return 0
        mean = self.mean()
        sigma2 = (self.sum2 - 2*mean*self.sum + mean*mean*self.n) / (self.n - 1)
        if sigma2 < 0:  # numerical errors
            sigma2 = 0
        return sqrt(sigma2)

    def to_html(self):
        if self.n == 0:
            return '--'
        if self.sigma() < 1e-10:
            return str(self.mean())
        return (
            '<span title="{}..{}, {} items">'
            '{:.3f} &plusmn; <i>{:.3f}</i>'
            '</span>'.format(
                self.min, self.max, self.n, self.mean(), self.sigma()))
