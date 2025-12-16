def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Evaluate Language Model on Benchmarks")
    #python evaluate.py LongVideoBench gpt-4 --max_qa 10
    parser.add_argument("bench_path", type=str, help="Path to the benchmark data")
    parser.add_argument("model", type=str, help="Language model to evaluate")
    parser.add_argument("--max_qa", type=int, default=-1, help="Maximum number of QAs to evaluate")
    return parser.parse_args()

if __name__ == "__main__":
    from MyLm import evaluate
    #arg = parse()
    evaluate()
