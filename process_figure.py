import re
import datetime
import pandas as pd
import matplotlib.pyplot as plt

def process_txt():
    # 读取txt文件
    file_path = 'data.txt'  # 替换为你的文件路径
    msg_times = []
    rcv_times = []
    pos = []
    ori = []

    # 读取文件并解析数据
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            if "Msg" in line and "Rcv" in line:
            # 解析 Msg time 和 Rcv time
                msg_time_match = re.search(r'\[Msg time\]:\s*([\d\.]+)', line)
                rcv_time_match = re.search(r'\[Rcv time\]:\s*(\d+)', line)

                msg_time = datetime.datetime.utcfromtimestamp(float(msg_time_match.group(1)))
                rcv_time = datetime.datetime.utcfromtimestamp(float(rcv_time_match.group(1)) / 1000)

                msg_time = msg_time.strftime('%S.%f')[:-3]
                rcv_time = rcv_time.strftime('%S.%f')[:-3]

                msg_times.append(msg_time)  # 获取 Msg time
                rcv_times.append(rcv_time)  # 获取 Rcv time

            if "pos" in line:
                # 解析 pos
                pos_match = re.search(r'pos\[(.*?)\]', line)
            if "ori" in line:
                ori_match = re.search(r'ori\[(.*?)\]', line)

                if pos_match and ori_match:
                    # 解析 pos 和 ori
                    pos_values = list(map(float, pos_match.group(1).split(',')))
                    ori_values = list(map(float, ori_match.group(1).split(',')))

                    pos.append(pos_values)  # 获取 pos
                    ori.append(ori_values)  # 获取 ori
            if len(pos) > 400:
                break

    # 将数据存储到 DataFrame 中
    data = {
        'Msg time': msg_times,
        'Rcv time': rcv_times,
        'Pos X': [p[0] for p in pos],
        'Pos Y': [p[1] for p in pos],
        'Pos Z': [p[2] for p in pos],
        'Ori X': [o[0] for o in ori],
        'Ori Y': [o[1] for o in ori],
        'Ori Z': [o[2] for o in ori]
    }

    df = pd.DataFrame(data)

    # 保存为 CSV 文件
    output_path = 'output_data.csv'  # 你可以修改输出文件路径
    df.to_csv(output_path, index=False)

    print(f"Data has been saved to {output_path}")
def write_figure_txt():
    # 读取txt文件并解析数据
    file_path = '2.txt'  # 修改为你的文件路径
    x = []
    y = []

    # 读取文件
    with open(file_path, 'r') as file:
        for line in file:
            # 分割每一行，获取 x, y, z 数据
            pos = line.strip().split(',')
            x.append(float(pos[0]))  # 获取 x 值
            y.append(float(pos[1]))  # 获取 y 值

    # 创建图形并绘制
    plt.plot(x, y, marker='o', linestyle='-', color='b', label='Path')

    # 添加标题和标签
    plt.title('X and Y Plot')
    plt.xlabel('X')
    plt.ylabel('Y')


    # 显示图例
    plt.legend()

    # 显示图形
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    # process_txt();

    # 读取文件内容
    with open('imu_250305_leftright.log', 'r') as file:
        content = file.read()

    # 正则表达式提取数据
    pattern = re.compile(
        r'timestamp_us: (\d+).*?'
        r'accx: ([\d\.\-e]+).*?'
        r'accy: ([\d\.\-e]+).*?'
        r'accz: ([\d\.\-e]+).*?'
        r'gyrox: ([\d\.\-e]+).*?'
        r'gyroy: ([\d\.\-e]+).*?'
        r'gyroz: ([\d\.\-e]+)',
        re.DOTALL
    )

    matches = pattern.findall(content)

    # 提取数据
    timestamps = []
    accx = []
    accy = []
    accz = []
    gyrox = []
    gyroy = []
    gyroz = []

    for match in matches:
        timestamps.append(int(match[0]))
        accx.append(float(match[1]))
        accy.append(float(match[2]))
        accz.append(float(match[3]))
        gyrox.append(float(match[4]))
        gyroy.append(float(match[5]))
        gyroz.append(float(match[6]))

    # 绘制图表
    plt.figure(figsize=(12, 8))

    # 绘制加速度数据
    plt.subplot(2, 1, 1)
    plt.plot(timestamps, accx, label='accx')
    plt.plot(timestamps, accy, label='accy')
    plt.plot(timestamps, accz, label='accz')
    plt.xlabel('Timestamp (us)')
    plt.ylabel('Acceleration')
    plt.title('Acceleration over Time')
    plt.legend()

    # 绘制角速度数据
    plt.subplot(2, 1, 2)
    plt.plot(timestamps, gyrox, label='gyrox')
    plt.plot(timestamps, gyroy, label='gyroy')
    plt.plot(timestamps, gyroz, label='gyroz')
    plt.xlabel('Timestamp (us)')
    plt.ylabel('Angular Velocity')
    plt.title('Angular Velocity over Time')
    plt.legend()

    plt.tight_layout()
    # plt.show()
    plt.savefig( 'imu_leftright.png', dpi=300, bbox_inches='tight')