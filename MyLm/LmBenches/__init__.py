from .Benchmark import Benchmark
BENCH_BASE = "/mnt/data/raw_data/"

BENCH_CONFIGS = {
    "LongTimeScope": {
        "path": BENCH_BASE + "LongTimeScope",
        "loader": Benchmark.asLongTimeScope,
    },
    "LongVideoBench": {
        "path": BENCH_BASE + "LongVideoBench",
        "loader": Benchmark.asLongVideoBench,
    },
    "LVBench": {
        "path": BENCH_BASE + "LVBench",
        "loader": Benchmark.asLVBench,
    },
    "MLVU": {
        "path": BENCH_BASE + "MLVU",
        "loader": Benchmark.asMLVU,
    },
    "EgoSchema": {
        "path": BENCH_BASE + "egoschema",
        "loader": Benchmark.asegoschema,
    },
}
# "Video-MME": {
 #       "path": BENCH_BASE + "Video-MME",
  #      "loader": Benchmark.asVideo_MME,
  #  },