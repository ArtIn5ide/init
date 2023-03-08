
from io import BytesIO
import matplotlib.pyplot as plt
from .constants import LABELS, COLORS, UPTIME_LABELS, DOWNTIME_LABELS
from .indexes import total_labels_time

def pie(data, fig_title, general=False):
    """
    Create pie chart of the data.
    data:
        {label_id1: summary_time1,
         label_id2: summary_time2,
         label_id3: summary_time3,
         ...,
         label_idN: summary_timeN}

    Args:
        data (dict): data for pie chart;
        fig_title (str): pie chart title;
        general (bool): if True, pie charts represent total Downtime and uptime.

    Return:
        image (BytesIO obj): BytesIO obj with pie chart.
    """

    # Prepare pie chart data.
    if not general:
        times = [data[iid] for iid in LABELS.keys()]
        pct = [100.*t/sum(times) if sum(times) > 0. else 0. for t in times]

        titles = [f"{val}, {pct[i]:.2f}%" for i, val in enumerate(LABELS.values())]

        colors = list(COLORS.values())
    else:
        uptime_ids = []
        downtime_ids = []
        for k, v in LABELS.items():
            if v in UPTIME_LABELS:
                uptime_ids.append(k)
            elif v in DOWNTIME_LABELS:
                downtime_ids.append(k)
        
        times = [total_labels_time(data, select) for select in [uptime_ids, downtime_ids]]
        pct = [100.*t/sum(times) if sum(times) > 0. else 0. for t in times]
        titles = [f"{val}, {pct[i]:.2f}%" for i, val in enumerate(['Uptime', 'Downtime'])]
        colors = [COLORS['Up'], COLORS['Down']]


    # Plot and customize pie chart.
    fig, axis = plt.subplots(figsize=(6., 6.),
                             subplot_kw=dict(aspect="equal"))
    pie_chart = axis.pie(pct,
                         colors=colors, startangle=-90)

    # Add legend and title to pie chart.
    axis.legend(pie_chart[0], titles,
                framealpha=0.5, loc="upper right",
                bbox_transform=plt.gcf().transFigure)

    axis.set_title(fig_title, weight="bold")

    # Save image to StringIO object.
    image = BytesIO()
    fig.savefig(image, bbox_inches='tight', format='png', dpi=70)
    plt.close()

    return image

if __name__ == '__main__':
    pass
