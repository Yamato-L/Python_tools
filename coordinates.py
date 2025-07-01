from pyproj import CRS, Geod, Transformer
import numpy as np

# 参考点经纬度
base_lat, base_lon, base_alt = 36.5653323, 119.1605849, 0

def enu_to_wgs84(e, n, u, lat0=base_lat, lon0=base_lon, alt0=base_alt):
    """
    ENU (East-North-Up) 局部坐标转 WGS84 (经纬度+高程)
    :param e: 东向坐标（米）
    :param n: 北向坐标（米）
    :param u: 天向坐标（米）
    :param lat0: 原点纬度
    :param lon0: 原点经度
    :param alt0: 原点高程
    :return: (lon, lat, alt) 经度、纬度、高程
    """
    # 1. 原点WGS84 → ECEF
    transformer = Transformer.from_crs("epsg:4979", "epsg:4978", always_xy=True)
    x0, y0, z0 = transformer.transform(lon0, lat0, alt0)

    # 2. ENU → ECEF
    lam = np.radians(lon0)
    phi = np.radians(lat0)
    R = np.array([
        [-np.sin(lam),              -np.sin(phi)*np.cos(lam),  np.cos(phi)*np.cos(lam)],
        [ np.cos(lam),              -np.sin(phi)*np.sin(lam),  np.cos(phi)*np.sin(lam)],
        [           0,                        np.cos(phi),              np.sin(phi)]
    ])
    enu = np.array([e, n, u])
    dx, dy, dz = R @ enu
    x = x0 + dx
    y = y0 + dy
    z = z0 + dz

    # 3. ECEF → WGS84
    transformer_back = Transformer.from_crs("epsg:4978", "epsg:4979", always_xy=True)
    lon, lat, alt = transformer_back.transform(x, y, z)
    return lon, lat, alt

def wgs84_to_enu(lon, lat, alt, lat0, lon0, alt0):
    """
    WGS84 (经纬度+高程) 转 ENU (East-North-Up) 局部坐标
    :param lon: 目标点经度
    :param lat: 目标点纬度
    :param alt: 目标点高程
    :param lat0: 原点纬度
    :param lon0: 原点经度
    :param alt0: 原点高程
    :return: (e, n, u) 东北天坐标
    """
    # 1. WGS84 -> ECEF
    transformer = Transformer.from_crs("epsg:4979", "epsg:4978", always_xy=True)
    x, y, z = transformer.transform(lon, lat, alt)
    x0, y0, z0 = transformer.transform(lon0, lat0, alt0)

    # 2. ECEF -> ENU
    # 计算旋转矩阵
    lam = np.radians(lon0)
    phi = np.radians(lat0)
    R = np.array([
        [-np.sin(lam),              np.cos(lam),             0],
        [-np.sin(phi)*np.cos(lam), -np.sin(phi)*np.sin(lam), np.cos(phi)],
        [np.cos(phi)*np.cos(lam),  np.cos(phi)*np.sin(lam),  np.sin(phi)]
    ])
    diff = np.array([x - x0, y - y0, z - z0])
    enu = R @ diff
    return enu[0], enu[1], enu[2]


def wgs84_to_gauss(lon, lat, zone_width=6, ellps='WGS84'):
    """
    将经纬度转换为高斯坐标（带带号）
    :param lon: 经度(度)
    :param lat: 纬度(度)
    :param zone_width: 分带宽度(3或6度)
    :param ellps: 椭球体('WGS84'/'CGCS2000'/'Beijing54')
    :return: x_with_zone, y, curv: 带带号的x坐标(如20500001.23表示20带500001.23米), y坐标(米), 中央子午线经度(度)
    """
    # 计算中央子午线
    if zone_width == 6:
        zone_number = int((lon + 6) / 6) if lon >=0 else int((lon + 6) / 6) + 1
        curv = zone_number * 6 - 3
    else:  # 3度带
        zone_number = int((lon + 1.5) / 3 + 0.5)
        curv = zone_number * 3
    
    # 创建坐标系
    wgs84 = CRS.from_epsg(4326)
    gauss_crs = CRS(
        proj='tmerc',
        ellps=ellps,
        lat_0=0,
        lon_0=curv,
        x_0=500000,
        k=1
    )
    
    # 执行转换
    transformer = Transformer.from_crs(wgs84, gauss_crs, always_xy=True)
    x, y = transformer.transform(lon, lat)
    
    # 添加带号(6度带前补2位，3度带前补1位)
    x_with_zone = zone_number * 1000000 + x
    
    return x_with_zone, y, curv

def gauss_to_wgs84(x_with_zone, y, curv=None, ellps='WGS84'):
    """
    将带带号的高斯坐标转换为经纬度
    :param x_with_zone: 带带号的x坐标(如20500000表示20带500000米)
    :param y: y坐标
    :param central_meridian: 中央子午线
    :param ellps: 椭球体模型
    :return: lon, lat: 经纬度(度)
    """
    # 解析带号和实际x坐标
    if x_with_zone > 10000000:  # 6度带
        zone_number = int(x_with_zone // 1000000)
        x = x_with_zone % 1000000
        auto_curv = zone_number * 6 - 3  # 6度带公式
    else:  # 3度带
        zone_number = int(x_with_zone // 100000)
        x = x_with_zone % 100000
        auto_curv = zone_number * 3
    
    # 使用手动指定的中央子午线或自动计算的
    curv = curv if curv is not None else auto_curv
    
    # 创建坐标系
    wgs84 = CRS.from_epsg(4326)
    gauss_crs = CRS(
        proj='tmerc',
        ellps=ellps,
        lat_0=0,
        lon_0=curv,
        x_0=500000,
        k=1
    )
    
    # 执行转换
    transformer = Transformer.from_crs(gauss_crs, wgs84, always_xy=True)
    lon, lat = transformer.transform(x, y)
    
    return lon, lat

def gauss_to_enu(x, y, central_meridian, ellps='WGS84'):
    lon, lat = gauss_to_wgs84(x, y, central_meridian)
    e,n,u = wgs84_to_enu(lon, lat, 0, base_lat, base_lon, base_alt)
    return e,n,u

def enu_to_gauss(e, n, u):
    lon, lat, alt = enu_to_wgs84(e, n, u)
    x, y, central_meridian = wgs84_to_gauss(lon, lat)
    return x, y, central_meridian

x, y, central_meridian = enu_to_gauss(100, -160, 0)
print(x, y, central_meridian)

x, y, central_meridian = enu_to_gauss(100, -280, 0)
print(x, y, central_meridian)

x, y, central_meridian = enu_to_gauss(230, -160, 0)
print(x, y, central_meridian)

x, y, central_meridian = enu_to_gauss(230, -280, 0)
print(x, y, central_meridian)

lon, lat, alt = enu_to_wgs84(10, 10, 0, base_lat, base_lon, base_alt)
print(lon, lat, alt)

e_back,n_back, u_back = wgs84_to_enu(lon, lat, 0, base_lat, base_lon, base_alt)
print(e_back,n_back, u_back)

x, y, central_meridian = wgs84_to_gauss(lon, lat)
print(x, y, central_meridian)

lon_back, lat_back = gauss_to_wgs84(20500006.2584,4048272.8532,119.15978492)
print(lon_back, lat_back)