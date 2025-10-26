## Identifying player similarities in Football

Football clubs and scouting agencies, such as Burnley FC, need ways to identify affordable and tactically appropriate player alternatives when replacing retired/sold players. Current methods rely heavily on manual filtering of stats and extensive video analysis through platforms such as WyScout, which is time-consuming and subject to human bias. Pocket Scout offers a scalable, automated solution that surfaces similar players by analyzing both event metrics (e.g., goals, assists) and spatial behavior on the pitch. This gives clubs and analysts deeper tactical insights and dramatically cuts down scouting time.


Status Quo & Business Metric:
Current Approach: People rely on scouting reports and video analyses that can be subjective and time consuming. 

Proposal Advantage: Our system provides a data-driven, spatial-centric tool, enabling users to make more strategic, long-term decisions about which players to scout further and eventually purchase.


Business Metrics for Success:
Precision/purity of Player Similarity: Proportion of top-N retrieved players who match in refined roles (from Transfermarkt-enhanced WyScout data).
By focusing on the spatial behaviour of players, this system transfers video analysis-dependent information into a dashboard that is numerically and heatmap-based.

### System diagram

![System Diagram](https://github.com/MusondaSinkala/Pocket-Scout/blob/main/system_diagram.jpeg?raw=true)


### Summary of outside materials

| Dataset           | How it was created | Conditions of use | Link              |
|-------------------|--------------------|-------------------|-------------------|
| WyScout Data      |                    | n/a               | *1 below          |
| Statsbomb Data    |                    | n/a               | *2 below          |
| Transfermarkt Data|                    | n/a               | *3 below          |
| Model 1: K-means <br> Clustering | n/a                | n/a               | n/a               |
| Model 2: K-Nearest-Neighbours Model | n/a                | n/a               | n/a               |
| Model 3: Random Forest Classifier | n/a                | n/a               | n/a               |


*1 = https://figshare.com/collections/_/4415000

*2 = https://github.com/Torvaney/statsbombapi

*3 = https://data.world/dcereijo/player-scores
