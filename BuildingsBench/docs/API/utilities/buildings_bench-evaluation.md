# buildings_bench.evaluation

The `buildings_bench.evaluation` module contains the main functionality for evaluting a model
on the benchmark tasks.

The `buildings_bench.evaluation.managers.DatasetMetricsManager` class is the main entry point.

## Simple usage

```python
from buildings_bench import BuildingTypes
from buildings_bench.evaluation.managers import DatasetMetricsManager

# By default, the DatasetMetricsManager keeps track of NRMSE, NMAE, and NMBE
metrics_manager = DatasetMetricsManager()

# Iterate over the dataset using our building dataset generator
for building_name, building_dataset in buildings_datasets_generator:

    # Register a new building with the manager
    metrics_manager.add_building_to_dataset_if_missing(
        dataset_name, building_name,
    )

    # Your model makes predictions
    # ...

    # Register the predictions with the manager
    metrics_manager(
        dataset_name,           	  # the name of the dataset, e.g., electricity
        building_name,          	  # the name of the building, e.g., MT_001
        continuous_targets,      	  # the ground truth 24 hour targets
        predictions,           		  # the model's 24 hour predictions
        BuildingTypes.RESIDENTIAL_INT,    # an int indicating the building type
    )
```

## Advanced usage (with scoring rule)

```python
from buildings_bench.evaluation.managers import DatasetMetricsManager
from buildings_bench.evaluation import scoring_rule_factory

metrics_manager = DatasetMetricsManager(scoring_rule = scoring_rule_factory('crps'))

# Iterate over the dataset
for building_name, building_dataset in buildings_datasets_generator:

    # Register a new building with the manager
    metrics_manager.add_building_to_dataset_if_missing(
        dataset_name, building_name,
    )

    # Your model makes predictions
    # ...

    # Register the predictions with the manager
    metrics_manager(
        dataset_name,           # the name of the dataset, e.g., electricity
        building_name,          # the name of the building, e.g., MT_001
        continuous_targets,     # the ground truth 24 hour targets
        predictions,            # the model's 24 hour predictions
        building_types_mask,    # a boolean tensor indicating building type
        y_categories=targets,   # for scoring rules, the ground truth (discrete categories if using tokenization)
        y_distribution_params=distribution_params, # for scoring rules, the distribution parameters
        centroids=centroids   # for scoring rules with categorical variables, the centroid values
    )
```

---

## metrics_factory

::: buildings_bench.evaluation.metrics_factory
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## scoring_rule_factory

::: buildings_bench.evaluation.scoring_rule_factory
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## all_metrics_list

::: buildings_bench.evaluation.all_metrics_list
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

---

## BuildingTypes

::: buildings_bench.evaluation.managers.BuildingTypes
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true


## DatasetMetricsManager

::: buildings_bench.evaluation.managers.DatasetMetricsManager
    selection:
        members:
        - __call__
        - summary
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## MetricsManager

::: buildings_bench.evaluation.managers.MetricsManager
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

---

## MetricType

::: buildings_bench.evaluation.metrics.MetricType
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true


## BuildingsBenchMetric

::: buildings_bench.evaluation.metrics.BuildingsBenchMetric
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## Metric

::: buildings_bench.evaluation.metrics.Metric
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## absolute_error

::: buildings_bench.evaluation.metrics.absolute_error
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## squared_error

::: buildings_bench.evaluation.metrics.squared_error
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## bias_error

::: buildings_bench.evaluation.metrics.bias_error
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

---

## ScoringRule

::: buildings_bench.evaluation.scoring_rules.ScoringRule
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true


## RankedProbabilityScore

::: buildings_bench.evaluation.scoring_rules.RankedProbabilityScore
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

## ContinuousRankedProbabilityScore

::: buildings_bench.evaluation.scoring_rules.ContinuousRankedProbabilityScore
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

---

## aggregate

::: buildings_bench.evaluation.aggregate.return_aggregate_median
    options:
        show_source: false
        heading_level: 4
        show_root_heading: true

