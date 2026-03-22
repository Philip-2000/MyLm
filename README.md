## 项目立意
本项目是Philip-2000同学在做EgoCL项目时，由于对多模态大语言模型部署框架vLLM的使用不熟悉，导致他从头写了一份非常简陋的多模态大模型的部署框架。这个框架在启动模型时基于transformers库，在部署本地服务时基于uvicorn库。同时，他将长视频问答的问答对数据结构和评测指标数据结构整合成了统一的对象，倒是在一定程度上简化了使用。虽然，这是他造的一个十分简陋的轮子，但是由于（1）他已经写完了，不需要他的队友去重新配置vllm（2）他一定程度上还是整合了Benchmark的数据结构的，使得使用相对便捷了，所以他还是把这个框架开源给队友用。

## 项目使用教程
### 模型启动
1. 启动tmux会话来运行模型服务
```bash
tmux new -s s
```
2. 那么在s会话中，首先去到
```bash
cd /path/to/MyLm/scripts/LmServe/LmServe/
```
3. 这个目录，同时启动对应环境
```bash
conda activate try
```
有时需要手动添加环境路径
```bash
export PATH="${CONDA_ROOT}/envs/try/bin:${PATH}"
```
4. 然后运行
```bash
python LmServe.py Qwen3-Embed-0.6B
```
或者相关命令已经打包成了该目录中的一个可执行sh文件了，只需要
```bash
./Qwen3_Embed_0_6B.sh
```
就可以启动Qwen3-32B模型的服务了。
支持的模型列表如附表一所示。

**参数量问题**
由于历史遗留原因，模型的参数量选项不是通过命令行参数传入的，而是在下面这个配置文件中设置的
```bash
path/to/MyLm/MyLm/LmServer/__init__.py
```
此文件中的BASE_CONFIG列表中，每个模型的参数量选项在par字段中设置，首项为默认选项。比如Qwen3-32B模型的参数量选项设置为
```bash
{"name":"Qwen3-32B","port":7001,"env":"try","par":"32B"} #["4B","8B","32B","30B-A3B", "14B", "1.7B"]
```
然后就需要在该行的注释中选择一项，填入前面的字段中，作为当前此模型的常用参数版本。后续在启动的时候，实际上启动的是这个版本。而无法通过命令行参数来指定其他版本了。如果需要切换版本，就需要修改这个配置文件了。

### 模型调用
如果模型服务已经在本机启动了的话，可以通过安装此MyLm库来调用模型。首先在MyLm目录下安装
```bash
pip install -e .
```
安装完成后，就可以在python中通过以下方式调用模型了，例如
```python
from MyLm import Call
response = Call("Qwen3-VL-8B-Instruct", {"content": [{"image": "path/to/image.jpg", "text": "请描述这张图"}]})
```

### 评测集合加载与评测过程
评测集合的加载主要在
```bash
/path/to/MyLm/scripts/LmBenches/Test/
```
中，而评测过程主要在
```bash
/path/to/MyLm/scripts/LmEvaluate/Evaluate/
```
中，评测过程原理也很直接，即**启动模型服务，评测集合加载，逐个条目调用该服务**。可以参考*fva.bash*文件中的写法
```bash
b=EgoSchema
# b=LongTimeScope
# b=LongVideoBench
# b=LVBench
# b=MLVU
# b=Video_MME
# b=EgoLifeQA
# b=EgoR1Bench
# b=XLeBench
# b=All


# m=Qwen3-VL-8B-Instruct
# m=Qwen2.5-VL-7B-Instruct
# m=LLaVA-Video-7B-Qwen2
# m=LLaVA-NeXT-Video-7B-hf #Out of Date
# m=llava-onevision-qwen2-7b-ov
# m=InternVideo2.5-Chat-8B
# m=InternVL3_5-8B
# m=LongVA-7B-DPO
# m=EgoGPT-7b-EgoIT-EgoLife
m=Qwen3.5-27B
# m=All

python $(dirname "${BASH_SOURCE[0]}")/evaluate.py $b $m --max_qa -1 --num_segments 64 --do_run --do_strong_run --do_compare # --load_qa 2 --N 64
```
我们支持的评测集合如附表二所示。参数含义与默认值如下
<div style="display:none">
parser.add_argument("bench_path", type=str, help="Path to the benchmark data")
    parser.add_argument("model", type=str, help="Language model to evaluate")
    parser.add_argument("--load_qa", type=int, default=-1, help="Maximum number of QAs to load")
    parser.add_argument("--max_qa", type=int, default=-1, help="Maximum number of QAs to evaluate")
    parser.add_argument("--num_segments", type=int, default=64, help="Number of segments to evaluate")

    parser.add_argument("--do_run", action="store_true", help="Whether to perform the standard run")
    parser.add_argument("--do_strong_run", action="store_true", help="Whether to perform the strong run")
    parser.add_argument("--do_compare", action="store_true", help="Whether to perform the comparison step")
</div>

| 参数 | 含义 | 默认值 |
| ---- | ---- | ---- |
| bench_path | 评测集合路径 | 必选参数 |
| model | 评测模型名称 | 必选参数 |
| --load_qa | 最大加载的QA数量 | -1（加载全部） |
| --max_qa | 最大评测的QA数量 | -1（评测全部） |
| --num_segments | 评测的视频帧数数量（均匀采样） | 64 |
| --do_run | 是否执行标准选择题流程 | False |
| --do_strong_run | 是否执行问答题流程 | False |
| --do_compare | 是否评测结果质量 | False |

评测结果会以JSON文件的形式存在
```bash
/path/to/MyLm/MyLm/LmEvaluate/res/
```
文件名为其时间戳。

## 项目进阶使用教程

### 模型副本
如果想要在同一台机器上运行多个同种模型，那么它们的服务的端口就会冲突。因此必须显式地指定模型副本使用不同的网络端口，同时也需要运行在不同的tmux会话中。在我们的系统中，这些副本以模型名称之后的“:a”、“:b”等等来区分的，例如
```bash
python LmServe.py Qwen3-Embed-0.6B:a
```
就会启动一个名为Qwen3-Embed-0.6B的模型的a副本了。不同副本的端口号相差10000，例如Qwen3-Embed-0.6B的默认端口是9003，那么a副本的端口就是9003，b副本的端口就是19003，以此类推。这个过程在上面提到的*__init__.py*文件中的BASE_CONFIG列表中是设置了的。

### 指定模型副本
使用*Call*函数调用模型时，如果想要指定模型副本的话，可以在模型名称后面加上冒号和副本标识，例如
```python
response = Call("Qwen3-Embed-0.6B:a", {"content": [{"image": "path/to/image.jpg", "text": "请描述这张图"}]})
```
如果不指定副本，或者该副本服务未启动的话，系统也会在已启动的同种模型的副本中选择一个来调用的。

<span style="font-size:1.2em; color:lightblue">附表一：项目支持的模型附表</span>  

<!--
BASE_CONFIG = [
    {"name": "Qwen3-32B",                   "port": 7001, "env": "try", "par":"32B"}, #["4B","8B","32B","30B-A3B", "1.7B", "14B"]
    {"name": "InternVideo2.5-Chat-8B",      "port": 8001, "env": "ivd", "par":"8B"}, #["8B"]
    {"name": "InternVL3_5-8B",              "port": 8002, "env": "try", "par":"38B-Instruct"}, #["1B","2B","4B","8B","38B","1B-Instruct","2B-Instruct","4B-Instruct","8B-Instruct","38B-Instruct"]
    {"name": "Qwen3-VL-8B-Instruct",        "port": 8003, "env": "try", "par":"8B-Instruct"}, #["4B-Instruct","8B-Instruct","32B-Instruct"]
    {"name": "Qwen2.5-VL-7B-Instruct",      "port": 8004, "env": "try", "par":"72B-Instruct"}, #["3B-Instruct","7B-Instruct","32B-Instruct","72B-Instruct"]
    {"name": "LLaVA-NeXT-Video-7B-hf",      "port": 8005, "env": "try", "par":"7B-hf"},
    {"name": "LLaVA-Video-7B-Qwen2",        "port": 8006, "env": "llava", "par":"72B"}, #["7B","72B"]
    {"name": "llava-onevision-qwen2-7b-ov", "port": 8007, "env": "llava", "par":"72b-ov-sft"}, #["0.5b-ov","7b-ov","72b-ov-sft"]
    {"name": "LongVA-7B-DPO",               "port": 8008, "env": "longva", "par":"7B-DPO"}, #["7B-DPO"]
    {"name": "EgoGPT-7b-EgoIT-EgoLife",     "port": 8009, "env": "egogpt", "par":"7b"}, #["7b"]
    {"name": "Qwen3.5-27B",                 "port": 8010, "env": "base", "par":"27B"}, #["4B, 27B, 122B-A10B-FP8"]
    {"name": "Qwen3_Embedding_0.6B",        "port": 9001, "env": "try", "par":"0.6B"}, #["0.6B", "4B", "8B"]
    {"name": "Qwen3-VL-Embedding-2B",       "port": 9002, "env": "try", "par":"8B"}, #["2B", "8B"]
    {"name": "Qwen3-Embed-0.6B",            "port": 9003, "env": "try", "par":"0.6B"}, #["0.6B", "4B", "8B"]
]
-->

| 模型名称 | 端口 | 环境 | 参数量选项（首项为默认选项） |
|----    | ---- | ---- | ---- |
| Qwen3-32B | 7001 | try | 32B, 30B-A3B, 14B, 1.7B |
| InternVideo2.5-Chat-8B | 8001 | ivd | 8B |
| InternVL3_5-8B | 8002 | try | 38B-Instruct |
| Qwen3-VL-8B-Instruct | 8003 | try | 8B-Instruct, 4B-Instruct, 32B-Instruct |
| Qwen2.5-VL-7B-Instruct | 8004 | try | 72B-Instruct, 3B-Instruct, 7B-Instruct, 32B-Instruct |
| LLaVA-NeXT-Video-7B-hf | 8005 | try | 7B-hf, 7B, 72B |
| LLaVA-Video-7B-Qwen2 | 8006 | llava | 72B, 7B |
| llava-onevision-qwen2-7b-ov | 8007 | llava | 72b-ov-sft, 7b-ov, 0.5b-ov |
| LongVA-7B-DPO | 8008 | longva | 7B-DPO |
| EgoGPT-7b-EgoIT-EgoLife | 8009 | egogpt | 7b |
| Qwen3.5-27B | 8010 | base | 27B, 4B, 122B-A10B-FP8 |
| Qwen3_Embedding_0.6B | 9001 | try | 0.6B, 4B, 8B |
| Qwen3-VL-Embedding-2B | 9002 | try | 8B, 2B |
| Qwen3-Embed-0.6B | 9003 | try | 0.6B, 4B, 8B |


<span style="font-size:1.2em; color:lightblue">附表二：项目支持的评测集合附表</span>

<!--
BENCH_CONFIGS = {
    "LongTimeScope": {
        "path": BENCH_BASE + "LongTimeScope",
        "loader": Benchmark.asLongTimeScope,
    },
    "LongVideoBench": {
        "path": BENCH_BASE + "LongVideoBench",
        "loader": Benchmark.asLongVideoBench,
    },
    "LVBench": {
        "path": BENCH_BASE + "LVBench",
        "loader": Benchmark.asLVBench,
    },
    "MLVU": {
        "path": BENCH_BASE + "MLVU",
        "loader": Benchmark.asMLVU,
    },
    "EgoSchema": {
        "path": BENCH_BASE + "egoschema",
        "loader": Benchmark.asEgoSchema,
    },
    "EgoLifeQA": {
        "path": BENCH_BASE + "EgoLife",
        "loader": Benchmark.asEgoLifeQA,
    },
    "EgoR1Bench": {
        "path": BENCH_BASE + "Ego-R1-bench",
        "loader": Benchmark.asEgoR1Bench,
    },
    "XLeBench": {
        "path": BENCH_BASE + "X-LeBench",
        "loader": Benchmark.asXLeBench,
    },
}

b=EgoSchema        # 500qa,500v
b=LongTimeScope    # 450qa,450v
b=LongVideoBench   #1202qa,618v
b=LVBench          #1549qa,103v
b=MLVU             #2592qa,1659v
b=Video_MME        #2700qa,900v
b=EgoLifeQA        #500qa, 1v
b=EgoR1Bench       #300qa, 6v
b=XLeBench         #1000qa, 100v

-->

| 评测集合名称 | 路径 | 题量（QA） | 视频数量（V） |
| ----    | ---- | ---- | ---- |
| LongTimeScope | BASE + "LongTimeScope" | 450 | 450 |
| LongVideoBench | BASE + "LongVideoBench" | 1202 | 618 |
| LVBench | BASE + "LVBench" | 1549 | 103 |
| MLVU | BASE + "MLVU" | 2592 | 1659 |
| Video_MME | BASE + "Video_MME" | 2700 | 900 |
| EgoSchema | BASE + "egoschema" | 500 | 500 |
| EgoLifeQA | BASE + "EgoLife" | 500 | 1 |
| EgoR1Bench | BASE + "Ego-R1-bench" | 300 | 6 |
| XLeBench | BASE + "X-LeBench" | - | - |


<span style="font-size:1.2em; color:lightblue">附录三：我的系统简化</span>

#### A. tmux相关
我一般使用增强版的tmux命令，其首先在~/.bashrc文件中设置
```bash
alias ta='tmux_attach_strong'
tmux_attach_strong(){
    local session_name="$1"   
    #check if such session exists, using tmux ls
    if tmux ls | grep -q "^${session_name}:"; then
        tmux attach-session -t "$session_name"
    else
        tmux new-session -s "$session_name"
    fi
}
```
这段代码的作用是当我输入ta s时，如果tmux中已经存在名为s的会话，就直接连接到这个会话；如果不存在，就新建一个名为s的会话并连接到它。这样就避免了每次都要先检查tmux会话是否存在了。将服务命名为“s”的目的首先其是server的首字母，其次是为了如此简短，方便输入。家人们的conda环境名、文件夹名、git分支名、tmux会话名等，最好都能保持简短且有规律，这样在命令行中切换和输入时就会非常方便。于是我们只需要
```bash
ta s
```
就可以进入到tmux会话s中了。当然类似地还可以设置
```bash
alias tn='tmux new-session -s'  #强制新建会话
alias tk='tmux kill-session -t' #强制关闭会话
alias tl='tmux list-sessions'   #列出所有会话
```
等等简化版。

#### B. Conda相关
Conda有的时候会犯病，激活一个环境的时候它可能没能成功地把pip的路径加入PATH环境中。这时候如果我们在这个环境中安装了某个包了，那么就会出现明明安装了包但是却提示没有安装的情况。这时候我们可以在~/.bashrc文件中设置
```bash
export PATH="${CONDA_ROOT}/envs/try/bin:${PATH}"
```
但是这个代码又比较长了，所以我一般会在~/.bashrc文件中设置一个更健壮的函数来自动激活环境并设置路径，如下
```bash
alias ca='conda activate'
alias cod='conda deactivate'
alias tca='tmux_conda_activate'
......
tmux_conda_activate() {
    #查看当前环境叫什么
    e=$(conda info --envs | grep -v '^#' | grep '*' | awk '{print $1}')
    if [ "$e" != "base" ]; then
        cod
    fi

    # 使用你已有的别名进行激活
    ca "$1"
    
    # 自动设置PATH路径，使用你已定义的CONDA_ROOT变量
    export PATH="${CONDA_ROOT}/envs/$1/bin:${PATH}"
    
    #echo "✅ 已激活环境: $1, 并更新PATH指向: ${CONDA_ROOT}/envs/$1/bin"
}
```
这段代码的功能包括（1）首先设置了常规的conda激活命令为ca，和常规的conda环境切换命令为cod（conda deactivate的简写）。（2）定义了一个新的函数tmux_conda_activate来自动激活环境并设置路径。这个函数首先会查看当前激活的环境是什么，如果不是base环境的话，就先切换回base环境。然后使用ca命令激活指定的环境。（3）最后这个函数会自动设置PATH路径，使用你已定义的CONDA_ROOT变量来指向新激活环境的bin目录。这样我们就可以直接
```bash
tca try
```
来激活try环境了，并且不需要担心路径问题了。

#### C. 路径相关
由于我的项目路径比较长，而且很常用，例如
```bash
/path/to/MyLm/scripts/LmServe/LmServe
/path/to/MyLm/scripts/LmEvaluate/Evaluate
```
我一般会在~/.bashrc文件中设置一些环境变量来简化路径，例如
```bash
export MyLm="/path/to/MyLm"
export CALL="$MyLm/scripts/LmServe/LmServe"
export EVAL="$MyLm/scripts/LmEvaluate/Evaluate"
```
这样只需要
```bash
cd $CALL
cd $EVAL
```
就可以进入到对应的目录中了。

C这一项还可以和B这一项联动，当我们需要启动命令的时候，我们其实是需要
```bash
cd $CALL && tca try
./Qwen3_Embed_0_6B.sh
```
来进入到CALL目录并且激活try环境的。我们也可以把前两条简化成一个命令，例如
```bash
alias fserv='for_serve'
for_serve(){
    cd $CALL
    tca try
}
```
这样我们就可以直接
```bash
fserv
./Qwen3_Embed_0_6B.sh
```
来进入到CALL目录并且激活try环境了。

甚至如果更加激进一些，可以利用tmux的send-keys命令来直接在tmux会话中发送命令来进入目录和激活环境，例如
```bash
alias tserv='tmux_serve'
tmux_serve(){
    tmux send-keys -t s "cd $CALL && tca try" C-m
    tmux send-keys -t s "./Qwen3_Embed_0_6B.sh" C-m
}
```
这样我们就可以直接在当前shell中
```bash
tserv
```
一个命令就可以在tmux会话s中进入到CALL目录并且激活try环境，并且启动Qwen3_Embed_0_6B模型的服务了。后续还可以用ta s命令进入到tmux会话s中查看服务的输出了。这个send-keys命令也为D中的和模型副本有关的便捷代码，奠定了理论基础。

#### D. 副本相关
例如，现在要启动abcd四个Qwen3-Embed-0.6B模型的副本，那么我们就需要新建四个tmux会话，然后在四个tmux会话中分别运行四条命令
```bash
CUDA_VISIBLE_DEVICES=0 ./Qwen3_Embed_0_6B.sh:a
CUDA_VISIBLE_DEVICES=1 ./Qwen3_Embed_0_6B.sh:b
CUDA_VISIBLE_DEVICES=2 ./Qwen3_Embed_0_6B.sh:c
CUDA_VISIBLE_DEVICES=3 ./Qwen3_Embed_0_6B.sh:d
```
这非常的麻烦。实际上可以通过构建如下的一个sh脚本来简化这个过程，例如
```bash
#!/bin/bash
model_script="./${1:-"Qwen3_Embed_0_6B"}.sh"
for i in {a..d}; do
    tmux send-keys -t s "fserv" C-m
    tmux send-keys -t s "CUDA_VISIBLE_DEVICES=$((i-a)) $model_script:$i" C-m
done
```
这样直接启动这个sh
```bash
./start_copies.sh InternVideo2.5-Chat-8B
```
就可以启动四个InternVideo2.5-Chat-8B模型的副本了。

<!-- 
<span style="font-size:1.2em; color:lightblue">附表四：被简化的命令附表</span>

| 简化版 | 完整版 | 说明 |
|----    | ---- | ---- |
| ta <session> |      |      | -->
