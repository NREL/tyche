import sys

import pandas as pd
import numpy as np
import seaborn as sb
import matplotlib.pyplot as plt

def generate_distn(
    response_df,
    expert_weights = None,
    expert_column = 'expert_id',
    response_columns = {'param': ['param_min','param_mode','param_max']},
    measures = ['min', 'mode', 'max'],
):
    """
    Convert raw elicitation responses into triangular distribution parameters.
    
    Reminder that scipy.stats.triang uses the following parameters:
    (c, loc=0, scale=1, size=1, random_state=None)
    c is the peak of the distribution (mode, NOT mean or median)
    scale is the width of the distribution (max - min)
    loc is the minimum of the distribution
    
    Parameters
    ----------
    response_df: DataFrame
        DataFrame containing elicited responses. No default value.
        Column names listed in response_columns must appear in this DataFrame.
        Otherwise the method will break.
    
    expert_weights: Dict
        Weights to apply to individual expert responses when calculating an
        aggregate probability distribution.
        Keys (str) are expert ID information contained in response_df.
        Values (float) are weights to apply to each expert's responses.
        Weights are normalized to sum to 1 before use.
        All experts without a weight provided are assigned a weight of zero,
        that is, are excluded from the aggregate distribution parameters.
        If expert_weights is None (the default value), then experts are
        weighted equally.
    
    expert_column: str
        Name of the column with expert ID information.
        Values in this column must match up with the ID information provided in 
        the expert_weights dictionary.
    
    measures: List(str)
        List of statistical measures elicited.
        For triangular distributions, measures must include at least
        the minimum, maximum, and mode (most likely/most common).
        Required values: min, max, mode
    
    response_columns: Dict
        Dictionary listing column names with elicited responses, by parameter.
        Keys are parameter names.
        values are lists of columns with responses for that parameter.
        Each column in the list must correspond to the measures listed in 
        the measures parameter.
    
    Returns
    -------
    Dict
        keys are elicited parameter names from the response_columns input
        Value is a string defining a triangular distribution for each parameter
    """
    # If the measures can't be used as min, mode, and max, throw an error
    if not all(_m in measures for _m in ['min', 'mode', 'max']):
        sys.exit('parameter error: measures must contain a minimum, maximum, and central measure')
    
    # Get list of all experts
    _all_experts = response_df[expert_column].drop_duplicates().values
    # If weights have been provided,
    if expert_weights:
        # For any expert not provided a weight, assign a zero weight which
        # excludes that expert's responses from the weighted average response
        for _e in _all_experts:
            if _e not in expert_weights:
                expert_weights[_e] = 0.0
        # then add a column with the expert weights to response_df
        response_df['weights'] = response_df['expert_id'].map(expert_weights)
    else:
        # If weights have not been provided, all experts get an equal weighting
        response_df['weights'] = 1.0
    
    # Apply normalized weights to the responses, store in separate variable
    parameters_agg = {}
    for _p in response_columns.keys():
        _r = [np.average(response_df.loc[np.where(~np.isnan(response_df[f'{_c}']))[0].tolist(), f'{_c}'].unstack(),
                         weights=response_df.loc[np.where(~np.isnan(response_df[f'{_c}']))[0].tolist(), 'weights']) for _c in [colname for value in response_columns.values() for colname in value]]
        parameters_agg[f'{_p}_dist'] = f'st.triang(c={np.round(_r[1], decimals=2)}, loc={np.round(_r[2]-_r[0], decimals=2)}, scale={np.round(_r[0], decimals=2)})'
        
    return parameters_agg


def visualize_responses(
    response_df,
    expert_column = 'expert_id',
    response_columns = {'param': ['param_min','param_mode','param_max']},
    plot_type = 'point',
    x_axis_label = 'question',
    y_axis_label = 'response',
    save = False
):
    """
    Generate point plots of expert responses for visual outlier identification.
    
    This function will visualize one parameter at a time. Multiple measures for
    the same parameter can be visualized simultaneously.
    
    Parameters
    ----------
    response_df: DataFrame
        DataFrame containing elicited responses. No default value.
        Column names listed in response_columns must appear in this DataFrame.
        Otherwise the method will break.

    expert_column: str
        Name of the column with expert ID information.
        Values in this column must match up with the ID information provided in 
        the expert_weights dictionary.
    
    response_columns: Dict
        Dictionary listing column names with elicited responses, by parameter.
        Keys are parameter names.
        values are lists of columns with responses for that parameter.
        Each column in the list must correspond to the measures listed in 
        the measures parameter.
    
    plot_type: str ('point' or 'box')
        Create a point plot or a box-and-whisker plot
    
    x_axis_label: str
        Label for the x axis of the response plot
    
    y_axis_label: str
        Label for the y axis of the response plot
    
    save: Bool
        If True, the response plot is saved as an SVG.
    
    Returns
    -------
    None
        Plot is displayed and/or saved    
    """
    sb.set(style='whitegrid')

    fig, ax = plt.subplots(figsize=(6,4))
    
    _df = pd.melt(
        response_df,
        id_vars = expert_column,
        value_vars = list(response_columns.values())[0],
        var_name = 'question',
        value_name = 'response',
    )
    
    if plot_type == 'point':
        responses = sb.pointplot(
            data = _df,
            x = 'question',
            y = 'response',
            hue = expert_column,
            join = False,
            dodge = True
        )
    elif plot_type == 'box':
        responses = sb.boxplot(
            data = _df,
            x = 'question',
            y = 'response',
        )
    else:
        sys.exit('plot type must be point or box')
        
    plt.xlabel(x_axis_label)
    plt.ylabel(y_axis_label)
    
    if save:
        plt.savefig(f'{list(response_columns.keys())[0]}_responses.svg')