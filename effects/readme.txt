Each effect has a name, for example "chorus". For each effect there should be two or three files:

* JSON file that describes the parameters of the effect
* Csound effect template file
* Csound global variables template file

They should be named like this, respectively:
{name}.json
{name}.effect.jinja2
{name}.globals.jinja2

Replace {name} with the actual name of the effect. For example:
chorus.json
chorus.effect.jinja2
chorus.globals.jinja2

Parameter names specified in a json file are prefixed with "k_" in the csound code

The following files are special templates and exceptions from the rules described above:
base_template.csd.jinja2
base_template_live.csd.jinja2
composite.jinja2
data_augmentation.csd.jinja2
test_effect.csd.jinja2
test_effect.json
