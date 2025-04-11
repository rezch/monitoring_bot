from matplotlib.axes import Axes
import matplotlib.pyplot as plt


def make_basic_plot(x, y) -> Axes:
    plt.style.use('dark_background')

    _, ax = plt.subplots()
    ax.fill_between(x, y)

    return ax


def make_basic_scatter_with_outliers(x, y, pred = lambda y: y == 1) -> Axes:
    plt.style.use('dark_background')

    _, ax = plt.subplots()

    ok = []
    bad = []

    for x_, y_ in zip(x, y):
        if pred(y_):
            bad.append((x_, y_))
        else:
            ok.append((x_, y_))

    ax.scatter(
        [value[0] for value in ok],
        [value[1] for value in ok],
        c='cyan', marker='.')

    ax.scatter(
        [value[0] for value in bad],
        [value[1] for value in bad],
        c='red', marker='x')

    return ax
