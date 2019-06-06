# JonasLB's Inelastica branches

The `mymaster` branch contains the merge of a number of working branches not yet in upstream:

- `myreadme` (for this alternate readme)
- `jinja` adds jinja template ability (will probably never go upstream)
- `tiling`: Replaces the old `repeteGeom` with a geometry tiling function which is much faster
- `py3shebang`: All scripts have a python3 shebang
- `clean_tbt_se`: Adds ability to use self-energies from tbtrans.

`git checkout master && git pull upstream master && git push && git branch -D mymaster && git checkout -b mymaster && git merge myreadme jinja tiling py3shebang clean_tbt_se`
