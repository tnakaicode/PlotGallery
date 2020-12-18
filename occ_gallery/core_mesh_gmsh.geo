SetFactory("OpenCASCADE");

    Mesh.CharacteristicLengthMin = 1;
    Mesh.CharacteristicLengthMax = 5;

    a() = ShapeFromFile("core_mesh_gmsh.brep");
    