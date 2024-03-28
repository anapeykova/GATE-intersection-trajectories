# Trajectory Preprocessing and Classification for LiDAR-Derived Data

A project on traffic trajectory analysis using machine learning. The data originates from a 6-LiDAR system set up at the intersection of Cherni Vruh Blvd and Sreburna St in Sofia, Bulgaria. Initially stored as binary .osef files, the data is accessed via TCP stream (using VPN) and subsequently parsed into .csv format. Each row within the .csv file represents the timestamped location of an object detected at the intersection. Objects are identified by unique `object_id`; grouping by `object_id` and ordering by timestamp allows the reconstruction of the object's trajectory. 



## traffic_flow_report
This is a straightforward pipeline combining all of the processes explored in the notebooks below. It takes a .csv file of the LiDAR output and produces a simple traffic flow heatmap.

1. First, complete trajectories are filtered out.
2. Then, the trajectories are classified using a pre-trained RNN model.
3. `report.py` takes the predictions from the RNN model and gives the number of vehicles which took certain paths. The results are printed out in terminal and visualized in a `folium` heatmap (opened as html in browser).

### Use
1. Navigate to traffic_flow_report/
2. Run the report script with a .csv file as an argument (`sample.csv` file available)

```
cd traffic_flow_report
python -m report "sample.csv"
```
### Demo
https://www.loom.com/share/fdc6bc6e4319486a880d2d1eb0014899?sid=686fa7aa-fba7-4795-a929-906820a79ee7


## capstone notebooks
#### aggregate_and_cluster
In this notebook, I combine the sample datasets from the LiDAR and filter trajectories based on semantic map ('traffic_flow_report/lanes_and_int.geojson'). Trajectories are manually split by incoming lane, then clustered using k-medoids with Hausdorff distance; model performance is evaluated through visualizations and appropriate metrics. The labeled trajectories are saved as file and visualized in an interactive `folium` map.

#### dbscan_hausdorff
In this notebook, I implement and evaluate another clustering method, DBSCAN. The algorithm is density-based and offers the advantage of noise detection: that is, trajectories are not forced into clusters;  instead, they can be labeled as noise, denoted by class '-1'. The implementation clusters all trajectories simultaneously, unlike the k-medoids approach where trajectories are first split into four groups. However, the results are worse than k-medoids as using the same distance measure - Hausdorff distance - does not allow the algorithm to distinguish between trajectories that are spatially close but moving in opposite directions.

#### dbscan_frechet
In this notebook, I implement and evaluate DBSCAN using a Frechet distance matrix. Unlike Hausdorff, the Frechet distance is directed. This is more suited for trajectory analyses but it does come at a higher computational cost. The model parameters (eps and MinPts) are tuned using grid search to find the optimal number of clusters and noise. Possibly due to different densities, performance is not comparable to the more manual approach taken with k-medoids.

#### means
Based on the clusters derived from k-medoids, a model intersection is constructed using the means of each cluster. This model ('traffic_flow_report/means.geoJSON') is used for visualization of the possible paths at the intersection.

#### augmentation_sampling
The labeled trajectory dataset is augmented using interpolation to increase the number of points by a factor of n; the interpolated trajectories are then uniformly sampled to derive n new trajectories from each. The output is a large, labeled dataset used for training an RNN model.

#### test_augmentation
Through interpolation, the initially jittery trajectories are smoothed to varying degrees. The extent of smoothing is directly related to the level of interpolation and sampling: the higher these factors, the greater the smoothing effect on the trajectories. The augmented dataset is compared to the original based on trajectory properties to determine the appropriate level of interpolation such that the augmented dataset is indistinguishable from the original. A 3-fold increase in interpolation (resulting in a 4-fold increase in the dataset size) demonstrates good performance based on KS statistics and corresponding p-values.

#### rnn_classification
I create and evaluate a simple RNN model that learns on the labeled large dataset. Weights are saved to use in the 'traffic_flow_report' pipeline.

