import argparse
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(description="Author-wise analysis of the Rokomari books dataset.")
    parser.add_argument("--input", default="cleaned_books_used.csv", help="Path to input CSV")
    parser.add_argument("--output", default="results", help="Folder for generated results")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(input_path)
    required = {"name", "author"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")

    df["name"] = df["name"].fillna("").astype(str).str.strip()
    df["author"] = df["author"].fillna("").astype(str).str.strip()
    df["author"] = df["author"].str.replace(r"\\s+", " ", regex=True).str.strip(" ,")
    df = df[(df["name"] != "") & (df["author"] != "") &
            (df["author"].str.lower() != "nan")]
    if "product_url" in df.columns:
        df = df.drop_duplicates(subset=["name", "author", "product_url"])
    else:
        df = df.drop_duplicates(subset=["name", "author"])

    counts = df.groupby("author").size().sort_values(ascending=False)
    result = pd.DataFrame({"author": counts.index, "book_count": counts.values})
    result["percentage_of_dataset"] = (result["book_count"] / len(df) * 100).round(2)
    result.to_csv(output_dir / "author_book_counts.csv", index=False, encoding="utf-8-sig")
    result.head(15).to_csv(output_dir / "top_15_authors.csv", index=False, encoding="utf-8-sig")
    result[result["book_count"] == result["book_count"].min()].to_csv(
        output_dir / "least_represented_authors.csv", index=False, encoding="utf-8-sig"
    )

    top = result.head(15).sort_values("book_count")
    plt.figure(figsize=(12, 7))
    plt.barh(top["author"], top["book_count"])
    plt.xlabel("Number of books")
    plt.ylabel("Author")
    plt.title("Top 15 Authors by Number of Books")
    plt.tight_layout()
    plt.savefig(output_dir / "top_15_authors.png", dpi=180)
    plt.close()

    distribution = result["book_count"].value_counts().sort_index()
    plt.figure(figsize=(10, 6))
    plt.bar(distribution.index, distribution.values)
    plt.xlabel("Number of books per author")
    plt.ylabel("Number of authors")
    plt.title("Distribution of Authors by Number of Books")
    plt.tight_layout()
    plt.savefig(output_dir / "author_distribution.png", dpi=180)
    plt.close()

    print(f"Books analyzed: {len(df)}")
    print(f"Unique authors: {len(result)}")
    print(f"Most represented author: {result.iloc[0]['author']} ({result.iloc[0]['book_count']} books)")
    print(f"Authors with one book: {(result['book_count'] == 1).sum()}")
    print(f"Results saved in: {output_dir.resolve()}")

if __name__ == "__main__":
    main()
