import argparse
import re

from multi_thread import *
from time import sleep, time
from prompt import *
from count_tokens import get_messages_token_count
from rank_diff import sort_questions_by_difficulty
from solvable import check_question_solvability
from time import sleep

def remove_question_number(text):
    """去除开头的题目序号"""
    # 匹配: 以数字开头 + 点号 + 可选空格
    pattern = r'^\d+\.\s*'
    return re.sub(pattern, '', text)

parser = argparse.ArgumentParser(description='处理输入参数')

parser.add_argument('--model_name', 
                        type=str,
                        required=True,
                        help='Name of the model to use')
    
parser.add_argument('--answer_key',
                    type=str,
                    required=True,
                    help='Key for storing model answers')

parser.add_argument('--files_path',
                    type=str,
                    required=True,
                    help='Path to the input files')

parser.add_argument('--dest_dir_name',
                    type=str,
                    required=True,
                    help='Directory name for output')

args = parser.parse_args()

model_name = args.model_name
max_workers = 1
final_difficulty = 3
max_round = 10

MAX_RETRY = 5

if model_name == "codiq":
    from codiq_api import *
    max_workers = 2

class FileProcessor(DataProcessor):
    def get_cot_answer(self, ret):
        if "<think>" not in ret or "</think>" not in ret:
            return "", ret
        else:
            cot = ret.split("<think>")[-1].split("</think>")[0].strip()
            answer = ret.split("</think>")[-1].strip()
            return cot, answer
    
    def process_messages(self, messages):
        new_messages = []
        for msg in messages:
            if msg["role"] == "assistant":
                cot, answer = self.get_cot_answer(msg["content"])
                new_messages.append({"role": "assistant", "content": answer})
            else:
                new_messages.append(msg)
        return new_messages

    def get_round_tts(self, question, max_round, easy_to_hard_prompt):
        result = []
        all_questions = [question]  # 存储所有问题用于难度比较
        last_solvable_hard_question = None  # 存储最后一个可解难题
        fail_log = None  # 新增：记录失败日志

        messages = [{"role": "user", "content": easy_to_hard_prompt + easy_to_hard_2.format(original_problem=question)}]
        cot_token = get_messages_token_count(messages)

        append_msg = {"role": "user", "content": "Can you make it more difficult?"}
        append_msg_token = get_messages_token_count([append_msg])

        for round_idx in range(max_round):
            # 初始化变量，避免未定义错误
            is_success = False
            ret = None
            cot = ""
            current_question = ""
            
            # 尝试生成问题
            for retry_count in range(MAX_RETRY):
                try:
                    ret = api_call(self.process_messages(messages))[-1]
                    cot, answer = self.get_cot_answer(ret)
                    current_question = answer
                    is_success = True
                    break
                except Exception as e:
                    logger.warning(f"API call failed (attempt {retry_count + 1}/{MAX_RETRY}): {e}")
                    sleep(1)
                    continue
            
            # 如果生成失败，记录并退出
            if not is_success:
                fail_log = {
                    "round": round_idx + 1,
                    "reason": "generation_failed",
                    "detail": {
                        "message": f"Failed to generate question after {MAX_RETRY} retries",
                        "last_error": str(e) if 'e' in locals() else "Unknown error",
                        "retry_count": MAX_RETRY
                    }
                }
                logger.error(f"Failed to generate question at round {round_idx + 1} after {MAX_RETRY} retries")
                break

            ret_msg = {"role": "assistant", "content": ret}
            messages.append(ret_msg)
            cot_token += get_messages_token_count([ret_msg])

            # 将当前问题加入列表
            all_questions.append(current_question)
            
            # 1. 先判断可解性（轻量级操作）
            solvable_info = check_question_solvability(current_question)
            is_solvable = solvable_info.get("solvable", False)
            
            # 2. 再进行难度排序（重量级操作）
            compare_info = sort_questions_by_difficulty(all_questions)
            
            # 当前问题在all_questions中的索引
            current_idx = len(all_questions) - 1
            
            # 判断当前问题是否在最难的分组中
            is_in_hardest_group = False
            should_stop = False
            stop_reason = None
            
            if compare_info.get("success", False) and compare_info.get("result"):
                difficulty_groups = compare_info["result"]
                hardest_group = difficulty_groups[-1]  # 最后一个分组是最难的
                is_in_hardest_group = current_idx in hardest_group
                
                # 如果不在最难分组,停止
                if not is_in_hardest_group:
                    should_stop = True
                    stop_reason = "difficulty_decreased"
                    logger.info(f"Stopping at round {round_idx + 1}: Not in hardest group")
            
            # 如果可解且在最难分组,更新最后一个可解难题
            if is_solvable and is_in_hardest_group:
                last_solvable_hard_question = {
                    "round": round_idx + 1,
                    "question": current_question,
                    "cot": cot,
                    "token_used": cot_token,
                    "compare_info": compare_info,
                    "solvable_info": solvable_info
                }

            # 记录当前轮次的结果
            result.append(
                {
                    "id": len(result) + 1,
                    "cot": cot,
                    "answer": current_question,
                    "token_used": cot_token,
                    "compare_info": compare_info,
                    "solvable_info": solvable_info,
                    "is_in_hardest_group": is_in_hardest_group,
                    "all_questions_count": len(all_questions)
                }
            )

            # 检查停止条件并记录失败日志
            if not is_solvable:
                fail_log = {
                    "round": round_idx + 1,
                    "reason": "unsolvable",
                    "detail": {
                        "solvable": solvable_info.get("solvable", False),
                        "confidence": solvable_info.get("confidence", "N/A"),
                        "reason": solvable_info.get("reason", "N/A"),
                        "full_solvable_info": solvable_info
                    }
                }
                logger.info(f"Stopping at round {round_idx + 1}: Question is not solvable")
                break
                
            if should_stop:
                fail_log = {
                    "round": round_idx + 1,
                    "reason": "difficulty_decreased",
                    "detail": {
                        "current_question_index": current_idx,
                        "hardest_group_indices": difficulty_groups[-1] if compare_info.get("success") else [],
                        "all_difficulty_groups": compare_info.get("result", []),
                        "difficulty_rank_info": compare_info.get("difficulty_info", {}),
                        "full_compare_info": compare_info
                    }
                }
                break

            messages.append(append_msg)
            cot_token += append_msg_token

        return result, last_solvable_hard_question, fail_log
    
    def process(self, input_info):
        easy_to_hard_upgrade_data, last_solvable_hard_question, fail_log = self.get_round_tts(
            question=input_info["question"], 
            max_round=8, 
            easy_to_hard_prompt=easy_to_hard_upgrade_1
        )

        result = {
            "easy_to_hard_upgrade_data": easy_to_hard_upgrade_data,
            "last_solvable_hard_question": last_solvable_hard_question,
        }
        
        # 只有在有失败日志时才添加该字段
        if fail_log is not None:
            result["fail_log"] = fail_log
        
        return result

def infer_by_files(source_file, dest_file):
    os.makedirs(Path(dest_file).parent, exist_ok=True)
    start_time = time()
    dp = FileProcessor(source_path=source_file, dest_path=dest_file, answer_key=args.answer_key, max_workers=max_workers)
    dp.start()
    while not dp.finished:
        sleep(3)
    end_time = time()
    logger.info(f"all task processed in {end_time-start_time:.2f} seconds.")

if __name__ == "__main__":

    all_files = glob(args.files_path)
    dest_dir_name = args.dest_dir_name

    print(all_files)

    for source_file in all_files:
        dest_file = os.path.join(f"{dest_dir_name}/", Path(source_file).name)
        infer_by_files(source_file, dest_file)