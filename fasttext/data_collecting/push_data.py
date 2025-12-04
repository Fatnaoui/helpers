from datasets import Dataset, DatasetDict, ClassLabel, Features, Value
from pathlib import Path
from sklearn.model_selection import train_test_split  
import random

# -------- CONFIG --------
labels = ["en", "fr", "it", "es","ar_msa", "ar_ma", "ar_ma_latin", "other"]
DATA_DIR = Path("data_waveA")
DATA_PATH = Path("en/en_data.txt")

HF_REPO_ID = "Fatnaoui/en-wiki-clean" 
SEED = 42
# ------------------------


def load_sentences(path: Path):
    sentences = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            sentences.append(line)
    return sentences


def push(label):
    # 1) Load sentences
    sentences = load_sentences(DATA_PATH)
    print("Total sentences loaded:", len(sentences))

    # 2) Create labels (for now, all 'en')
    labels = [label] * len(sentences)

    # 3) Shuffle once to mix things
    combined = list(zip(sentences, labels))
    random.Random(SEED).shuffle(combined)
    sentences, labels = zip(*combined)

    # 4) Split into train / val / test (80 / 10 / 10)
    # First split: train+val vs test
    sent_train_val, sent_test, lab_train_val, lab_test = train_test_split(
        sentences, labels, test_size=0.1, random_state=SEED, stratify=labels
    )
    # Second split: train vs val
    sent_train, sent_val, lab_train, lab_val = train_test_split(
        sent_train_val, lab_train_val, test_size=0.1111,  
        random_state=SEED, stratify=lab_train_val
    )

    print("Train:", len(sent_train), "Val:", len(sent_val), "Test:", len(sent_test))

    # 5) Define label names (for later multi-language, we already plan all labels)
    label_names = [
        "en",
        "fr",
        "es",
        "it",
        "ar_msa",
        "ar_ma",
        "ar_ma_latn",
        "other",
    ]

    features = Features({
        "text": Value("string"),
        "label": ClassLabel(names=label_names),
    })

    # 6) Build Dataset objects
    train_ds = Dataset.from_dict({"text": list(sent_train), "label": list(lab_train)}).cast(features)
    val_ds   = Dataset.from_dict({"text": list(sent_val),   "label": list(lab_val)}).cast(features)
    test_ds  = Dataset.from_dict({"text": list(sent_test),  "label": list(lab_test)}).cast(features)

    dataset = DatasetDict({
        "train": train_ds,
        "validation": val_ds,
        "test": test_ds,
    })

    print(dataset)
    print("Sample:", dataset["train"][0])

    # 7) Push to Hugging Face Hub
    dataset.push_to_hub(HF_REPO_ID)
    print(f"Pushed to HF: https://huggingface.co/datasets/{HF_REPO_ID}")

