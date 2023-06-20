# Create latex summary slides for different fit tests

You can create latex scripts using `make_latex_slides.py`.
Currently, the script offers three modes

- impacts (i) to create slides with impacts
- pulls (p) to create slides with pull plots
- results (r) (deprecated since summary plots and tables was updated)
- coming soon: evolution (e) for parameter evolution plots

The script will also create navigation slides to easily jump between the different stages of the combination.
Please use `make_latex_slides.py -h` for more information about the modes and inputs you need.

Short description:

- `c`: config for a given mode, e.g. `config_impactslides_XX_YYYY.py` for mode `i`
- `n`: naming config, e.g. `config_channel_naming_YYYY.py` with he channels you want to include
- `o`: name of the output file containing the latex slides
