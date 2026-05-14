# MEASURING META-CULTURAL COMPETENCY: A SPECTRAL FRAMEWORK FOR LLM KNOWLEDGE STRUCTURES

This repository is the official implementation of "MEASURING META-CULTURAL COMPETENCY: A SPECTRAL FRAMEWORK FOR LLM KNOWLEDGE STRUCTURES"

## Requirements

```setup
pip install -r requirements.txt
```

## Logprob Collection

Setup required config in `collect_logits.sh` and run using the below command to collect logprobs from specified models on the defined tasks.:

```bash
bash collect_logits.sh
```

Please note that each task is structured as "input file path" and "task name" pairs. The input file contains the set of cultural items. 

#### Configurable parameters:
- `models`: List of model names/paths from HuggingFace to evaluate.
- `batch_sizes`: Dictionary mapping model names to batch sizes for evaluation.
- `tasks`: List of tasks to evaluate on.
- `data_dir`: Directory containing the dataset files.
- `output_dir`: Directory to save the output logits.

This script will generate logprob files in the specified output directory for each model and task combination.

## Analysis and Visualization

Please refer to `Analysis-Notebook.ipynb` for detailed analysis and visualizations of the collected logprobs.

### Synthetic ER/SR Regime Visualization

To visualize the 4 ER/SR regimes on synthetic data refer to the `Synthetic-ER-SR-Visualization.ipynb` notebook.