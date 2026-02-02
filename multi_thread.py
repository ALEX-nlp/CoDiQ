import os
import json

from threading import Lock
from pathlib import Path
from concurrent import futures
from loguru import logger
from traceback import format_exc
from glob import glob
from tqdm import tqdm

file_lock = Lock()

class ResourceManager:
    def __init__(self, free_resource):
        self.free_resource = free_resource
        self.lock = Lock()
    
    def request_resource(self):
        with self.lock:
            if not self.free_resource:
                return None
            return self.free_resource.pop(0)
    
    def release_resource(self, resource):
        with self.lock:
            self.free_resource.append(resource)

class DataProcessor:
    def __init__(self, source_path, dest_path="output", is_jsonl=True, answer_key="default", max_workers=8):
        self.source_path = source_path
        self.dest_path = dest_path
        self.is_jsonl = is_jsonl
        self.answer_key = answer_key
        self.max_workers = max_workers
        self.finished = False
        self.all_files = [source_path] if os.path.isfile(source_path) else [os.path.join(source_path, file) for file in os.listdir(source_path)]
        
    @staticmethod
    def read_json_file(source_file, is_jsonl=True):
        with open(source_file, "r", encoding="utf-8") as f:
            if is_jsonl:
                source_data = f.readlines()
                source_data = [json.loads(line) for line in source_data]
            else:
                source_data = json.load(f)
        return source_data

    @staticmethod
    def write_json_file(result, dest_file, is_jsonl=True):
        with open(dest_file, "w", encoding="utf-8") as f:
            if is_jsonl:
                for line in result:
                    f.write(json.dumps(line, ensure_ascii=False)+"\n")
            else:
                json.dump(result, f, ensure_ascii=False, indent=4)
                
    @staticmethod
    def sort_json_by_id(source_file, is_jsonl=True):
        source_data = DataProcessor.read_json_file(source_file, is_jsonl)
        source_data.sort(key=lambda x: x["id"])
        DataProcessor.write_json_file(source_data, source_file, is_jsonl)

    @staticmethod
    def get_all_files(directory):
        file_list = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_list.append(os.path.join(root, file))
        return file_list
    
    def process(self, input_info):
        return ""

    def start(self):
        for source_file in self.all_files:
            self.source_file = source_file
            self.dest_file = self.dest_path if ".json" in self.dest_path else os.path.join(self.dest_path, Path(source_file).name)
            os.makedirs(Path(self.dest_file).parent, exist_ok=True)
            self.multi_process()
            DataProcessor.sort_json_by_id(self.dest_file)
        self.finished = True

    def single_process(self, args_tuple):
        try:
            index, input_info = args_tuple
            input_info["id"] = index
            if isinstance(self.answer_key, list):
                ret = self.process(input_info)
                for answer_key, item in zip(self.answer_key, ret):
                    input_info[answer_key] = item
            else:
                input_info[self.answer_key] = self.process(input_info)
            with file_lock:
                with open(self.dest_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(input_info, ensure_ascii=False)+"\n")
            logger.info(f"processed: {index}")
        except:
            logger.error(format_exc())

    def multi_process(self):
        questions = DataProcessor.read_json_file(self.source_file, is_jsonl=self.is_jsonl)
        processed_indexs = set() 
        if os.path.exists(self.dest_file):
            prod_questions = DataProcessor.read_json_file(self.dest_file)
            processed_indexs = {line["id"] for line in prod_questions}
        unpro_indexs = set(range(len(questions))) - processed_indexs
        logger.info(f"待处理对话数：{len(unpro_indexs)}")
        indexed_input = [(unpro_index, questions[unpro_index]) for unpro_index in unpro_indexs]

        with futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.single_process, indexed_input)

if __name__ == "__main__":
    input_path = "input.json"
    
    from time import sleep, time
    start_time = time()
    dp = DataProcessor(source_path=input_path)
    dp.start()
    while not dp.finished:
        sleep(30)
    end_time = time()
    logger.info(f"all task processed in {end_time-start_time:.2f} seconds.")
    