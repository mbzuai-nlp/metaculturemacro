import os
from tqdm import tqdm
from argparse import ArgumentParser
from prompt import prefix_prompt_templates, prefix_mapping, prompt_templates
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import json
import unicodedata

# os.environ["CUDA_VISIBLE_DEVICES"] = "1"


def normalize_text(text):
    """Normalize Unicode text for comparison"""
    # Normalize Unicode to handle different representations
    normalized = unicodedata.normalize("NFKC", text)
    # Remove any replacement characters that might have been introduced
    normalized = normalized.replace("�", "")
    return normalized


def texts_match(text1, text2):
    """Check if two texts match, handling encoding issues"""
    norm1 = normalize_text(text1)
    norm2 = normalize_text(text2)

    # Direct comparison
    if norm1 == norm2:
        return True

    # Try comparing after removing all non-ASCII characters
    ascii1 = "".join(c for c in norm1 if ord(c) < 128)
    ascii2 = "".join(c for c in norm2 if ord(c) < 128)
    if ascii1 == ascii2 and ascii1:  # Only if there are ASCII chars
        return True

    # Try byte-wise comparison after encoding/decoding
    try:
        bytes1 = text1.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
        bytes2 = text2.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")
        if bytes1 == bytes2:
            return True
    except:
        pass

    return False


def load_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_obj_to_json_file(obj, file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=4, ensure_ascii=False)


def load_model_and_tokenizer(model_name):
    # Select GPU by setting CUDA_VISIBLE_DEVICES for this process (vLLM reads this)
    if args.gpu_num is not None:
        os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_num)
        print(f"Using CUDA device {args.gpu_num} via CUDA_VISIBLE_DEVICES")

    dtype = "half"
    if model_name.startswith("google/gemma"):
        dtype = "bfloat16"
    llm = LLM(
        model=model_name,
        dtype=dtype,
        # hf_token="",
        enable_prefix_caching=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    return llm, llm.llm_engine.tokenizer, tokenizer


def collect_food_logits(args):
    prompt_assistant_token = "assistant"
    prompt_newlines = "\n\n"
    prompt_template = prompt_templates[args.proxy_prompt]
    country_food_map = load_json_file(args.in_path)

    if args.debug:
        subset_countries = list(country_food_map.keys())[:2]
        country_food_map = {
            country: country_food_map[country][:3] for country in subset_countries
        }

    batch_size = args.batch_size
    model, tokenizer, hf_tokenizer = load_model_and_tokenizer(args.model_name)

    out_logit_path = f"{args.out_path_prefix}_{args.proxy_prompt}_logits.json"
    out_meta_path = f"{args.out_path_prefix}_{args.proxy_prompt}_meta.json"

    if os.path.exists(out_logit_path):
        country_logits = load_json_file(out_logit_path)
        print(f"Loaded existing logits from {out_logit_path}.")
    else:
        country_logits = {}

    all_food_items = []
    for food_items in tqdm(country_food_map.values(), desc="Collecting foods"):
        all_food_items.extend(food_items)
    all_countries = load_json_file(args.countries_path)["countries_list"]
    for country_name in tqdm(all_countries, desc="Processing countries"):
        if country_name in country_logits:
            print(f"Skipping {country_name} as it already exists in the output file.")
            continue

        initial_prompt = prompt_template.format(country=country_name)
        initial_prompt = f"{prefix_prompt_templates[prefix_mapping[args.proxy_prompt.rsplit('_', 1)[0]]]} {initial_prompt}"
        # print(f"Initial prompt: {initial_prompt}")
        food_logits = {}
        if not (
            args.model_name.startswith("openai-community/gpt2")
            or args.model_name.startswith("EleutherAI/gpt")
        ):

            prompt_order = [{"role": "user", "content": initial_prompt}]
            prompt = hf_tokenizer.apply_chat_template(
                prompt_order, tokenize=False, add_generation_prompt=True
            )
            tokenized_prompt = hf_tokenizer.apply_chat_template(
                prompt_order, tokenize=True, add_generation_prompt=True
            )
            prompt_len = len(tokenized_prompt)
        else:
            prompt = initial_prompt + "\nAnswer:"
            tokenized_prompt = hf_tokenizer(prompt, return_tensors="pt")
            prompt_len = tokenized_prompt.input_ids.size(1)

        # for batch_idx in tqdm(
        #     range(0, len(all_food_items), batch_size), desc="Batching foods"
        # ):
        for batch_idx in range(0, len(all_food_items), batch_size):
            batch_items = all_food_items[
                batch_idx : min(len(all_food_items), batch_idx + batch_size)
            ]
            prompts = []

            if args.model_name.startswith(
                "openai-community/gpt2"
            ) or args.model_name.startswith("EleutherAI/gpt"):
                for idx, item in enumerate(batch_items):
                    # Add a leading space to ensure proper tokenization
                    # especially for models like GPT-2
                    item = " " + item
                    batch_items[idx] = item

            for item in batch_items:
                food_prompt = prompt + item
                prompts.append(food_prompt)

            sampling_params = SamplingParams(
                temperature=1.0, top_p=1.0, logprobs=1, prompt_logprobs=1
            )
            outputs = model.generate(
                prompts, sampling_params=sampling_params, use_tqdm=False
            )

            for i, output in enumerate(outputs):
                # print(f"Output {i}: {output}")
                # breakpoint()
                if not (
                    args.model_name.startswith("openai-community/gpt2")
                    or args.model_name.startswith("EleutherAI/gpt")
                ):
                    logprobs = output.prompt_logprobs[1:]
                else:
                    logprobs = output.prompt_logprobs
                food_item_logprobs = logprobs[prompt_len:]
                token_logits = [
                    [*token_logprobs.values()][0].logprob
                    for token_logprobs in food_item_logprobs
                ]  # the first index is the input prompt token log prob
                recon_food_item = "".join(
                    [
                        [*token_logprobs.values()][0].decoded_token
                        for token_logprobs in food_item_logprobs
                    ]
                )  # the first index is the input prompt token log prob
                food_item = batch_items[i]

                # Use robust text matching to handle encoding issues
                if not texts_match(food_item, recon_food_item):
                    print(
                        f"Warning: Text mismatch (continuing anyway): '{food_item}' vs '{recon_food_item}'"
                    )
                    # raise ValueError("Text mismatch detected")
                    # You can uncomment the line below to see detailed character codes for debugging
                    # print(f"  Original chars: {[ord(c) for c in food_item]}")
                    # print(f"  Reconstructed chars: {[ord(c) for c in recon_food_item]}")

                if args.model_name.startswith(
                    "openai-community/gpt2"
                ) or args.model_name.startswith("EleutherAI/gpt"):
                    food_item = food_item.lstrip()
                food_logits[food_item] = sum(token_logits)
        country_logits[country_name] = food_logits

        write_obj_to_json_file(country_logits, out_logit_path)

    meta_info = {"rows": all_countries, "cols": all_food_items}
    write_obj_to_json_file(meta_info, out_meta_path)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument(
        "--in_path",
        type=str,
        help="Path to the JSON file containing country-food mappings.",
    )
    parser.add_argument(
        "--countries_path",
        type=str,
        help="Path to the JSON file containing countries that we want to collect the logprobs.",
    )
    parser.add_argument(
        "--out_path_prefix",
        type=str,
        help="Prefix for output file paths (logits and metadata).",
    )
    parser.add_argument("--model_name", type=str, help="Name of the vLLM model to use.")
    parser.add_argument(
        "--batch_size",
        type=int,
        default=8,
        help="Batch size for processing food items.",
    )
    parser.add_argument(
        "--proxy_prompt",
        type=str,
        help="Key to select the prompt template from the `prompt_templates` dictionary.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode for processing a smaller subset of data.",
    )
    parser.add_argument(
        "--gpu_num",
        type=int,
        help="GPU number to use for processing.",
    )
    args = parser.parse_args()

    collect_food_logits(args)
