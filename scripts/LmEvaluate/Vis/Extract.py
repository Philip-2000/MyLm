import json

def extract_method_and_accuracy(data, output_file="res.txt"):
    """
    提取方法名、基准测试名和准确率并写入txt文件
    
    Args:
        data: 输入的原始数据（列表/字典格式）
        output_file: 输出的txt文件路径
    """
    with open(output_file, "a", encoding="utf-8") as f:
        # 写入表头（新增benchmark列）
      
        
        
        # 遍历每个条目，提取核心信息
        for item in data:
            method = item.get("method", "未知模型")
            benchmark = item.get("benchmark", "未知基准")  # 新增提取benchmark
            accuracy = item.get("accuracy", 0.0)
            
            # 格式化写入（制表符分隔，三列对齐）
            f.write(f"{method}\t{benchmark}\t{accuracy:.6f}\n")
    
    print(f"已成功提取方法名、基准测试名和准确率，文件保存至：{output_file}")

# 方式2：从JSON文件读取数据并执行提取
with open("/mnt/data/yl/C/MyLm/MyLm/LmEvaluate/res/20251212_142521.json", "r", encoding="utf-8") as f:
    input_data = json.load(f)
extract_method_and_accuracy(input_data)