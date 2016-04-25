Each effect has a name, for example "dist_lpf". For each effect there should be two files:
one csound template file and one file that describes the parameters of the effect. They should be
named like this, respectively:
{name}.json
{name}.csd.jinja2

Replace {name} with the actual name of the effect. For example:
dist_lpf.json
dist_lpf.csd.jinja2
