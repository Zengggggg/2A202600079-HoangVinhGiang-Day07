import os

# import các chunker của bạn
from src.chunking import FixedSizeChunker, SentenceChunker, RecursiveChunker, CustomChunker, ChunkingStrategyComparator





def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()


def run_comparison(file_paths):
    comparator = ChunkingStrategyComparator()

    for path in file_paths:
        print("\n" + "=" * 60)
        print(f"📄 File: {os.path.basename(path)}")

        text = load_text(path)
        result = comparator.compare(text)

        print("\n📊 Results:")
        for strategy, stats in result.items():
            print(f"- {strategy}:")
            print(f"   + Chunks: {stats['count']}")
            print(f"   + Avg length: {stats['avg_length']:.2f}")


if __name__ == "__main__":
    # 👇 sửa đường dẫn theo project của bạn
    files = [
        "data_phase_2/shopee_chinh_sach_tra_hang_hoan_tien.md",
    ]

    run_comparison(files)