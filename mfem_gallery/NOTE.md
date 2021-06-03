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

line:391 'DMFEM_USE_ZLIB': '1' -> 'DMFEM_USE_ZLIB': '0'

```python
    cmake_opts = {'DCMAKE_VERBOSE_MAKEFILE': '1',
                  'DBUILD_SHARED_LIBS': '1',
                  'DMFEM_ENABLE_EXAMPLES': '1',
                  'DMFEM_ENABLE_MINIAPPS': '1',
                  'DCMAKE_SHARED_LINKER_FLAGS': '',
                  'DMFEM_USE_ZLIB': '0',
                  'DCMAKE_CXX_FLAGS': cxx11_flag}
```

Error when to wrap

```bash
mesh_wrap.cxx: In function 'PyObject* _wrap_Mesh_tmp_vertex_parents_set(PyObject*, PyObject*)':
mesh_wrap.cxx:4335:21: error: 'mfem::Array<mfem::Triple<int, int, int> > mfem::Mesh::tmp_vertex_parents' is protected within this context
   if (arg1) (arg1)->tmp_vertex_parents = *arg2;
```

- <https://teratail.com/questions/173271>
- <https://teratail.com/questions/108373>
- <https://bg1.hatenablog.com/entry/2016/06/21/210000>
