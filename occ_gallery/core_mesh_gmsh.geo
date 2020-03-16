
    SetFactory("OpenCASCADE");

    Mesh.CharacteristicLengthMin = 1;
    Mesh.CharacteristicLengthMax = 5;

    a() = ShapeFromFile("core_mesh_gmsh.brep");
    b() = ShapeFromFile("core_mesh_gmsh_box.brep");
    