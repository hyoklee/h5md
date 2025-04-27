# HDF5 File Structure: sample.h5


### Attributes:

| Name | Value | Type |
|------|--------|------|
| `created_by` | `markitdown-hdf5 test script` | `str` |
| `description` | `Sample HDF5 file for testing markitdown plugin` | `str` |


## Group: /data


### Dataset: matrix

### Dataset Properties:

| Property | Value |
|----------|--------|
| Shape | `(3, 3)` |
| Type | `float64` |


### Dataset: timeseries

### Dataset Properties:

| Property | Value |
|----------|--------|
| Shape | `(100,)` |
| Type | `int32` |


## Group: /metadata

### Attributes:

| Name | Value | Type |
|------|--------|------|
| `version` | `1.0` | `str` |


### Dataset: config

### Dataset Properties:

| Property | Value |
|----------|--------|
| Shape | `(3,)` |
| Type | `|S10` |

### Attributes:

| Name | Value | Type |
|------|--------|------|
| `type` | `settings` | `str` |


## Group: /sensors

### Attributes:

| Name | Value | Type |
|------|--------|------|
| `location` | `Building A` | `str` |


### Dataset: temperature

### Dataset Properties:

| Property | Value |
|----------|--------|
| Shape | `(24,)` |
| Type | `float64` |

### Attributes:

| Name | Value | Type |
|------|--------|------|
| `sampling_rate` | `1 per hour` | `str` |
| `unit` | `celsius` | `str` |
