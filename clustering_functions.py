import numpy as np
import pandas as pd
import os

from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import haversine_distances


def transform_to_array(df: pd.DataFrame, lon: str, lat: str) -> np.array:
    """Transform dataframe to numpy array
    Args:
        df (pd.DataFrame): df from functions get_df_from_txt and get_df_from_csv
    Returns:
        [numpy.array]: 2 dimensions array, 1d - points, 2d - coordinates of point (longitute, latitude)
    """    
    coor_array = np.array(df[[lon,lat]])
    return coor_array


def dbscan_clustering(points: np.array, epsilon: float) -> pd.Series:
    """Clustering points
    Args:
        points (2d numpy array): array of points
        epsilon (float): distance between neighbours points 
    Returns:
        [pandas Series]: Series, where every element is number of cluster for every point
    """    
    db = DBSCAN(eps=epsilon/6371., min_samples=1, metric='haversine', algorithm='auto').fit(np.radians(points))
    
    return pd.Series(db.labels_)


def choose_point(points):
    """Chose only one points from one cluster points
    Args:
        points (numpy array): one cluster points
    Returns:
        [numpy array]: one point
    """    
    rad_points = np.radians(points)
    index = haversine_distances(rad_points).sum(axis=1).argmin()
    return points[index]


def auto_correction_data(coor_array, _labels):
    """Auto corralarion of spartial data
    Args:
        coor_array (numpy array): points of occurances
        _labels (pandas series): label of clusters for every point
    Returns:
        [numpy array]: points where in one cluster only one point
    """    
    final_array = np.array(list())
    unique_labels = _labels.unique()
    for label in unique_labels:
        indexes = _labels[_labels==label].index
        final_array = np.append(final_array, choose_point(coor_array[indexes]), axis=0)
    final_array = np.reshape(final_array, (-1,2))
    return final_array


def make_final_df(final_coor, name):
    """Create data frame with 3 columns: species(name), longitude, latitude 
       Suitable for maxent samples
    Args:
        final_coor (numpy array): numpy array from auto_corralarion_data function
        name (string): name of species
    Returns:
        [pandas DataFrame]: dataframe with 3 columns: species(name), longitude, latitude
    """    
    df = pd.DataFrame(final_coor)

    df.columns = ['longitude','latitude']
    df['species'] = name
    df = df[['species','longitude','latitude']]
    return df


def do_pipeline(df: pd.DataFrame, name: str, lon: str, lat: str, epsilon: float):

    coor_array = transform_to_array(df, lon, lat)

    _labels = dbscan_clustering(coor_array, epsilon)

    final_df = auto_correction_data(coor_array, _labels)

    final_df = np.reshape(final_df, (-1,2))

    final_df = make_final_df(final_df, name)

    return final_df