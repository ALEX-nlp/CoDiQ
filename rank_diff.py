import json
import random
from typing import List, Dict, Tuple
from count_tokens import get_token_count

# 难度分组排序系统提示词
DIFFICULTY_SORTING_SYSTEM_PROMPT = """You are an expert in assessing question difficulty. Evaluate questions based on:

1. Knowledge Complexity: Number and depth of concepts required
2. Cognitive Load: Reasoning levels and abstract thinking needed
3. Computational Complexity: Steps and calculations involved
4. Traps and Common Mistakes: Hidden pitfalls in the question
5. Integration Skills: Cross-domain knowledge application required

Your task is to group questions by difficulty level and sort groups from easiest to hardest.

**Important:** Questions with the SAME difficulty level should be grouped together.

Analyze each question carefully and return them grouped by difficulty level.

Output format requirements:
- Return ONLY a valid JSON object
- The JSON must have a "result" field containing a list of lists (groups)
- Each inner list contains question indices of the SAME difficulty level
- Groups should be ordered from easiest to hardest
- Use 0-based indexing matching the input order

Example output format:
{"result": [[1, 3], [0], [2, 4]]}

This means: 
- Questions 1 and 3 are easiest (same difficulty)
- Question 0 is medium difficulty
- Questions 2 and 4 are hardest (same difficulty)"""

DIFFICULTY_SORTING_USER_PROMPT = """Please group the following questions by difficulty level and sort groups from easiest to hardest:

{questions}

Return the result as JSON with format: {{"result": [[indices of easiest group], [indices of next group], ...]}}"""


def truncate_text_by_tokens(text: str, max_tokens: int = 2048) -> str:
    """
    按token数量截断文本
    
    Args:
        text: 原始文本
        max_tokens: 最大token数(默认2048)
    
    Returns:
        str: 截断后的文本
    """
    # 获取当前token数
    current_tokens = get_token_count(text)
    
    # 如果不超过限制,直接返回
    if current_tokens <= max_tokens:
        return text
    
    # 二分查找截断位置
    left, right = 0, len(text)
    result = text
    
    while left < right:
        mid = (left + right + 1) // 2
        truncated = text[:mid]
        tokens = get_token_count(truncated)
        
        if tokens <= max_tokens:
            result = truncated
            left = mid
        else:
            right = mid - 1
    
    # 添加截断标记
    if result != text:
        result += "... [truncated due to length]"
    
    return result


def preprocess_questions(questions: List[str], max_tokens: int = 2048) -> Tuple[List[str], List[bool]]:
    """
    预处理问题列表,对超长问题进行截断
    
    Args:
        questions: 原始问题列表
        max_tokens: 每个问题的最大token数(默认2048)
    
    Returns:
        tuple: (处理后的问题列表, 是否被截断的标记列表)
    """
    processed_questions = []
    truncated_flags = []
    
    for question in questions:
        original_tokens = get_token_count(question)
        
        if original_tokens > max_tokens:
            truncated_question = truncate_text_by_tokens(question, max_tokens)
            processed_questions.append(truncated_question)
            truncated_flags.append(True)
            print(f"⚠️  Question truncated: {original_tokens} tokens → ~{max_tokens} tokens")
        else:
            processed_questions.append(question)
            truncated_flags.append(False)
    
    return processed_questions, truncated_flags


def shuffle_questions(questions: List[str], seed: int = None) -> Tuple[List[str], List[int]]:
    """
    打乱问题顺序
    
    Args:
        questions: 原始问题列表
        seed: 随机种子(用于可复现性)
    
    Returns:
        tuple: (打乱后的问题列表, 原始索引映射)
        例如: 如果原始顺序是[Q0, Q1, Q2], 打乱后是[Q2, Q0, Q1]
             则返回 ([Q2, Q0, Q1], [2, 0, 1])
             其中映射[2, 0, 1]表示: 打乱后位置0的问题原本在位置2
    """
    if seed is not None:
        random.seed(seed)
    
    n = len(questions)
    indices = list(range(n))
    random.shuffle(indices)
    
    shuffled_questions = [questions[i] for i in indices]
    
    return shuffled_questions, indices


def map_back_to_original(shuffled_result: List[List[int]], 
                         shuffle_mapping: List[int]) -> List[List[int]]:
    """
    将打乱后的结果映射回原始索引
    
    Args:
        shuffled_result: 基于打乱顺序的分组结果
        shuffle_mapping: 打乱时的索引映射
    
    Returns:
        list: 映射回原始索引的分组结果
    
    Example:
        原始问题: [Q0, Q1, Q2, Q3]
        打乱后: [Q2, Q0, Q3, Q1], mapping=[2, 0, 3, 1]
        打乱后的分组: [[0, 1], [2], [3]]
        含义: 打乱后位置0,1是简单题, 位置2是中等题, 位置3是难题
        
        映射回原始索引:
        - 打乱后位置0对应原始位置2 (Q2)
        - 打乱后位置1对应原始位置0 (Q0)
        - 打乱后位置2对应原始位置3 (Q3)
        - 打乱后位置3对应原始位置1 (Q1)
        
        结果: [[2, 0], [3], [1]]
        含义: 原始Q2和Q0是简单题, Q3是中等题, Q1是难题
    """
    mapped_result = []
    
    for group in shuffled_result:
        mapped_group = [shuffle_mapping[shuffled_idx] for shuffled_idx in group]
        mapped_result.append(mapped_group)
    
    return mapped_result


def format_questions_for_prompt(questions: List[str]) -> str:
    """格式化问题列表为提示词"""
    formatted = []
    for idx, question in enumerate(questions):
        formatted.append(f"[Question {idx}]\n{question}")
    return "\n\n".join(formatted)


def parse_and_validate_result(response_str: str, n_questions: int) -> List[List[int]]:
    """
    解析并验证分组排序结果
    
    Args:
        response_str: JSON响应字符串
        n_questions: 问题数量
    
    Returns:
        list: 验证通过的分组索引列表
    
    Raises:
        ValueError: 验证失败时抛出异常
    """
    result = json.loads(response_str)
    
    # 验证结果格式
    if "result" not in result:
        raise ValueError("Response missing 'result' field")
    
    if not isinstance(result["result"], list):
        raise ValueError("'result' field must be a list")
    
    groups = result["result"]
    
    # 验证每个分组都是列表
    if not all(isinstance(group, list) for group in groups):
        raise ValueError("Each group must be a list")
    
    # 验证分组不为空
    if not groups or any(len(group) == 0 for group in groups):
        raise ValueError("Groups cannot be empty")
    
    # 收集所有索引
    all_indices = []
    for group in groups:
        all_indices.extend(group)
    
    # 验证索引完整性和唯一性
    if len(all_indices) != n_questions:
        raise ValueError(f"Expected {n_questions} total indices, got {len(all_indices)}")
    
    if set(all_indices) != set(range(n_questions)):
        raise ValueError("Invalid or duplicate indices in result")
    
    return groups


def sort_questions_by_difficulty(questions: List[str], 
                                max_retries: int = 3,
                                shuffle: bool = True,
                                shuffle_seed: int = None,
                                max_tokens_per_question: int = 2048) -> Dict:
    """
    对问题按难度进行分组排序
    
    Args:
        questions: 问题列表
        max_retries: 最大重试次数(默认3次)
        shuffle: 是否打乱问题顺序以减少位置偏见(默认True)
        shuffle_seed: 打乱的随机种子(用于可复现性)
        max_tokens_per_question: 每个问题的最大token数(默认2048)
    
    Returns:
        dict: {
            "result": 分组排序结果(按难度从易到难的分组索引列表, 基于原始索引),
            "success": 是否成功,
            "shuffled": 是否进行了打乱,
            "truncated_count": 被截断的问题数量
        }
    """
    if len(questions) == 0:
        return {
            "result": [],
            "success": True,
            "shuffled": False,
            "truncated_count": 0
        }
    
    if len(questions) == 1:
        # 即使只有一个问题也需要检查是否需要截断
        processed_questions, truncated_flags = preprocess_questions(
            questions, max_tokens_per_question
        )
        return {
            "result": [[0]],
            "success": True,
            "shuffled": False,
            "truncated_count": sum(truncated_flags)
        }
    
    # 预处理问题(截断超长问题)
    print(f"\n📊 Preprocessing {len(questions)} questions...")
    processed_questions, truncated_flags = preprocess_questions(
        questions, max_tokens_per_question
    )
    truncated_count = sum(truncated_flags)
    
    if truncated_count > 0:
        print(f"✂️  {truncated_count} question(s) truncated to {max_tokens_per_question} tokens")
    
    n_questions = len(processed_questions)
    
    # 打乱问题顺序
    if shuffle:
        shuffled_questions, shuffle_mapping = shuffle_questions(processed_questions, shuffle_seed)
    else:
        shuffled_questions = processed_questions
        shuffle_mapping = list(range(n_questions))
    
    # 构建消息
    messages = [
        {
            "role": "system",
            "content": DIFFICULTY_SORTING_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": DIFFICULTY_SORTING_USER_PROMPT.format(
                questions=format_questions_for_prompt(shuffled_questions)
            )
        }
    ]
    
    from tools_api import json_api_call
    
    # 尝试获取有效结果
    for _ in range(max_retries):
        try:
            # 生成1个结果
            response_list = json_api_call(messages, n=1)
            
            if not response_list:
                continue
            
            # 解析和验证结果
            try:
                shuffled_groups = parse_and_validate_result(response_list[0], n_questions)
                
                # 映射回原始索引
                if shuffle:
                    original_groups = map_back_to_original(shuffled_groups, shuffle_mapping)
                else:
                    original_groups = shuffled_groups
                
                return {
                    "result": original_groups,
                    "success": True,
                    "shuffled": shuffle,
                    "truncated_count": truncated_count
                }
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                continue
            
        except Exception as e:
            pass
    
    # 如果没有获得有效结果,返回默认顺序(每个问题单独一组)
    print("⚠️  Warning: No valid result obtained, returning default order")
    return {
        "result": [[i] for i in range(n_questions)],
        "success": False,
        "shuffled": shuffle,
        "truncated_count": truncated_count
    }


def get_sorted_questions(questions: List[str], sorting_result: Dict) -> List[Dict]:
    """
    根据排序结果获取按难度分组排序的问题列表
    
    Args:
        questions: 原始问题列表
        sorting_result: sort_questions_by_difficulty的返回结果
    
    Returns:
        list: 按难度分组的问题信息列表
    """
    groups = sorting_result["result"]
    n_groups = len(groups)
    
    sorted_questions = []
    
    for group_idx, group in enumerate(groups):
        # 确定难度等级
        if n_groups == 1:
            difficulty_level = "Medium"
        else:
            # 按比例划分难度等级
            ratio = group_idx / (n_groups - 1)
            if ratio < 0.33:
                difficulty_level = "Easy"
            elif ratio < 0.67:
                difficulty_level = "Medium"
            else:
                difficulty_level = "Hard"
        
        for original_idx in group:
            sorted_questions.append({
                "difficulty_group": group_idx + 1,
                "original_index": original_idx,
                "question": questions[original_idx],
                "difficulty_level": difficulty_level
            })
    
    return sorted_questions


def print_grouped_questions(questions: List[str], sorting_result: Dict):
    """
    按分组打印问题
    
    Args:
        questions: 原始问题列表
        sorting_result: sort_questions_by_difficulty的返回结果
    """
    groups = sorting_result["result"]
    n_groups = len(groups)
    
    for group_idx, group in enumerate(groups):
        # 确定难度等级标签
        if n_groups == 1:
            difficulty_label = "Medium"
        else:
            ratio = group_idx / (n_groups - 1)
            if ratio < 0.33:
                difficulty_label = "Easy"
            elif ratio < 0.67:
                difficulty_label = "Medium"
            else:
                difficulty_label = "Hard"
        
        print(f"\n{'='*60}")
        print(f"Difficulty Group {group_idx + 1} ({difficulty_label})")
        print(f"{'='*60}")
        
        for original_idx in group:
            print(f"\n[Question {original_idx}]")
            question_text = questions[original_idx]
            # 限制显示长度
            if len(question_text) > 500:
                print(f"{question_text[:500]}... [truncated for display]")
            else:
                print(f"{question_text}")


# 使用示例
if __name__ == "__main__":
    questions = [
        "What is 5 + 3?",
        "Prove that for all real numbers a, b, c, if $$a^2 + b^2 = c^2$$ and the triangle is inscribed in a semicircle, then the angle opposite to side c is a right angle.",
        "Calculate the perimeter of a square with side length 6 cm.",
        "Solve the equation: $$2x + 5 = 13$$",
        "What is 7 - 2?",
        "Find the derivative of $$f(x) = x^3 + 2x^2 - 5x + 1$$",
        # 添加一个超长问题用于测试截断功能
        "This is a very long question. " + "Lorem ipsum dolor sit amet, consectetur adipiscing elit. " * 100
    ]
    
    # 执行排序(带打乱和截断功能, 最多重试3次)
    print("=== Sorting Questions by Difficulty (with Shuffling and Token Truncation) ===\n")
    result = sort_questions_by_difficulty(
        questions, 
        max_retries=3,
        shuffle=True,  # 启用打乱
        shuffle_seed=42,  # 固定种子以便复现
        max_tokens_per_question=2048  # 每个问题最多2048 tokens
    )
    
    print("\n=== Sorting Result ===")
    print(f"Success: {result['success']}")
    print(f"Shuffled: {result['shuffled']}")
    print(f"Truncated: {result['truncated_count']} question(s)")
    print(f"Grouped indices (easiest to hardest): {result['result']}")
    
    # 打印分组的问题
    print("\n=== Questions Grouped by Difficulty (Easiest to Hardest) ===")
    print_grouped_questions(questions, result)
    
    # 获取详细信息
    print("\n\n=== Detailed Question Information ===")
    sorted_questions = get_sorted_questions(questions, result)
    
    for item in sorted_questions:
        print(f"\nGroup {item['difficulty_group']} | "
              f"Question {item['original_index']} | "
              f"{item['difficulty_level']}")
        question_preview = item['question'][:100] + "..." if len(item['question']) > 100 else item['question']
        print(f"   {question_preview}")
    
    # 输出JSON格式
    print("\n\n=== JSON Output ===")
    output = {
        "result": result["result"],
        "success": result["success"],
        "shuffled": result["shuffled"],
        "truncated_count": result["truncated_count"]
    }
    print(json.dumps(output, indent=2, ensure_ascii=False))
    
    # 验证映射正确性
    print("\n\n=== Verification ===")
    print("Checking that all original indices are present:")
    all_indices = []
    for group in result["result"]:
        all_indices.extend(group)
    all_indices.sort()
    print(f"Expected: {list(range(len(questions)))}")
    print(f"Got: {all_indices}")
    print(f"Match: {all_indices == list(range(len(questions)))}")