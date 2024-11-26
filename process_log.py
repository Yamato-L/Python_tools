import os
import csv
import json
import pandas as pd
import matplotlib.pyplot as plt

def process_log_file_aeb(log_file, csv_file):
    with open(log_file, 'r') as log, open(csv_file, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['stamp', 'aeb_switch', 'aeb_state', 'aeb_direction', 'aeb_fcn_state', 'IsAEBActive'])  # 写入CSV文件的头部

        # processing = False
        stamp = None
        frame_id_json = None

        for line in log:
            line = line.strip()

            if line == "------------------":
                if stamp is not None and frame_id_json is not None:
                    try:
                        frame_id_data = json.loads(frame_id_json)
                        # print(frame_id_data)
                        cm = frame_id_data.get('cm', {})

                        csv_writer.writerow([
                            stamp,
                            frame_id_data.get('aeb_switch', ''),
                            frame_id_data.get('aeb_state', ''),
                            frame_id_data.get('aeb_direction', ''),
                            frame_id_data.get('aeb_fcn_state', ''),
                            cm.get('IsAEBActive', ''),
                        ])
                    except json.JSONDecodeError as e:
                        print(f"Error decoding JSON: {e}")
                
                # processing = not processing
                stamp = None
                frame_id_json = None

            else:
                if line.startswith("stamp:"):
                    stamp = line[len("stamp:"):].strip()
                elif line.startswith("frame_id:"):
                    frame_id_json = line[len("frame_id:"):].strip().strip('"')

def process_log_file_radar(log_filename, csv_filename):
    with open(log_filename, 'r') as log_file, open(csv_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['timestamp_ns', 'sensor_timestamp_us', 'pipeline_start_timestamp_us', 'pipeline_finish_timestamp_us', 'pipeline_timestamp_us', 'available', 'camera_source', 'track_id', 'location_x', 'location_y', 'location_z'])  # 写入CSV头部

        block = []
        # within_block = False
        
        for line in log_file:
            if "------------------" in line:
                # if within_block:
                block[len(block)-1] = block[len(block)-1][:-1]
                json_str = '{' + ''.join(block) + '}'
                try:
                    json_obj = json.loads(json_str)
                    # print(json.dumps(json_obj, indent=4))
                    timestamp = json_obj.get('header',{}).get('stamp', '')
                    sensor_timestamp = json_obj.get('meta',{}).get('sensor_timestamp_us', '')
                    pipeline_start_timestamp = json_obj.get('meta',{}).get('pipeline_start_timestamp_us', '')
                    pipeline_finish_timestamp = json_obj.get('meta',{}).get('pipeline_finish_timestamp_us', '')
                    pipeline_timestamp = pipeline_finish_timestamp - pipeline_start_timestamp

                    lidar_perception_objects = json_obj.get('lidar_perception_objects', {})
                    available = lidar_perception_objects.get('available', '')

                    value = json_obj.get('value', '')# not found

                    lidar_perception_object_data = lidar_perception_objects.get('lidar_perception_object_data', {})
                    if lidar_perception_object_data:
                        track_id = lidar_perception_object_data.get('track_id', '')

                        location_bv = lidar_perception_object_data.get('position', {})
                        location_x = location_bv.get('x', '') if isinstance(location_bv, dict) else ''
                        location_y = location_bv.get('y', '') if isinstance(location_bv, dict) else ''
                        location_z = location_bv.get('z', '') if isinstance(location_bv, dict) else ''
                    else:
                        track_id = location_x = location_y = location_z = ''
                    # print("available: ", available, "camera_source: ", value, "track_id: ", track_id, "location_x: ", location_x)

                    csv_writer.writerow([timestamp, sensor_timestamp, pipeline_start_timestamp, pipeline_finish_timestamp, pipeline_timestamp, available, value, track_id, location_x, location_y, location_z])
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON: {json_str}")
                block = []
                # within_block = not within_block
            else:
                line = line.strip()
                if '{' in line:
                    parts = line.split('{')
                    parts[0] = '"' + parts[0].strip() + '":{'
                    line = ''.join(parts)
                elif ':' in line:
                    parts = line.split(':', 1)
                    parts[0] = '"' + parts[0].strip() + '":'
                    line = ''.join(parts)

                if not line.strip().endswith('{'):
                    line += ','

                if line.strip().startswith('}'):
                    block[len(block)-1] = block[len(block)-1][:-1]
                
                block.append(line)

def process_log_file_vision(log_filename, csv_filename, object_name):
    with open(log_filename, 'r') as log_file, open(csv_filename, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['timestamp_ns', 'sensor_timestamp_us', 'pipeline_start_timestamp_us', 'pipeline_finish_timestamp_us', 'pipeline_timestamp_us', 'available', 'camera_source', 'track_id', 'location_x'])  # 写入CSV头部

        block = []
        # within_block = False
        
        for line in log_file:
            if "------------------" in line:
                # if within_block:
                block[len(block)-1] = block[len(block)-1][:-1]
                json_str = '{' + ''.join(block) + '}'
                try:
                    json_obj = json.loads(json_str)
                    # print(json.dumps(json_obj, indent=4))
                    timestamp = json_obj.get('header',{}).get('stamp', '')
                    sensor_timestamp = json_obj.get('meta',{}).get('sensor_timestamp_us', '')
                    pipeline_start_timestamp = json_obj.get('meta',{}).get('pipeline_start_timestamp_us', '')
                    pipeline_finish_timestamp = json_obj.get('meta',{}).get('pipeline_finish_timestamp_us', '')
                    pipeline_timestamp = pipeline_finish_timestamp - pipeline_start_timestamp

                    available = json_obj.get('available', '')
                    objects = json_obj.get(object_name, {})

                    if objects:
                        camera_source = objects.get('camera_source', {})
                        value = camera_source.get('value', '')

                        track_info = objects.get('track_info', {})
                        track_id = track_info.get('track_id', '')

                        location_bv = objects.get('location_bv', {})
                        location_x = location_bv.get('x', '') if isinstance(location_bv, dict) else ''
                    else:
                        value = track_id = location_x = ''

                    # print("available: ", available, "camera_source: ", value, "track_id: ", track_id, "location_x: ", location_x)

                    csv_writer.writerow([timestamp, sensor_timestamp, pipeline_start_timestamp, pipeline_finish_timestamp, pipeline_timestamp, available, value, track_id, location_x])
                except json.JSONDecodeError:
                    print(f"Failed to decode JSON: {json_str}")
                block = []
                # within_block = not within_block
            else:
                line = line.strip()
                if "reserved_infos" in line:
                    continue
                if '{' in line:
                    parts = line.split('{')
                    parts[0] = '"' + parts[0].strip() + '":{'
                    line = ''.join(parts)
                elif ':' in line:
                    parts = line.split(':', 1)
                    parts[0] = '"' + parts[0].strip() + '":'
                    line = ''.join(parts)

                if not line.strip().endswith('{'):
                    line += ','

                if line.strip().startswith('}'):
                    block[len(block)-1] = block[len(block)-1][:-1]

                block.append(line)

def write_figure(csv_filename):
    data = pd.read_csv(csv_filename)
    figure_name = os.path.splitext(os.path.basename(csv_filename))[0]

    plt.figure(figsize=(10, 5))
    plt.plot(data['location_x'], marker='o')

    plt.title(figure_name + '_locationx')
    plt.ylabel('location')

    plt.grid()
    # plt.show()

    # plt.savefig(figure_name + '_locationx.png', dpi=300, bbox_inches='tight')

if __name__ == "__main__":
    # process data for aeb_stat
    # process_log_file_aeb('20241118/aeb_sts.log', '20241118/aeb_sts.csv')

    # process data for radar_object
    process_log_file_radar('20241118/radar_object.log', '20241118/radar_object.csv')

    # process data for vision_object
    process_log_file_vision('20241118/vision_object.log', '20241118/vision_object.csv', 'objects')

    # process data for vision_aeb_object
    process_log_file_vision('20241118/vision_aeb_object.log', '20241118/vision_aeb_object.csv', 'vision_aeb_objects')

    # write_figure('20241106/vision_aeb_object.csv')

#     import math
#     azimuth_list = [0.7, 0.3, 0.8, 0.2, 359.8]
#     elevation_list = [90.2, 90.2, 89.7, 89.7, 89.7]
#     range_list = [43.0, 42.1, 40.8, 40.8, 40.8]
#
#
#     for azimuth, elevation, range in zip(azimuth_list, elevation_list, range_list):
#         if azimuth < 180:
#             m_azimuth = - azimuth * math.pi / 180.0
#         else:
#             m_azimuth = (360.0 - azimuth) * math.pi / 180.0
#
#         # if azimuth < 180:
#         #     m_azimuth = azimuth * math.pi / 180.0
#         # else:
#         #     m_azimuth = (azimuth - 360.0) * math.pi / 180.0
#
#         m_elevation = (90.0 - elevation) * math.pi / 180.0
#
#         x = range * math.cos(m_elevation) * math.cos(m_azimuth)
#         y = range * math.cos(m_elevation) * math.sin(m_azimuth)
#         z = range * math.sin(m_elevation)
#         print(f'x: {x}, y: {y}, z: {z}')
#
# # echo "-0.00154847 -0.0000597069" | cs2cs +proj=longlat +datum=WGS84 +to +proj=utm +zone=30 +datum=WGS84
# # echo "-0.00130053 -0.00302225" | cs2cs +proj=longlat +datum=WGS84 +to +proj=utm +zone=30 +datum=WGS84
#     x=44.796974
#     y=0.121964
#     z=-0.860096
#     dist = math.sqrt(x**2 + y**2 + z**2)
#     print(f'dist: {dist}')