def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Language Model on Benchmarks")
    #python evaluate.py LongVideoBench gpt-4 --max_qa 10
    parser.add_argument("bench_path", type=str, help="Path to the benchmark data")
    parser.add_argument("model", type=str, help="Language model to evaluate")
    parser.add_argument("--load_qa", type=int, default=-1, help="Maximum number of QAs to load")
    parser.add_argument("--max_qa", type=int, default=-1, help="Maximum number of QAs to evaluate")
    parser.add_argument("--num_segments", type=int, default=64, help="Number of segments to evaluate")

    parser.add_argument("--do_run", action="store_true", help="Whether to perform the standard run")
    parser.add_argument("--do_strong_run", action="store_true", help="Whether to perform the strong run")
    parser.add_argument("--do_compare", action="store_true", help="Whether to perform the comparison step")
    return parser.parse_args()

if __name__ == "__main__":
    from MyLm import evaluate
    args = parse()
    evaluate(_b=args.bench_path, _m=args.model, max_qa=args.max_qa, num_segments=args.num_segments, load_qa=args.load_qa, do_run=args.do_run, do_strong_run=args.do_strong_run, do_compare=args.do_compare)