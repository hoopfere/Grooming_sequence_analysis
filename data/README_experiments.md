# Dataset README

## 1. Data Format and Organization

Behavioral data are stored in Excel (`.xlsx`) files. Each file contains manually scored behavioral events from individual *Drosophila*.

### Data Structure

Each row represents a single behavioral bout. Multiple rows may correspond to the same fly, and each fly is identified by a unique filename.

The dataset contains five columns:

| Column | Description |
|---|---|
| `genotype` | Identifier for the experimental group or condition. |
| `file` | Unique identifier for an individual fly, corresponding to its source recording. |
| `behavior` | Behavioral category assigned to the bout. |
| `start_time` | Start of the behavioral bout, in seconds. |
| `duration` | Duration of the behavioral bout, in seconds. |

Filename conventions may vary between recordings. Filenames sometimes include chamber identifiers (e.g., `CH2`, `CH3`), but these are not standardized and should not be used to identify individual flies independently of the complete filename.

### Behavioral Categories

Behavioral bouts were manually scored using the following categories:

- `head`
- `thorax`
- `abdominal`
- `wing`
- `front_leg_rubbing`
- `back_leg_rubbing`
- `rubbing`
- `class_all_grooming`

The individual grooming behaviors are mutually exclusive: only one individual behavioral category can be assigned at a given time.

In the heat experiments, front-leg and back-leg rubbing were scored separately as `front_leg_rubbing` and `back_leg_rubbing`. In the social isolation experiments, they were not differentiated and were scored together as `rubbing`.

`class_all_grooming` is an aggregate category encompassing all individual grooming behaviors scored in the corresponding experiment. Events in this category therefore overlap with events recorded under the individual behavioral categories and should not be counted as additional independent grooming events.

### Time Measurements

Both `start_time` and `duration` are expressed in seconds.

The end time of each behavioral bout can be calculated as:

`end_time = start_time + duration`

## 2. Experimental Conditions

### Heat experiments

- `HeatExpt_25C.xlsx`: Flies exposed to 25°C for 30 minutes and recorded for 5 minutes after exposure.
- `HeatExpt_37C.xlsx`: Flies exposed to 37°C for 30 minutes and recorded for 5 minutes after exposure.

### Social isolation

- `SocialIso_GH.xlsx`: Flies reared in groups (group-housed; GH) for 6 days.
- `SocialIso_SH.xlsx`: Flies reared alone (single-housed; SH) for 6 days.

In these experiments, `rubbing` includes both front-leg and back-leg rubbing; these behaviors were not differentiated.
