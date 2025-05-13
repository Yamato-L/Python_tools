import math
azimuth_list = [0.7, 0.3, 0.8, 0.2, 359.8]
elevation_list = [90.2, 90.2, 89.7, 89.7, 89.7]
range_list = [43.0, 42.1, 40.8, 40.8, 40.8]


for azimuth, elevation, range in zip(azimuth_list, elevation_list, range_list):
    if azimuth < 180:
        m_azimuth = - azimuth * math.pi / 180.0
    else:
        m_azimuth = (360.0 - azimuth) * math.pi / 180.0

    # if azimuth < 180:
    #     m_azimuth = azimuth * math.pi / 180.0
    # else:
    #     m_azimuth = (azimuth - 360.0) * math.pi / 180.0

    m_elevation = (90.0 - elevation) * math.pi / 180.0

    x = range * math.cos(m_elevation) * math.cos(m_azimuth)
    y = range * math.cos(m_elevation) * math.sin(m_azimuth)
    z = range * math.sin(m_elevation)
    print(f'x: {x}, y: {y}, z: {z}')

# echo "-0.00154847 -0.0000597069" | cs2cs +proj=longlat +datum=WGS84 +to +proj=utm +zone=30 +datum=WGS84
# echo "-0.00130053 -0.00302225" | cs2cs +proj=longlat +datum=WGS84 +to +proj=utm +zone=30 +datum=WGS84
x=44.796974
y=0.121964
z=-0.860096
dist = math.sqrt(x**2 + y**2 + z**2)
print(f'dist: {dist}')