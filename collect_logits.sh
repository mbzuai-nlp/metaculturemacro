#!/bin/bash

models=(
    "openai-community/gpt2"
    "google/gemma-2-2b-it"
    "google/gemma-2-9b-it"
    "CohereLabs/aya-expanse-8b"
    "EleutherAI/gpt-j-6b"
    "meta-llama/Llama-3.2-1B-Instruct"
    "meta-llama/Meta-Llama-3.1-8B-Instruct"
    "meta-llama/Llama-3.1-70B-Instruct"
)

declare -A batch_sizes
batch_sizes["EleutherAI/gpt-j-6b"]=1024
batch_sizes["openai-community/gpt2"]=8096
batch_sizes["meta-llama/Llama-3.2-1B-Instruct"]=4098
batch_sizes["meta-llama/Meta-Llama-3.1-8B-Instruct"]=512
batch_sizes["google/gemma-2-2b-it"]=512
batch_sizes["google/gemma-2-9b-it"]=128
batch_sizes["CohereLabs/aya-expanse-8b"]=128
batch_sizes["meta-llama/Llama-3.1-70B-Instruct"]=16


tasks=(
    "../data/languages_wvs.json languages_0"
    "../data/languages_wvs.json languages_1"
    "../data/languages_wvs.json languages_2"
    "../data/taste_atlas_convenience_0.json convenience_0"
    "../data/taste_atlas_convenience_2.json convenience_2"
    "../data/taste_atlas_convenience_3.json convenience_3"
    "../data/taste_atlas_familiarity_0.json familiarity_0"
    "../data/taste_atlas_familiarity_1.json familiarity_1"
    "../data/taste_atlas_familiarity_2.json familiarity_2"
    "../data/taste_atlas_health_1.json health_1"
    "../data/taste_atlas_health_2.json health_2"
    "../data/taste_atlas_health_4.json health_4"
    "../data/houses.json house_0"
    "../data/houses.json house_1"
    "../data/houses.json house_2"
    "../data/taste_atlas_convenience_0.json national_0"
    "../data/taste_atlas_convenience_0.json national_1"
    "../data/taste_atlas_convenience_0.json national_2"
    "../data/wiki_religions.json religions_0"
    "../data/wiki_religions.json religions_1"
    "../data/wiki_religions.json religions_2"
    "../data/wiki_currencies.json currency_0"
    "../data/wiki_currencies.json currency_1"
    "../data/wiki_currencies.json currency_2"
    "../data/country_holidays_timeanddate.json holidays_0"
    "../data/country_holidays_timeanddate.json holidays_1"
    "../data/country_holidays_timeanddate.json holidays_2"
    # Add more (in_path proxy_prompt) pairs as needed
)

# Specify which GPUs to use
GPUS=(0 1) # Edit this array to select GPUs



for model in "${models[@]}"
do
    batch_size=${batch_sizes[$model]}
    gpu_count=${#GPUS[@]}
    task_idx=0
    declare -A gpu_pids  # Track which PID is running on which GPU
    declare -A gpu_available  # Track which GPUs are available
    
    # Initialize all GPUs as available
    for i in "${!GPUS[@]}"; do
        gpu_available[$i]=1
    done
    
    echo "\n=============================="
    echo "Starting tasks for model: $model"
    echo "Batch size: $batch_size"
    echo "GPUs available: ${GPUS[*]}"
    echo "==============================\n"
    
    for task in "${tasks[@]}"
    do
        set -- $task
        in_path=$1
        proxy_prompt=$2
        
        # Wait for an available GPU
        while true; do
            # Check if any running tasks have finished and free up their GPUs
            for gpu_idx in "${!gpu_pids[@]}"; do
                pid=${gpu_pids[$gpu_idx]}
                if ! kill -0 $pid 2>/dev/null; then
                    # Process has finished, GPU is now available
                    echo "GPU ${GPUS[$gpu_idx]} is now available (PID $pid finished)"
                    gpu_available[$gpu_idx]=1
                    unset gpu_pids[$gpu_idx]
                fi
            done
            
            # Find an available GPU
            available_gpu_idx=""
            for i in "${!GPUS[@]}"; do
                if [[ ${gpu_available[$i]} -eq 1 ]]; then
                    available_gpu_idx=$i
                    break
                fi
            done
            
            if [[ -n "$available_gpu_idx" ]]; then
                # Found an available GPU, launch the task
                gpu_num=${GPUS[$available_gpu_idx]}
                gpu_available[$available_gpu_idx]=0
                
                echo "Launching task:"
                echo "  Model: $model"
                echo "  Batch size: $batch_size"
                echo "  Input path: $in_path"
                echo "  Proxy prompt: $proxy_prompt"
                echo "  GPU: $gpu_num"

                python collect_logits_vllm_v2.py \
                    --in_path "$in_path" \
                    --countries_path ../data/countries_all.json \
                    --out_path_prefix "../outputs/logits_v2/${model//\//_}_${proxy_prompt}" \
                    --model_name "$model" \
                    --batch_size "$batch_size" \
                    --proxy_prompt "$proxy_prompt" \
                    --gpu_num "$gpu_num" &

                gpu_pids[$available_gpu_idx]=$!
                ((task_idx++))
                break
            else
                # No GPUs available, wait a bit before checking again
                sleep 1
            fi
        done
    done
    
    # Wait for all remaining tasks to complete
    echo "Waiting for all remaining tasks for model $model to finish..."
    for gpu_idx in "${!gpu_pids[@]}"; do
        wait ${gpu_pids[$gpu_idx]}
    done
    echo "All tasks for model $model completed."
    
    # Clean up arrays for next model
    unset gpu_pids
    unset gpu_available
done