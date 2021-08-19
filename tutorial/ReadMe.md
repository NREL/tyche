# ReadMe -- Transport Model

## Model Overview
- The techno-economic model framework is applicable to all powertrain designs, but the data used to build and test the 
model is specific to a Class 8 diesel tractor. 
- In theory, this general powertrain/vehicle approach should work for non-on-road vehicle applications, but
a nother model or data would be needed to replace FASTSim estimates of powertrain design and fuel efficiency. 
- Please see the [Jupyter Notebook](transport_model.ipynb) for in-line documenation and discussion of `V1` and `V2` models. 
- Data flow diagrams are in the [model-architecture.pptx](./data/transport_model_v1/model-architecture.pptx).

## Data Sources
The `parameters.tsv` and `designs.tsv` [data](./data/transport_model_v1) are based on the recent NREL Report evaluating the total cost of ownership of commercial vehicles. 
- Citation: Hunter, C., Penev, M., Reznicek, E., Lustbader, J., Birky, A., & Zhang, C. (2021). Spatial and Temporal Analysis of the Total Cost of Ownership for Class 8 
Tractors and Class 4 Parcel Delivery Trucks (Technical NREL/TP-5400-71796). National Renewable Energy Laboratory.
- FASTSim inputs and outputs from this report have been added [here](./data/transport_model_v1/fastsim-data/) and can also be found on [GitHub here](https://github.nrel.gov/SERA/market-segmentation/blob/master/FASTSim/fastsim-python-outputs/FASTSimPyOutputs.csv)
- Reach out to Misho Penev if you have any questions or need to know more about the FASTSim analysis and data.

## Tyche Data Files
- All `Tyche` input data files are located in the [data/transport_model_v1](./data/transport_model_v1) directory. 
- The [transport_model_data.xlsx workbook](./data/transport_model_v1/transport_model_data.xlsx) was used to create the data files. 
Then executing the [create_tsv.py](./data/transport_model_v1/create_tsv.py) script creates the `Tyche` input `.tsv` files.