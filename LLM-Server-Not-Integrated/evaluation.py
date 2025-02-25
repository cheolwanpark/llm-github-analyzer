import json
import nltk
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
from rouge_score import rouge_scorer

#  Initialize smoothing function for BLEU
smooth_fn = SmoothingFunction().method1

###  Compute BLEU Score
def compute_bleu_score(reference_summary, generated_summary):
    reference_tokens = [reference_summary.split()]
    generated_tokens = generated_summary.split()
    return sentence_bleu(reference_tokens, generated_tokens, smoothing_function=smooth_fn)

###  Compute ROUGE Score
def compute_rouge_score(reference_summary, generated_summary):
    scorer = rouge_scorer.RougeScorer(["rouge1", "rouge2", "rougeL"], use_stemmer=True)
    scores = scorer.score(reference_summary, generated_summary)
    return {
        "rouge-1": scores["rouge1"].fmeasure,
        "rouge-2": scores["rouge2"].fmeasure,
        "rouge-L": scores["rougeL"].fmeasure,
    }

###  Read File Content
def read_file(filepath):
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read().strip()

###  Compare Two AI Models
def compare_ai_models(reference_file, native_file):
    """
    Evaluates the native AI vs. fine-tuned AI using BLEU and ROUGE scores.
    """
    reference_summary = read_file(reference_file)
    native_ai_summary = read_file(native_file)

    # ✅ Compute scores for Native AI
    native_bleu = compute_bleu_score(reference_summary, native_ai_summary)
    native_rouge = compute_rouge_score(reference_summary, native_ai_summary)

    return {
        "BLEU": native_bleu,
        "ROUGE": native_rouge
    }

###  Evaluate All Cases
if __name__ == "__main__":
    # Define file paths
    file_pairs = [
        ("Easy_repository_analysis.txt", "Easy_repository_analysis_Native.txt"),
        ("Medium_repository_analysis.txt", "Medium_repository_analysis_Native.txt"),
        ("Hard_repository_analysis.txt", "Hard_repository_analysis_Native.txt"),
    ]

    results = {}

    for ref_file, native_file in file_pairs:
        result = compare_ai_models(ref_file, native_file)
        results[ref_file] = result

    # Print and save results
    print("Evaluation Results:\n", json.dumps(results, indent=4))

    with open("evaluation_results.txt", "w", encoding="utf-8") as f:
        f.write("Evaluation Results:\n")
        f.write(json.dumps(results, indent=4))
    
    print("✅ Evaluation saved to `evaluation_results.txt`")
