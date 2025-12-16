def parse():
    import argparse
    parser = argparse.ArgumentParser(description="Benchmark Transfer to Experience and Execution")
    parser.add_argument("path", type=str, help="Path to the benchmark data")
    return parser.parse_args()

if __name__ == "__main__":
    arg = parse()
    from MyLm import Benchmark
    B = Benchmark.asAuto(arg.path)
    print(f"Loaded benchmark: {B.name}, len={len(B.QAs)} QAs, {len(B.Videos)} videos")
    B.save_ee()