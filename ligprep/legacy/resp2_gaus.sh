#!/bin/bash

# Function to display help information
show_help() {
  echo "Usage: $0 [options]"
  echo "Options:"
  echo "  -h, --help           Show help information."
  echo "  -i, --input_path     Specify the input path (file, directory, or wildcard pattern)."
  echo "  -r, --run            Submit the sbatch job after creating the sbatch file."
  exit 0
}

# Initialize variables
INPUT_PATH=""
SUBMIT_JOB=false
# 定义 Gaussian 计算的根工作目录
BASE_WORK_DIR="/home/zhutao/scratch/workdir/ligprep/gauscalc"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -h|--help)
      show_help
      ;;
    -i|--input_path)
      INPUT_PATH="$2"
      shift # past argument
      shift # past value
      ;;
    -r|--run)
      SUBMIT_JOB=true
      shift # past argument
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      ;;
  esac
done

# Check if input path is provided
if [ -z "$INPUT_PATH" ]; then
  echo "Error: --input_path is required."
  show_help
fi

# Function to create and submit a SLURM job for each file
# Args: $1 = file path, $2 = group directory name
submit_job() {
  local file="$1"
  local group_name="$2"
  local filename=$(basename "$file")
  local prefix="${filename%%.*}"
  
  # 1. 定义基础目标路径
  local base_path="${BASE_WORK_DIR}/${group_name}/${prefix}"
  local output_dir="$base_path"
  
  # 2. [自动编号逻辑] 检查目录是否存在，如果存在则添加后缀 _2, _3 ...
  local counter=2
  while [ -d "$output_dir" ]; do
      output_dir="${base_path}_${counter}"
      ((counter++))
  done

  # 3. 创建确定的唯一目录
  mkdir -p "$output_dir"
  
  # 获取最终的目录名（可能带有 _2, _3），用于 Job Name
  local final_dirname=$(basename "$output_dir")

  # Copy the file to the output directory (保持文件名不变)
  cp "$file" "$output_dir"

  # 4. 定义 Job 标识符 (使用 final_dirname 确保 Job Name 唯一)
  # 后缀使用 _gaus 以区别 ORCA 任务
  local job_identifier="${final_dirname}_${group_name}_gaus"

  # Create a SLURM job script for this file
  cat <<EOF > "$output_dir/job_${final_dirname}.sbatch"
#!/bin/bash
#SBATCH --job-name=${job_identifier}
#SBATCH --partition=xh321
#SBATCH --account=weiwang
#SBATCH --nodes=1
#SBATCH --cpus-per-task=1
#SBATCH --ntasks-per-node=16
#SBATCH --output=${job_identifier}_%j.out

source /home/zhutao/project/source_Gaussian16_A03.source
cd $output_dir

# 使用绝对路径调用 RESP2.sh (Gaussian版)，确保脚本能被找到
sh /home/zhutao/scratch/workdir/ligprep/bashfile/RESP2.sh $filename

EOF

  # Make the job script executable
  chmod +x "$output_dir/job_${final_dirname}.sbatch"

  echo "Prepared: $output_dir (Job: ${job_identifier})"

  # Optionally submit the job script to SLURM
  if [ "$SUBMIT_JOB" = true ]; then
    sbatch "$output_dir/job_${final_dirname}.sbatch"
  fi
}

# 逻辑：处理单个文件并提取组名
process_file() {
    local f="$1"
    if [ -f "$f" ]; then
        # 获取文件所在的目录路径
        local parent_path=$(dirname "$f")
        # 获取该目录的名称作为 group_name (使用 realpath 避免 . 或 ..)
        local group_name=$(basename "$(realpath "$parent_path")")
        
        submit_job "$f" "$group_name"
    else
        echo "Warning: $f is not a valid file, skipping."
    fi
}

# Process input path logic
if [[ "$INPUT_PATH" == *"*"* ]]; then
  for file in $INPUT_PATH; do
    process_file "$file"
  done
elif [ -d "$INPUT_PATH" ]; then
  echo "Processing directory: $INPUT_PATH"
  for file in "$INPUT_PATH"/*; do
    process_file "$file"
  done
elif [ -f "$INPUT_PATH" ]; then
  process_file "$INPUT_PATH"
else
  echo "Invalid input path: $INPUT_PATH"
  exit 1
fi