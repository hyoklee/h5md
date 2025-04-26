# Table of Contents

- [📦 HDF5 File: `sample.h5`](#📦-hdf5-file-sample.h5)
- [📑 File Information](#📑-file-information)
- [🌳 File Structure](#🌳-file-structure)
- [📁 Group: `data`](#📁-group-data)
- [📁 Group: `metadata`](#📁-group-metadata)
- [📁 Group: `sensors`](#📁-group-sensors)

# 📦 HDF5 File: `sample.h5`

## 📑 File Information
| Property | Value |
|----------|--------|
| Size on disk | `11.7 KB` |
| Last modified | `2025-04-26 13:23:25.366119` |
| Created | `2025-04-26 13:23:25.354394` |

## 🌳 File Structure
📝 **Attributes:**
    | Name | Value | Type |
    |------|--------|------|
    | `created_by` | `markitdown-hdf5 test script` | _str_ |
    | `description` | `Sample HDF5 file for testing markitdown plugin` | _str_ |

## 📁 Group: `data`
    ### 📊 Dataset: `matrix`
        #### 📋 Properties:
        | Property | Value |
        |----------|--------|
        | Shape | `(3, 3)` |
        | Type | `float64` |
        | Size in memory | `72.0 B` |
        | Chunks | `None` |
        | Compression | `None` |
        
        #### 📈 Statistics:
        | Metric | Value |
        |--------|--------|
        | Minimum | `0.054` |
        | Maximum | `0.967` |
        | Mean | `0.545` |
        | Median | `0.564` |
        | Std Dev | `0.278` |
        | Unique Values | `9` |
        
        #### 👁️ Preview:
        ```
        First 3x3 elements:
[[0.49468684 0.41324788 0.18327774]
 [0.96680209 0.70957749 0.81521978]
 [0.05404344 0.56405017 0.70671099]]
        ```
        
    ### 📊 Dataset: `timeseries`
        #### 📋 Properties:
        | Property | Value |
        |----------|--------|
        | Shape | `(100,)` |
        | Type | `int32` |
        | Size in memory | `400.0 B` |
        | Chunks | `None` |
        | Compression | `None` |
        
        #### 📈 Statistics:
        | Metric | Value |
        |--------|--------|
        | Minimum | `0.000` |
        | Maximum | `99.000` |
        | Mean | `49.500` |
        | Median | `49.500` |
        | Std Dev | `28.866` |
        | Unique Values | `100` |
        
        #### 👁️ Preview:
        ```
        [0 1 2 3 4, ...]
        ```
        
## 📁 Group: `metadata`
    📝 **Attributes:**
        | Name | Value | Type |
        |------|--------|------|
        | `version` | `1.0` | _str_ |
    
    ### 📊 Dataset: `config`
        #### 📋 Properties:
        | Property | Value |
        |----------|--------|
        | Shape | `(3,)` |
        | Type | `|S10` |
        | Size in memory | `30.0 B` |
        | Chunks | `None` |
        | Compression | `None` |
        
        #### 👁️ Preview:
        ```
        [b'high' b'medium' b'low']
        ```
        
        📝 **Attributes:**
            | Name | Value | Type |
            |------|--------|------|
            | `type` | `settings` | _str_ |
        
## 📁 Group: `sensors`
    📝 **Attributes:**
        | Name | Value | Type |
        |------|--------|------|
        | `location` | `Building A` | _str_ |
    
    ### 📊 Dataset: `temperature`
        #### 📋 Properties:
        | Property | Value |
        |----------|--------|
        | Shape | `(24,)` |
        | Type | `float64` |
        | Size in memory | `192.0 B` |
        | Chunks | `None` |
        | Compression | `None` |
        
        #### 📈 Statistics:
        | Metric | Value |
        |--------|--------|
        | Minimum | `0.025` |
        | Maximum | `0.974` |
        | Mean | `0.444` |
        | Median | `0.434` |
        | Std Dev | `0.272` |
        | Unique Values | `24` |
        
        #### 👁️ Preview:
        ```
        [0.18435621 0.97414573 0.02505631 0.08934539 0.45308786, ...]
        ```
        
        📝 **Attributes:**
            | Name | Value | Type |
            |------|--------|------|
            | `sampling_rate` | `1 per hour` | _str_ |
            | `unit` | `celsius` | _str_ |
        

## 📊 Summary Statistics
| Metric | Value |
|--------|--------|
| Total Groups | `4` |
| Total Datasets | `4` |
| Total Data Size | `694.0 B` |
| Compressed Datasets | `0` |
| Compression Ratio | `17.27x` |