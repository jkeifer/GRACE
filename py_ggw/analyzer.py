import os
import argparse
import numpy as np
import pandas as pd; pd.set_option('max_columns', 6)
import geopandas as gpd
import rioxarray
import xarray
import matplotlib.pyplot as plt
import tempfile
import imageio

from datetime import date
from pathlib import Path
from rasterio import features


# TODO: maybe some better way to handle this
# We're only doing this to stop the deluge of
# NotGeoreferencedWarning when we load data
import warnings
warnings.filterwarnings("ignore")


def aoi_file_arg(arg):
    ''' argparse type for aoi data'''
    try:
        return gpd.read_file(arg)
    except:
        raise argparse.ArgumentError(
            "Could not load AOI data from provided file: '{}'".format(arg),
        )


def grace_data_arg(arg):
    '''argparse type for grace data'''
    try:
        return Analyzer.grace_data_from_data_dir(arg)
    except:
        raise argparse.ArgumentError(
            "Could not load GRACE data from provided data directory: '{}'".format(arg),
        )


def grace_date_arg(arg):
    '''argparse type for a grace observation date'''
    try:
        try:
            return date.fromisoformat(arg)
        except ValueError:
            return date.fromisoformat(arg + '-01')
    except:
        raise argparse.ArgumentError(
            "Unable to coerce into valid date: '{}'".format(arg),
        )



def add_grace_data_opt(parser):
    parser.add_argument(
        '-d',
        '--data_dir',
        help='py_ggw data directory (as created by `update-data`)',
        type=grace_data_arg,
        default=grace_data_arg(Path(os.getcwd()).joinpath('data')),
        dest='grace_data',
    )


def add_aoi_file_arg(parser):
    parser.add_argument(
        'aoi',
        metavar='AOI',
        help='File containting the geometry of the Area Of Interest',
        type=aoi_file_arg,
    )


def add_grace_date_arg(parser, name='date'):
    parser.add_argument(
        name,
        help='GRACE dataset date in format YYYY-MM. '
             'The first observation found in the given month will be used.',
        type=grace_date_arg,
    )


def add_outfile_arg(parser):
    parser.add_argument(
        'outfile',
        help='Path at which to write output file.',
        type=Path,
    )


def grace_vrange(timeseries, mask=None):
    vmin=None
    vmax=None
    for t in timeseries:
        masked = t * mask if mask is not None else t
        vmax = max(masked.max(), vmax) if vmax is not None else masked.max()
        vmin = min(masked.min(), vmin) if vmin is not None else masked.min()
    return (vmin, vmax)


def grace_date_to_str(data_array):
    return data_array.time.to_dict()['data'].strftime('%Y-%m-%d')


def grace_plot_ds(data_array, aoi, mask=None, vmin=None, vmax=None):
    ax = aoi.geometry.boundary.plot(edgecolor='black')
    data = data_array * mask if mask is not None else data_array
    ax = data.plot(cmap='RdBu', vmin=vmin, vmax=vmax, ax=ax)
    mean_cm = data.mean()
    plt.title('GRACE LWE Thickness {}'.format(grace_date_to_str(data_array)))
    plt.figtext(
        .53,
        .03,
        'Mean LWE Thickness: {:.2f} cm'.format(float(mean_cm)),
        ha='center',
    )
    ax.colorbar.set_label('LWE Thickness [cm]')
    ax.figure.set_facecolor('white')
    ax.figure.set_size_inches(8,8)
    return ax


def grace_animate(timeseries, aoi, filename, fps, mask=None, vmin=None, vmax=None):
    with tempfile.TemporaryDirectory() as _dir:
        _dir = Path(_dir)
        imgs = []
        for index, ds in enumerate(timeseries):
            ax = grace_plot_ds(ds, aoi, mask=mask, vmin=vmin, vmax=vmax)
            f = str(_dir.joinpath(str(index) + '.png'))
            ax.figure.savefig(f, bbox_inches="tight", pad_inches=0.1)
            plt.close(ax.figure)
            # seems like we should be able to get the bytes from
            # the plot and load them into an imageio object without
            # using the temp storage, but we'll do this for now...
            imgs.append(imageio.imread(f))
        imageio.mimsave(filename, imgs, fps=9)


def _compare_dates(check_date, start_date, end_date=None):
    if end_date is not None:
        return (
            (start_date.year == check_date.year and start_date.month <= check_date.month)
            or (check_date.year == end_date.year and check_date.month <= end_date.month)
            or (start_date.year < check_date.year < end_date.year)
        )
    return check_date.year == start_date.year and check_date.month == start_date.month


def grace_filter_by_date(data_array, date, end_date=None):
    min_index = None
    max_index = None
    for index, time in enumerate(data_array.time):
        ds_date = time.to_dict()['data']
        if _compare_dates(ds_date, date, end_date=end_date):
            min_index = min(min_index, index) if min_index is not None else index
            max_index = max(max_index, index) if max_index is not None else index

    if min_index and max_index:
        return data_array[min_index:max_index+1]
    return []


def grace_open_file(path, array_index):
    # TODO: there's got to be a better way than passing in this array index
    arr = rioxarray.open_rasterio(path, decode_coords="all", parse_coordinates=True, decode_times=True, mask=True)
    return arr[array_index].rio.write_crs(4326)


def trend_line(x, y):
    n = len(x)
    sum_xy = 0
    sum_x = 0
    sum_x2 = 0
    sum_y = 0
    for x, y in zip(x, y):
        sum_xy += x * y
        sum_x += x
        sum_x2 += x ** 2
        sum_y += y

    m = (sum_xy - (sum_x * sum_y) / n) / (sum_x2 - (sum_x ** 2) / n)
    b = (sum_y / n) - m * (sum_x / n)

    return m, b


class Analyzer(object):
    DATA_FILE_PATH='grace/combined/GRCTellus.JPL.200204_202103.GLO.RL06M.MSCNv02CRI.nc.latlon'
    SF_FILE_PATH='grace/combined/CLM4.SCALE_FACTOR.JPL.MSCNv02CRI.nc.latlon'

    def __init__(self, grace_data, grace_sf, aoi):
        self.aoi = aoi
        self.grace = grace_data.lwe_thickness.rio.clip(self.aoi.geometry, all_touched=True)
        self.sf = grace_sf.rio.clip(self.aoi.geometry, all_touched=True)

        self.mask = features.rasterize(
            shapes=self.aoi.geometry,
            fill=np.nan,
            out_shape=self.grace[0].shape,
            transform=self.grace.rio.transform(),
        )

        self._vrange = None

    @property
    def vmin(self):
        if self._vrange is None:
            self._calc_vrange()
        return self._vrange[0]

    @property
    def vmax(self):
        if self._vrange is None:
            self._calc_vrange()
        return self._vrange[1]

    def _calc_vrange(self):
            self._vrange = grace_vrange(self.grace, mask=(self.sf * self.mask))

    @staticmethod
    def grace_data_from_data_dir(data_dir,
                                 data_file_path=DATA_FILE_PATH,
                                 sf_file_path=SF_FILE_PATH):
        data_dir = Path(data_dir)
        return (
            grace_open_file(data_dir.joinpath(data_file_path), 3),
            grace_open_file(data_dir.joinpath(sf_file_path), 0),
        )

    def map_date(self, date, savefile):
        try:
            ds = grace_filter_by_date(self.grace, date)[0]
        except IndexError:
            # TODO: better way to log messages
            print("Unable to find dataset with year/month '{}-{:02d}'".format(date.year, date.month))
            return

        ax = grace_plot_ds(
            ds,
            self.aoi,
            mask=(self.sf * self.mask),
            vmin=self.vmin,
            vmax=self.vmax,
        )
        ax.figure.savefig(savefile, bbox_inches="tight", pad_inches=0.1)
        print("Map written to '{}'".format(savefile))

    def animate(self, start_date, end_date, savefile, fps=10):
        ds = grace_filter_by_date(self.grace, start_date, end_date)
        if len(ds) == 0:
            print("Unable to find any datasets within range '{}-{:02d}' to '{}-{:02d}'".format(
                start_date.year,
                start_date.month,
                end_date.year,
                end_date.month,
            ))
            return

        grace_animate(
            ds,
            self.aoi,
            savefile,
            fps=fps,
            mask=(self.sf * self.mask),
            vmin=self.vmin,
            vmax=self.vmax,
        )
        print("Animation written to '{}'".format(savefile))

    def plot(self, start_date, end_date, savefile):
        _ds = grace_filter_by_date(self.grace, start_date, end_date)
        if len(_ds) == 0:
            print("Unable to find any datasets within range '{}-{:02d}' to '{}-{:02d}'".format(
                start_date.year,
                start_date.month,
                end_date.year,
                end_date.month,
            ))
            return

        average_grid = (_ds * self.mask * self.sf).mean(dim='time')

        dates = []
        means = []
        corrected = []
        for ds in _ds:
            dates.append(date.fromisoformat(grace_date_to_str(ds)))
            means.append(float((ds * self.mask * self.sf).mean().values))
            corrected.append(float(((ds * self.mask * self.sf) - average_grid).mean().values))

        df = pd.DataFrame(
            zip(dates, means, corrected),
            columns=('date', 'mean_lwe', 'corrected_mean_lwe'),
            index=dates,
        )

        slope, intercept = trend_line(range(len(corrected)), corrected)

        # change is trend last obs - firt obs
        change = (intercept + slope * len(corrected)) - (intercept + slope * 0)

        ax = df.plot(x='date', y='corrected_mean_lwe', figsize=(16, 4))
        ax.set_xlabel('Observation Date')
        ax.set_ylabel('LWE Thickness [cm]')
        ax.axhline(y=0, color='black', lw=1)
        ax.figure.set_facecolor('white')

        def trend_y(m, b, count):
            for x in range(count):
                yield m * x + b

        plt.plot(dates, list(trend_y(slope, intercept, len(corrected))), 'r', label='trend')
        plt.legend()
        plt.figtext(
            0.51,
            -0.04,
            'Total LWE thickness trend over time: {:.2f} cm'.format(change),
            ha='center',
        )

        ax.figure.savefig(savefile, bbox_inches="tight", pad_inches=0.1)
        print("Plot written to '{}'".format(savefile))


if __name__ == '__main__':
    pass
