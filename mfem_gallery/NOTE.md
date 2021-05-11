---
title: MFEM for Python
---

```bash
git clone https://github.com/mfem/mfem.git
git clone https://github.com/mfem/PyMFEM.git
git clone https://github.com/mfem/data.git mfem_data

cd PyMFEM
git submodule add https://salsa.debian.org/science-team/hypre.git external/hypre
git submodule add -f https://github.com/mfem/mfem.git external/mfem
cd external
wget http://glaros.dtc.umn.edu/gkhome/fetch/sw/metis/metis-5.1.0.tar.gz
tar -zxvf metis-5.1.0.tar.gz -C metis/ --strip-components=1
cd ..
```

"Windows is not supported yet. Contribution is welcome"
AssertionError: Windows is not supported yet. Contribution is welcome
