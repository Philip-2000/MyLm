def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Language Model on Benchmarks")
    #python evaluate.py LongVideoBench gpt-4 --max_qa 10
    parser.add_argument("bench_path", type=str, help="Path to the benchmark data")
    parser.add_argument("model", type=str, help="Language model to evaluate")
    parser.add_argument("--max_qa", type=int, default=-1, help="Maximum number of QAs to evaluate")
    parser.add_argument("--num_segments", type=int, default=64, help="Number of segments to evaluate")
    return parser.parse_args()

if __name__ == "__main__":
    from MyLm import evaluate
    args = parse()
    evaluate(_b=args.bench_path, _m=args.model, max_qa=args.max_qa, num_segments=args.num_segments)