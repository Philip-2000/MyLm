def parse():
    import argparse, datetime
    parser = argparse.ArgumentParser(description="Visualize LmEvaluate results")
    parser.add_argument("--start_time", type=str, default="-1", help="Start time for loading results")
    tomorrow_second = (datetime.datetime.now() + datetime.timedelta(days=1)).timestamp()
    parser.add_argument("--end_time", type=float, default=tomorrow_second, help="End time for loading results")
    parser.add_argument("--figname", type=str, default="vis.png", help="Output figure name")
    args = parser.parse_args()
    if args.start_time != -1:
        args.start_time = datetime.datetime.strptime(args.start_time, "%Y%m%d_%H%M%S")
    if args.end_time != tomorrow_second:
        args.end_time = datetime.datetime.strptime(args.end_time, "%Y%m%d_%H%M%S")
    if isinstance(args.start_time, datetime.datetime):
        args.start_time = args.start_time.timestamp()
    if isinstance(args.end_time, datetime.datetime):
        args.end_time = args.end_time.timestamp()
    return args

if __name__ == "__main__":
    args = parse()
    from MyLm import visualize
    visualize(args.start_time, args.end_time, args.figname)