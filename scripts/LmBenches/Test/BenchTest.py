def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark Load Parser")
    #python BenchLoad.py LongVideoBench
    parser.add_argument("path", type=str, help="Path to the benchmark data")
    parser.add_argument("model", type=str, help="Language model to use for testing")
    parser.add_argument("--max_qa", type=int, default=-1, help="Maximum number of QAs to test")
    parser.add_argument("--key", type=str, nargs='*', default=None, help="Specific QA keys to test")
    return parser.parse_args()

if __name__ == "__main__":
    arg = parse()
    from MyLm import Benchmark
    B = Benchmark.asAuto(arg.path)
    print(f"Loaded benchmark: {B.name}, len={len(B.QAs)} QAs, {len(B.Videos)} videos")
    B.run(model=arg.model, max_qa=arg.max_qa, key=arg.key, num_segments=64)