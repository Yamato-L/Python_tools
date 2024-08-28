# 说明文档
## 简介
此脚本用于处理日志文件并将其转换为 CSV 文件。脚本包含三个主要的处理函数：process_log_file_aeb、process_log_file_radar 和 process_log_file_vision，它们分别处理不同类型的日志文件。根据日志文件的内容和格式，脚本会将数据解析并保存到指定的 CSV 文件中。

## 使用说明
1. 替换日志文件路径: 输入的日志文件路径，注意相对路径应放在当前文件夹目录。
注意：log文件第一个数据需要用------------------分割header，示例如下：
```
[mosadaptor] Set thread priority on non-linux ok, thread_id=2, thread_priority=10, errno=3, error=No such process
current mfrtool is new,this is just log info, has no effection.
------------------
header {
  seq: 0
  stamp: 1722938935411266050
  frame_id: "enu"
}
```
2. 设置输出的CSV 文件: 输出的 CSV 文件名，将保存日志文件处理后的数据。

修改示例：
```
if __name__ == "__main__":
    # 处理 AEB 类型日志文件
    process_log_file_aeb('your_aeb_log_file.log', 'your_aeb_output.csv')

    # 处理 Radar 类型日志文件
    process_log_file_radar('your_radar_log_file.log', 'your_radar_output.csv')

    # 处理 Vision 类型日志文件
    process_log_file_vision('your_vision_log_file.log', 'your_vision_output.csv')
```
在上述示例中，您需要：

- 替换 your_aeb_log_file.log 为您的 AEB 类型日志文件名。
- 替换 your_aeb_output.csv 为处理后生成的 CSV 文件名。
- 替换 your_radar_log_file.log 为您的 Radar 类型日志文件名。
- 替换 your_radar_output.csv 为处理后生成的 CSV 文件名。
- 替换 your_vision_log_file.log 为您的 Vision 类型日志文件名。
- 替换 your_vision_output.csv 为处理后生成的 CSV 文件名。

3. 执行 python process_log.py （需要python环境）
4. 使用excel打开输出的csv文件，选中需要分析的track_id、location_x或其他数据，生成折线图、散点图等图表进行分析


