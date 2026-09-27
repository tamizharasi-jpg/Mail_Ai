"""
MailMind Data Preparation Script
=================================
Downloads and prepares the UCI SMS Spam Collection for training and evaluation.

Dataset: SMS Spam Collection v.1
Source : https://archive.ics.uci.edu/dataset/228/sms+spam+collection
License: CC BY 4.0
Records: 5,574 SMS messages (4,827 ham, 747 spam)

Outputs
-------
data/processed/dataset.csv        – Cleaned full dataset
data/train/train.csv              – 70 % stratified training split
data/validation/validation.csv    – 15 % stratified validation split
data/test/test.csv                – 15 % stratified held-out test split
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pandas as pd
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
TRAIN_DIR = ROOT / "data" / "train"
VAL_DIR = ROOT / "data" / "validation"
TEST_DIR = ROOT / "data" / "test"

RANDOM_STATE = 42


def load_sms_spam_collection() -> pd.DataFrame:
    """Load the tab-separated SMS Spam Collection file."""
    filepath = RAW_DIR / "SMSSpamCollection"
    if not filepath.exists():
        print(f"ERROR: {filepath} not found. Run the download step first.")
        sys.exit(1)

    df = pd.read_csv(
        filepath,
        sep="\t",
        header=None,
        names=["label", "text"],
        encoding="latin-1",
    )
    print(f"Loaded {len(df):,} raw messages from {filepath.name}")
    return df


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Basic cleaning: drop nulls, duplicates, strip whitespace."""
    original_count = len(df)

    # Drop rows with missing text or label
    df = df.dropna(subset=["text", "label"])

    # Strip whitespace
    df["text"] = df["text"].str.strip()
    df["label"] = df["label"].str.strip().str.lower()

    # Drop exact duplicate messages (keep first)
    df = df.drop_duplicates(subset=["text"], keep="first")

    # Validate labels
    valid_labels = {"ham", "spam"}
    df = df[df["label"].isin(valid_labels)]

    # Reset index
    df = df.reset_index(drop=True)

    removed = original_count - len(df)
    print(f"Cleaned: {original_count:,} → {len(df):,} messages ({removed} removed)")
    print(f"  Duplicates removed: {removed}")
    return df


def add_metadata(df: pd.DataFrame) -> pd.DataFrame:
    """Add basic metadata columns useful for EDA."""
    df["text_length"] = df["text"].str.len()
    df["word_count"] = df["text"].str.split().str.len()
    df["has_url"] = df["text"].str.contains(r"https?://|www\.", case=False, regex=True).astype(int)
    df["has_phone"] = df["text"].str.contains(r"\+?\d[\d\s().-]{7,}\d", regex=True).astype(int)
    df["exclamation_count"] = df["text"].str.count("!")
    df["uppercase_ratio"] = df["text"].apply(lambda t: sum(c.isupper() for c in t) / max(len(t), 1))
    return df


def split_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Stratified 70/15/15 train/validation/test split."""
    train_df, temp_df = train_test_split(
        df, test_size=0.30, random_state=RANDOM_STATE, stratify=df["label"]
    )
    val_df, test_df = train_test_split(
        temp_df, test_size=0.50, random_state=RANDOM_STATE, stratify=temp_df["label"]
    )
    print(f"Split sizes — Train: {len(train_df):,}  Val: {len(val_df):,}  Test: {len(test_df):,}")
    for name, split in [("Train", train_df), ("Val", val_df), ("Test", test_df)]:
        dist = split["label"].value_counts()
        print(f"  {name}: ham={dist.get('ham', 0)}, spam={dist.get('spam', 0)} ({dist.get('spam', 0) / len(split) * 100:.1f}% spam)")
    return train_df, val_df, test_df


def save_splits(full_df: pd.DataFrame, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame) -> None:
    """Write CSV files to disk."""
    for directory in [PROCESSED_DIR, TRAIN_DIR, VAL_DIR, TEST_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    full_df.to_csv(PROCESSED_DIR / "dataset.csv", index=False)
    train_df.to_csv(TRAIN_DIR / "train.csv", index=False)
    val_df.to_csv(VAL_DIR / "validation.csv", index=False)
    test_df.to_csv(TEST_DIR / "test.csv", index=False)

    print(f"\nSaved to:")
    print(f"  {PROCESSED_DIR / 'dataset.csv'}")
    print(f"  {TRAIN_DIR / 'train.csv'}")
    print(f"  {VAL_DIR / 'validation.csv'}")
    print(f"  {TEST_DIR / 'test.csv'}")


def main() -> None:
    print("=" * 60)
    print("MailMind Dataset Preparation")
    print("=" * 60)

    df = load_sms_spam_collection()
    df = clean_dataset(df)
    df = add_metadata(df)

    print(f"\nDataset summary:")
    print(f"  Total messages: {len(df):,}")
    print(f"  Ham: {(df['label'] == 'ham').sum():,} ({(df['label'] == 'ham').mean() * 100:.1f}%)")
    print(f"  Spam: {(df['label'] == 'spam').sum():,} ({(df['label'] == 'spam').mean() * 100:.1f}%)")
    print(f"  Avg text length: {df['text_length'].mean():.0f} chars")
    print(f"  Avg word count: {df['word_count'].mean():.1f} words")

    train_df, val_df, test_df = split_dataset(df)
    save_splits(df, train_df, val_df, test_df)

    print("\nDataset preparation complete.")


if __name__ == "__main__":
    main()
