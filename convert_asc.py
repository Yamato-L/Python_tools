def convert_can_dump_to_asc(input_file, output_file):
    with open(input_file, 'r') as f_in, open(output_file, 'w') as f_out:
        # 写入ASC文件头
        f_out.write("date Mon Jan 1 00:00:00.000 2024\n")
        f_out.write("base hex  timestamps absolute\n")
        f_out.write("internal events logged\n")
        f_out.write("// version 13.0.0\n")
        f_out.write("// Measurement UUID: 523f8d33-0ca4-4251-914f-79b28bfed7a9\n")
        f_out.write("0.000000 Start of measurement\n")
        
        # 逐行读取并转换
        for line in f_in:
            if line.strip() and not line.startswith(';'):  # 跳过空行和注释行
                try:
                    # 解析原始数据
                    parts = line.strip().split()
                    if len(parts) >= 4:  # 确保有足够的部分
                        # 处理带括号的时间戳
                        timestamp = float(parts[0].strip('()'))
                        timestamp = timestamp - 1742452373

                        #if parts[2] in["18FEE81C", "18FEF31C", "18FEF41C", "18FEF61C"] :#"18FEE61C", "18FEE71C",
                        if len(parts[2]) == 3:
                            can_id = parts[2]
                        else:
                            can_id = parts[2] + 'x'  # can0 之后的ID
                        can_id_hex = parts[2]
                        can_id_dec = str(int(can_id_hex, 16))

                        # 跳过 [8] 部分，获取数据
                        length_str = parts[3].strip('[]')  # 移除方括号
                        data_length = int(length_str)

                        data_start = line.find(']') + 1
                        data = line[data_start:].strip()
                    
                        # 转换为标准ASC格式：时间戳 通道 ID Rx/Tx d 长度 数据
                        formatted_line = f"   {timestamp:.6f} 1  {can_id:<15} Tx   d {data_length} {data}\n"#   Length = 475789 BitCount = 123 ID = {can_id_dec}x\n"
                        f_out.write(formatted_line)
                except Exception as e:
                    print(f"Error processing line: {line.strip()}")
                    print(f"Error details: {str(e)}")

# 使用示例
input_file = "P_D2701_nav.asc"
output_file = input_file.replace(".asc", "_converted.asc")
convert_can_dump_to_asc(input_file, output_file)