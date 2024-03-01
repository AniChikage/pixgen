#!/bin/bash

# 设置监视 GPU 占用的阈值
threshold=14000

# 检查是否安装了 nvidia-smi
if ! command -v nvidia-smi &>/dev/null; then
    echo "Error: nvidia-smi is not installed. Please make sure NVIDIA drivers are installed."
    exit 1
fi

# 循环监视 GPU 占用情况
while true; do
    # 获取 GPU 占用情况
    gpu_usage=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)

    # 将 GPU 占用转换为 GB
    # gpu_usage_gb=$(echo "scale=2; $gpu_usage / 1024" | bc)
    gpu_usage_gb=$(echo "$gpu_usage / 1024" | awk '{printf "%.2f", $1}')
    gpu_usage_gb=result=$(awk -F'.' '{print $1}' <<< "$gpu_usage_gb")

    echo "GPU Memory Usage: $gpu_usage_gb GB"

    # 如果 GPU 占用大于阈值，则查找并关闭对应的程序
    if (( $(echo "$gpu_usage_gb > $threshold" | bc -l) )); then
        echo "GPU usage exceeds $threshold GB."
        echo "Searching for 'python app.py'..."

        # 查找并关闭名为 "python app.py" 的程序
        pids=$(pgrep -f "python app.py")

        if [ -n "$pids" ]; then
            echo "Found 'python app.py' running with PID: $pids"
            echo "Killing 'python app.py'..."
            kill -9 $pids
            echo "Restarting 'python app.py'..."
            # 在此处添加重新启动 "python app.py" 的命令
	    echo "Starting 'python app.py'..."
            bash -c "python app.py"
        else
            echo "No 'python app.py' process found."
        fi
    fi

    # 休眠一段时间后再次检查
    sleep 10
done

