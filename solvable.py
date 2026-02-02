import json
from typing import Dict, Optional
from count_tokens import get_token_count

# 问题可解性判断系统提示词
SOLVABILITY_SYSTEM_PROMPT = """You are an expert in analyzing mathematical and logical problems. Your task is to determine whether a given question is solvable.

A question is considered **SOLVABLE** if:
1. It provides all necessary information and conditions
2. The problem is well-defined with clear objectives
3. It has a determinable answer (even if complex)
4. The constraints are consistent (not contradictory)

A question is considered **UNSOLVABLE** if:
1. Missing critical information or parameters
2. Contains contradictory conditions
3. The problem statement is ambiguous or unclear
4. Asks for information that cannot be determined from given data
5. The question is incomplete or truncated

**Important Guidelines:**
- Be strict but reasonable in your judgment
- Consider if a reasonable person could solve the problem with the given information
- For mathematical problems, check if all necessary values are provided
- For logical problems, verify if the premises are sufficient for the conclusion

Output format requirements:
- Return ONLY a valid JSON object
- Must have exactly these fields:
  - "solvable": boolean (true/false)
  - "confidence": number (0.0-1.0, your confidence in the judgment)
  - "reason": string (brief explanation in English, max 200 characters)
  - "missing_info": list of strings (what information is missing, empty list if solvable)

Example outputs:
{"solvable": true, "confidence": 0.95, "reason": "All necessary parameters provided, problem is well-defined", "missing_info": []}
{"solvable": false, "confidence": 0.85, "reason": "Missing the radius value needed to calculate circle area", "missing_info": ["radius"]}"""

SOLVABILITY_USER_PROMPT = """Analyze whether the following question is solvable:

{question}

Return the result as JSON with format: {{"solvable": true/false, "confidence": 0.0-1.0, "reason": "explanation", "missing_info": ["item1", "item2"]}}"""


def truncate_question_for_solvability(question: str, max_tokens: int = 4096) -> str:
    """
    为可解性判断截断问题文本
    
    Args:
        question: 原始问题
        max_tokens: 最大token数(默认4096,给判断留足够上下文)
    
    Returns:
        str: 截断后的问题
    """
    current_tokens = get_token_count(question)
    
    if current_tokens <= max_tokens:
        return question
    
    # 二分查找截断位置
    left, right = 0, len(question)
    result = question
    
    while left < right:
        mid = (left + right + 1) // 2
        truncated = question[:mid]
        tokens = get_token_count(truncated)
        
        if tokens <= max_tokens:
            result = truncated
            left = mid
        else:
            right = mid - 1
    
    # 添加截断标记
    if result != question:
        result += "\n\n... [Question truncated due to length]"
    
    return result


def parse_solvability_result(response_str: str) -> Dict:
    """
    解析并验证可解性判断结果
    
    Args:
        response_str: JSON响应字符串
    
    Returns:
        dict: 验证通过的结果字典
    
    Raises:
        ValueError: 验证失败时抛出异常
    """
    result = json.loads(response_str)
    
    # 验证必需字段
    required_fields = ["solvable", "confidence", "reason", "missing_info"]
    for field in required_fields:
        if field not in result:
            raise ValueError(f"Missing required field: {field}")
    
    # 验证字段类型
    if not isinstance(result["solvable"], bool):
        raise ValueError("'solvable' must be boolean")
    
    if not isinstance(result["confidence"], (int, float)):
        raise ValueError("'confidence' must be a number")
    
    if not isinstance(result["reason"], str):
        raise ValueError("'reason' must be a string")
    
    if not isinstance(result["missing_info"], list):
        raise ValueError("'missing_info' must be a list")
    
    # 验证confidence范围
    if not 0.0 <= result["confidence"] <= 1.0:
        raise ValueError("'confidence' must be between 0.0 and 1.0")
    
    # 验证reason长度
    if len(result["reason"]) > 300:
        result["reason"] = result["reason"][:297] + "..."
    
    # 确保missing_info中的元素都是字符串
    if not all(isinstance(item, str) for item in result["missing_info"]):
        raise ValueError("All items in 'missing_info' must be strings")
    
    return result


def check_question_solvability(question: str, 
                               max_retries: int = 3,
                               max_tokens: int = 4096,
                               verbose: bool = True) -> Dict:
    """
    判断单个问题是否可解
    
    Args:
        question: 要判断的问题
        max_retries: 最大重试次数(默认3次)
        max_tokens: 问题的最大token数(默认4096)
        verbose: 是否打印详细信息(默认True)
    
    Returns:
        dict: {
            "solvable": 是否可解(bool),
            "confidence": 置信度(0.0-1.0),
            "reason": 判断理由(str),
            "missing_info": 缺失的信息列表(list),
            "success": 判断是否成功完成(bool),
            "truncated": 问题是否被截断(bool),
            "original_length": 原始问题长度,
            "processed_length": 处理后问题长度
        }
    """
    if not question or not question.strip():
        return {
            "solvable": False,
            "confidence": 1.0,
            "reason": "Empty or invalid question",
            "missing_info": ["question content"],
            "success": True,
            "truncated": False,
            "original_length": 0,
            "processed_length": 0
        }
    
    original_length = len(question)
    
    # # 截断过长的问题
    # if verbose:
    #     print(f"\n📊 Analyzing question solvability...")
    #     print(f"   Original length: {original_length} characters")
    
    processed_question = truncate_question_for_solvability(question, max_tokens)
    processed_length = len(processed_question)
    truncated = (processed_length < original_length)
    
    # if truncated and verbose:
    #     print(f"✂️  Question truncated to {max_tokens} tokens")
    #     print(f"   Processed length: {processed_length} characters")
    
    # 构建消息
    messages = [
        {
            "role": "system",
            "content": SOLVABILITY_SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": SOLVABILITY_USER_PROMPT.format(question=processed_question)
        }
    ]
    
    
    from tools_api import json_api_call
    # 尝试获取有效结果
    last_error = None
    for retry in range(max_retries):
        try:
            # if verbose and retry > 0:
            #     print(f"   Retry {retry}/{max_retries}...")
            
            # 生成1个结果
            response_list = json_api_call(messages, n=1)
            
            if not response_list:
                last_error = "Empty response from API"
                continue
            
            # 解析和验证结果
            try:
                result = parse_solvability_result(response_list[0])
                
                # 添加额外信息
                result["success"] = True
                result["truncated"] = truncated
                result["original_length"] = original_length
                result["processed_length"] = processed_length
                
                # if verbose:
                #     print(f"✅ Analysis completed successfully")
                #     print(f"   Solvable: {result['solvable']}")
                #     print(f"   Confidence: {result['confidence']:.2f}")
                #     print(f"   Reason: {result['reason']}")
                #     if result['missing_info']:
                #         print(f"   Missing info: {', '.join(result['missing_info'])}")
                
                return result
                
            except (json.JSONDecodeError, ValueError, KeyError) as e:
                last_error = str(e)
                # if verbose:
                #     print(f"   ⚠️  Parse error: {e}")
                continue
            
        except Exception as e:
            last_error = str(e)
            # if verbose:
            #     print(f"   ⚠️  API error: {e}")
            continue
    
    # 如果所有重试都失败,返回默认结果
    if verbose:
        print(f"❌ Failed to analyze question after {max_retries} retries")
        print(f"   Last error: {last_error}")
    
    return {
        "solvable": None,  # 表示无法判断
        "confidence": 0.0,
        "reason": f"Failed to analyze: {last_error}",
        "missing_info": [],
        "success": False,
        "truncated": truncated,
        "original_length": original_length,
        "processed_length": processed_length
    }


def batch_check_solvability(questions: list[str], 
                           max_retries: int = 3,
                           max_tokens: int = 4096,
                           verbose: bool = True) -> list[Dict]:
    """
    批量判断多个问题的可解性
    
    Args:
        questions: 问题列表
        max_retries: 每个问题的最大重试次数
        max_tokens: 每个问题的最大token数
        verbose: 是否打印详细信息
    
    Returns:
        list: 每个问题的判断结果列表
    """
    results = []
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"Batch Solvability Check: {len(questions)} questions")
        print(f"{'='*60}")
    
    for idx, question in enumerate(questions):
        if verbose:
            print(f"\n--- Question {idx + 1}/{len(questions)} ---")
            preview = question[:100] + "..." if len(question) > 100 else question
            print(f"Preview: {preview}")
        
        result = check_question_solvability(
            question, 
            max_retries=max_retries,
            max_tokens=max_tokens,
            verbose=verbose
        )
        
        result["question_index"] = idx
        results.append(result)
    
    if verbose:
        print(f"\n{'='*60}")
        print("Batch Check Summary")
        print(f"{'='*60}")
        
        solvable_count = sum(1 for r in results if r["solvable"] is True)
        unsolvable_count = sum(1 for r in results if r["solvable"] is False)
        failed_count = sum(1 for r in results if r["solvable"] is None)
        
        print(f"✅ Solvable: {solvable_count}")
        print(f"❌ Unsolvable: {unsolvable_count}")
        print(f"⚠️  Failed to analyze: {failed_count}")
        
        avg_confidence = sum(r["confidence"] for r in results if r["success"]) / len(results) if results else 0
        print(f"📊 Average confidence: {avg_confidence:.2f}")
    
    return results


# 使用示例
if __name__ == "__main__":
    # 测试单个问题
    print("="*80)
    print("Test 1: Solvable Question")
    print("="*80)
    
    question1 = """
    A rectangle has a length of 10 cm and a width of 5 cm. 
    Calculate the area and perimeter of the rectangle.
    """
    
    result1 = check_question_solvability(question1, verbose=True)
    print("\n=== Result JSON ===")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    
    print("\n\n" + "="*80)
    print("Test 2: Unsolvable Question (Missing Information)")
    print("="*80)
    
    question2 = """
    Calculate the area of a circle.
    """
    
    result2 = check_question_solvability(question2, verbose=True)
    print("\n=== Result JSON ===")
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    
    print("\n\n" + "="*80)
    print("Test 3: Ambiguous Question")
    print("="*80)
    
    question3 = """
    A number is greater than 5. What is the number?
    """
    
    result3 = check_question_solvability(question3, verbose=True)
    print("\n=== Result JSON ===")
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    
    print("\n\n" + "="*80)
    print("Test 4: Batch Check")
    print("="*80)
    
    test_questions = [
        "What is 2 + 2?",
        "Solve for x: $$2x + 5 = 13$$",
        "Find the volume of a sphere.",  # 缺少半径
        "A triangle has sides of length 3, 4, and 5. Is it a right triangle?",
        "Calculate the derivative.",  # 缺少函数
        "If $$a^2 + b^2 = c^2$$ and $$a = 3$$, $$b = 4$$, find $$c$$.",
    ]
    
    batch_results = batch_check_solvability(test_questions, verbose=True)
    
    print("\n\n=== Detailed Batch Results ===")
    for idx, result in enumerate(batch_results):
        print(f"\nQuestion {idx + 1}:")
        print(f"  Preview: {test_questions[idx][:60]}...")
        print(f"  Solvable: {result['solvable']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Reason: {result['reason']}")
        if result['missing_info']:
            print(f"  Missing: {', '.join(result['missing_info'])}")
    
    
    print("\n\n" + "="*80)
    print("Test 5: Very Long Question (Truncation Test)")
    print("="*80)
    
    long_question = """
    Consider a complex mathematical problem involving multiple steps.
    """ + "This is additional context. " * 500 + """
    Now, calculate the final result.
    """
    
    result5 = check_question_solvability(long_question, max_tokens=2048, verbose=True)
    print("\n=== Result JSON ===")
    print(json.dumps(result5, indent=2, ensure_ascii=False))
