import geopandas

def create_save_stacked_intersection_df(gdf_primary, gdf_secondary, gdf_primary_col="FIPS", gdf_secondary_col="ID",
                                        geom_primary="geometry", geom_secondary="geometry", file_save=True,
                                        file_save_name="tracts_planning_area_ratios_stacked.pkl"):
    
    """
        Returns a stacked dataframe with all the fraction of intersecting areas for both geometries 
        
        Inputs:
            
            gdf_primary (GeoDataframe): primaryer geodataframe
            gdf_secondary (GeoDataframe): secondaryr dataframe
            gdf_primary_col (str): index column for gdf_primary
            gdf_secondary_col(str): index column for gdf_secondary
            file_save (bool): save file option
            
        Outputs:
        
            new_df: dataframe with columns primary_index, secondary_index,
                    primary_intersection_fraction, secondary_intersection_fraction
    
    """
    
    new_df = geopandas.overlay(gdf_primary[[gdf_primary_col, geom_primary]], gdf_secondary[[gdf_secondary_col, geom_secondary]], how='intersection')
    new_df["area_derived"] = new_df["geometry"].area
    
    gdf_primary["primary_area_derived"] = gdf_primary[geom_primary].area
    gdf_secondary["secondary_area_derived"] = gdf_secondary[geom_secondary].area
    
    new_df = (new_df[[gdf_primary_col, gdf_secondary_col, "geometry"]]
              .merge(gdf_primary[[gdf_primary_col, "primary_area_derived"]])
              .merge(gdf_secondary[[gdf_secondary_col, "secondary_area_derived"]]))
    
    
    new_df["gdf_primary_intersection_fraction"] = new_df["area_derived"] / new_df["primary_area_derived"]
    new_df["gdf_secondary_intersection_fraction"] = new_df["area_derived"] / new_df["secondary_area_derived"]
    
    new_df = new_df[[gdf_primary_col, gdf_secondary_col, "gdf_primary_intersection_fraction",
                     "gdf_secondary_intersection_fraction"]]
    
    if file_save==True:

        with open(file_save_name, "wb") as f:
            pickle.dump(new_df, f)
    
    return new_df
    
def create_intersection_matrix(gdf_intersection, gdf_intersection_col="gdf_primary_intersection_fraction",
                               gdf_primary_col="FIPS", gdf_secondary_col="ID", normalization=1, normalize_axis=1):
    
    """
    
        Provides the intersection matrix with the area intersection fraction a[i, j] for every primary id i
        and secondary id j. Normalization option available (To normalize double-counting)
        
        Inputs:
        
            gdf_intersection: stacked dataframe with every one-one mapping of primary ids
            gdf_intersection_col: usually the area intersection fraction. (Usually the fraction along the
                                  type (primary/secondary) you want to normalize)
                                  
            gdf_primary_col: index of primary gdf
            gdf_secondary_col: index of secondary gdf
            
            normalize_axis: 1 for normalizing along primary axis (generally)
                            0 for noramlizing along secondary axis
                            
        Outputs:
        
            returns: intersection_matrix
    
    """
    
    intersection_matrix = gdf_intersection.pivot_table(values=gdf_intersection_col,
                                                       index=gdf_primary_col,
                                                       columns=gdf_secondary_col,
                                                       fill_value=0)
    
    if normalization == 1:
        intersection_matrix = intersection_matrix.divide(intersection_matrix.sum(axis=normalize_axis),
                                                     axis=int(not normalize_axis))
                                                     
    return intersection_matrix
    
def matrix_linear_scaling(intersection_matrix, gdf_scale, gdf_scale_col="POPULATION", axis_scale=1,
                          normalize=1):
    
    """
        Scales the linear mapping matrix by a particular variable e.g. If you want to allocate demand by 
        population, scale the area intersection fraction matrix by the population of each of the FIPS
        using matrix_linear_scaling once by axis_scale=1, appropriate dataframe, scale_col="POPULATION",
        then allocate demand using matrix_linear_scaling once by axis_scale=0, appropriate dataframe,
        scale_col="demand_mwh"
        
        Inputs:
        
            intersection_matrix: matrix with every one-one mapping of primary ids
            gdf_scale: dataframe with the appropriate scaling data
            gdf_scale_col: the column being allocated (needs to have the same name in the dataframe
                            and the matrix)
                            
            axis_scale: scale of normalization and demand allocation
                        1 if data being multiplied to rows
                        0 if data being multiplied to columns
                        
            normalize: normalize along the axis mentioned
            
        Outputs:
        
            returns scaled matrix

    
    """
    
    if axis_scale == 1:
        unique_index = intersection_matrix.index
        index_name = intersection_matrix.index.name
        
    else:
        unique_index = intersection_matrix.columns
        index_name = intersection_matrix.columns.name
        
    if normalize == 1:
        
        intersection_matrix = intersection_matrix.divide(intersection_matrix.sum(axis=axis_scale),
                                                     axis=int(not axis_scale))
    
    return intersection_matrix.multiply(gdf_scale[gdf_scale[index_name].isin(unique_index)]
                                        .set_index(index_name)[gdf_scale_col], axis=int(not axis_scale))


def extract_multiple_tracts_demand_ratios(pop_norm_df, tract_ids):
    
    tract_demand_ratio_dict = pop_norm_df.loc[tract_ids].sum().to_dict()
    dict_area = pop_norm_df.sum(axis=0).to_dict()
    return {k: v / dict_area[k] for k, v in tract_demand_ratio_dict.items() if v != 0}



def extract_time_series_demand_multiple_tracts(ferc_df, ferc_df_col, tract_ids):
    
    ratio_dict = extract_multiple_tracts_demand_ratios(pop_norm_df, tract_ids)
    ferc_df_trunc = ferc_df[ferc_df[ferc_df_col].isin(ratio_dict.keys())]
    return ferc_df_trunc.pivot(index='local_time',
                        columns='eia_code',
                        values='demand_mwh').dot(pd.Series(ratio_dict))
