import concurrent.futures
from io import BytesIO
import matplotlib.pyplot as plt
from numpy import array
from matplotlib.ticker import MaxNLocator
from numpy import inf, histogram
from constants import LABELS, COLORS

def occurrence_curve(data, fig_title):
    """
    Function creates occurrence curve (for all labels) for particular issue.
    x axis: time edges, ['<1 hour', '1/2 day', '1 day',
                         '2 days', '1 week', '>1 week']
    y_axis: amount of issue (tool) occurrences in time edges.

    data:
        [{'days': 0.12064253472222221,
          'hours': 2.895420833333333,
          'id': label_id1,
          'minutes': 173.72525,
          'seconds': 10423.515},
         {'days': 0.12064253472222221,
          'hours': 2.895420833333333,
          'id': label_id2,
          'minutes': 173.72525,
          'seconds': 10423.515},
          ...,
         {'days': 0.12064253472222221,
          'hours': 2.895420833333333,
          'id': label_idN,
          'minutes': 173.72525,
          'seconds': 10423.515}]

    Args:
        data (list of dicts): data for occurrence curve;
        fig_title (str): occurrence curve title;

    Return:
        image (io.BytesIO obj): BytesIO obj with occurrence curve.
    """

    # Prepare data for occurrence curve.
    bins = [0, 1, 4, 10, 34, 120, inf] # bins edges, [hours]
    ticklabels = ['<1 hour', '1/2 day', '1 day',
                  '2 days', '1 week', '>1 week']
    color = [COLORS[val] for val in LABELS.values()]

    hist_data = {label:[] for label in LABELS.keys()}
    for row in data:
        hist_data[row['id']].append(row['hours'])
    hist_data = list(hist_data.values())

    # Create occurrence curve plot.
    fig_width, fig_height = 16., 9.
    nrows, ncols = 3, 3
    fig, axes = plt.subplots(figsize=(fig_width, fig_height),
                             nrows=nrows, ncols=ncols)

    legend = []
    for i, row in enumerate(hist_data):

        # Customize subplots: set title, grid and etc.
        ax_row, ax_col = (i//ncols, i%ncols)
        axes[ax_row, ax_col].yaxis.set_major_locator(MaxNLocator(integer=True))

        # Create barplot for each label.
        if row:
            hist, _ = histogram(row, bins)
            ax_bar = axes[ax_row, ax_col].bar(range(len(hist)), hist,
                                              width=0.8, align='center',
                                              label=list(LABELS.values())[i],
                                              color=color[i], tick_label=ticklabels)
            # Add numbers to bar plot.
            for x_coord, y_coord in enumerate(hist):

                if y_coord > 0:
                    axes[ax_row, ax_col].text(x_coord, y_coord,
                                              str(y_coord), color='black', fontsize=8)

            legend.append([ax_bar, list(LABELS.values())[i]])

    # Set figure title, add legend and save an image.
    axes[-1][-1].set_axis_off()
    if legend:
        axes[-1][-1].legend(array(legend, dtype='object')[:, 0], array(legend, dtype='object')[:, 1],
                            framealpha=0.5, loc="lower right",
                            bbox_transform=plt.gcf().transFigure)

    fig.suptitle(fig_title, fontsize=14, fontweight='bold')

    image = BytesIO()
    fig.savefig(image, bbox_inches='tight', format='png', dpi=70)
    plt.close()

    return image

if __name__ == '__main__':
    pass
