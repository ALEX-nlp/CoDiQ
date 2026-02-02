model_name=codiq
source_dir_name=Data
dest_dir_name=result
python codiq_pipeline.py \
    --model_name ${model_name} \
    --answer_key generated \
    --files_path ${source_dir_name}/\*.jsonl \
    --dest_dir_name ${dest_dir_name}
