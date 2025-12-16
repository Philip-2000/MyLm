import matplotlib.pyplot as plt
import numpy as np
import os

def parse_txt_data(txt_path):
    """
    解析txt文件中的模型-基准-准确率数据（修复行过滤逻辑）
    """
    # 存储解析后的数据
    methods = []          # 模型方法名列表（去重）
    benchmarks = []       # 基准测试名列表（去重）
    results_dict = {}     # 临时存储 {method: {benchmark: accuracy}}

    # 校验文件是否存在
    if not os.path.exists(txt_path):
        print(f"❌ 错误：文件 {txt_path} 不存在！")
        return None
    
    # 读取txt文件（强制UTF-8编码，兼容不同换行符）
    try:
        with open(txt_path, "r", encoding="utf-8", newline="") as f:
            lines = f.readlines()
            if len(lines) == 0:
                print(f"❌ 错误：文件 {txt_path} 为空！")
                return None
            
            # 逐行解析（只跳过空行，不过滤其他内容）
            for line_num, raw_line in enumerate(lines, 1):
                line = raw_line.strip()
                # 只跳过空行（核心修复：不再过滤包含"-"的行）
                if not line:
                    continue
                
                # 拆分每行数据（兼容制表符/多个空格/混合分隔）
                # 先替换制表符为空格，再按任意空格拆分
                line_clean = line.replace("\t", " ").strip()
                parts = []
                for p in line_clean.split(" "):
                    if p:  # 过滤空字符串（多个空格导致）
                        parts.append(p)
                
                # 校验拆分结果
                if len(parts) != 3:
                    print(f"⚠️  警告：第{line_num}行格式错误，跳过 → {raw_line.strip()}")
                    continue
                
                # 提取并转换数据
                try:
                    method = parts[0].strip()
                    benchmark = parts[1].strip()
                    accuracy = float(parts[2].strip())
                except ValueError:
                    print(f"⚠️  警告：第{line_num}行准确率不是数字，跳过 → {raw_line.strip()}")
                    continue

                # 去重收集方法名和基准名
                if method not in methods:
                    methods.append(method)
                if benchmark not in benchmarks:
                    benchmarks.append(benchmark)
                
                # 存储准确率
                if method not in results_dict:
                    results_dict[method] = {}
                results_dict[method][benchmark] = accuracy

        # 最终数据校验
        if len(methods) == 0:
            print("❌ 错误：未解析到任何模型数据！")
            print("   请检查文件格式是否为：模型名 基准名 准确率（空格/制表符分隔）")
            return None
        if len(benchmarks) == 0:
            print("❌ 错误：未解析到任何基准数据！")
            return None

        # 构建参考代码格式的results
        results = []
        for method in methods:
            method_scores = []
            for benchmark in benchmarks:
                score = results_dict[method].get(benchmark, 0.0)
                method_scores.append((score, 64))  # total默认64，不影响绘图
            results.append(method_scores)

        print(f"✅ 解析成功：{len(methods)}个模型，{len(benchmarks)}个基准")
        print(f"   模型列表：{', '.join(methods[:3])}...")
        print(f"   基准列表：{', '.join(benchmarks)}")

        return {
            "methods": methods,
            "benchmarks": benchmarks,
            "results": results
        }
    
    except Exception as e:
        print(f"❌ 读取文件出错：{str(e)}")
        return None

def plot(data, figname):
    """
    完全沿用参考代码的绘图逻辑
    """
    if not data:
        print("❌ 无有效数据可绘图！")
        return
    
    methods = data["methods"]
    benchmarks = data["benchmarks"]
    results = data["results"]

    # 核心绘图逻辑（和参考代码完全一致）
    x = np.arange(len(benchmarks))
    width = 0.8 / len(methods)

    fig, ax = plt.subplots(figsize=(12, 6))

    for i, method in enumerate(methods):
        scores = [results[i][j][0] if results[i][j][0] is not None else 0 for j in range(len(benchmarks))]
        ax.bar(x + i * width, scores, width, label=method)

    ax.set_xlabel('Benchmarks')
    ax.set_ylabel('Scores')
    ax.set_title('Method Performance on Benchmarks')
    ax.set_xticks(x + width * (len(methods) - 1) / 2)
    ax.set_xticklabels(benchmarks, rotation=45)
    ax.legend()

    plt.tight_layout()
    plt.savefig(figname, dpi=100, bbox_inches='tight')
    plt.close()
    print(f"✅ 图表已保存：{os.path.abspath(figname)}")

def visualize(txt_path, figname="method_performance.png"):
    """
    主函数：解析+绘图
    """
    data = parse_txt_data(txt_path)
    if data:
        plot(data, figname)
    else:
        print("❌ 可视化失败！")

# ==================== 执行入口 ====================
if __name__ == "__main__":
    # 替换为你的res.txt绝对路径（推荐用绝对路径避免路径问题）
    TXT_FILE_PATH = "/mnt/data/yl/C/MyLm/MyLm/LmEvaluate/res.txt"  # 请确认这个路径正确！
    
    # 执行可视化
    visualize(TXT_FILE_PATH)