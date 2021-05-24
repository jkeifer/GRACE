from py_ggw.analyzer import (
    add_grace_data_opt,
    add_aoi_file_arg,
    add_grace_date_arg,
    add_outfile_arg,
    Analyzer,
)


class Singleton(object):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


class Command(Singleton):
    help=""

    def get(self, keyname, value=None):
        return getattr(self, keyname, value)

    def collect_args(self, subparser):
        pass

    def postprocess_args(self, parser, args):
        pass

    def __call__(self, args):
        raise NotImplementedError('Subclasses of {} must implement a __call__ method'.format(self.__class__))


class Map(Command):
    help="Create a map of a single GRACE monthly LWE dataset for an AOI"

    def collect_args(self, parser):
        add_grace_data_opt(parser)
        add_aoi_file_arg(parser)
        add_grace_date_arg(parser)
        add_outfile_arg(parser)

    def __call__(self, args):
        Analyzer(args.grace_data[0], args.grace_data[1], args.aoi).map_date(
            args.date,
            args.outfile,
        )


class Animate(Command):
    help="Animate maps of a GRACE monthly LWE datasets for an AOI"

    def collect_args(self, parser):
        add_grace_data_opt(parser)
        add_aoi_file_arg(parser)
        add_grace_date_arg(parser, name='start_date')
        add_grace_date_arg(parser, name='end_date')
        add_outfile_arg(parser)
        parser.add_argument(
            '--fps',
            help='Frames per second for output animation',
            type=int,
            default=10,
        )

    def __call__(self, args):
        Analyzer(args.grace_data[0], args.grace_data[1], args.aoi).animate(
            args.start_date,
            args.end_date,
            args.outfile,
            fps=args.fps,
        )


class Plot(Command):
    help="Plot GRACE monthly LWE dataset averages for an AOI"

    def collect_args(self, parser):
        add_grace_data_opt(parser)
        add_aoi_file_arg(parser)
        add_grace_date_arg(parser, name='start_date')
        add_grace_date_arg(parser, name='end_date')
        add_outfile_arg(parser)

    def __call__(self, args):
        Analyzer(args.grace_data[0], args.grace_data[1], args.aoi).plot(
            args.start_date,
            args.end_date,
            args.outfile,
        )
