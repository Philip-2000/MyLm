def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Visualize LmEvaluate results")
    parser.add_argument("--start_time", type=float, default=-1, help="Start time for loading results")
    parser.add_argument("--end_time", type=float, default=-1, help="End time for loading results")
    parser.add_argument("--figname", type=str, default="vis.png", help="Output figure name")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse()
    from MyLm import visualize
    visualize(args.start_time, args.end_time, args.figname)