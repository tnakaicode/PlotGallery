from PyQt5.QtWidgets import QMainWindow, QAction, QApplication, QWidget, QPushButton, qApp, QLabel, QHBoxLayout, QVBoxLayout, QSplitter
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QImage, QMatrix4x4, QQuaternion, QVector3D, QColor, QGuiApplication
from PyQt5.QtCore import QSize, Qt
import sys
from PyQt5.Qt3DCore import QEntity, QTransform, QAspectEngine
from PyQt5.Qt3DRender import QCamera, QCameraLens, QRenderAspect
from PyQt5.Qt3DInput import QInputAspect
from PyQt5.Qt3DExtras import QForwardRenderer, QPhongMaterial, QCylinderMesh, QSphereMesh, QTorusMesh, Qt3DWindow, QOrbitCameraController

class View3D(QWidget):
    def __init__(self):
        super(View3D, self).__init__()
        self.view = Qt3DWindow()
        self.container = self.createWindowContainer(self.view)

        vboxlayout = QHBoxLayout()
        vboxlayout.addWidget(self.container)
        self.setLayout(vboxlayout)

        scene = createScene()

        # Camera.
        initialiseCamera(self.view, scene)

        self.view.setRootEntity(scene)

def initialiseCamera(view, scene):
    # Camera.
    camera = view.camera()
    camera.lens().setPerspectiveProjection(45.0, 16.0 / 9.0, 0.1, 1000.0)
    camera.setPosition(QVector3D(0.0, 0.0, 40.0))
    camera.setViewCenter(QVector3D(0.0, 0.0, 0.0))

    # For camera controls.
    camController = QOrbitCameraController(scene)
    camController.setLinearSpeed(50.0)
    camController.setLookSpeed(180.0)
    camController.setCamera(camera)

def createScene():
    # Root entity.
    rootEntity = QEntity()

    # Material.
    material = QPhongMaterial(rootEntity)

    # Torus.
    torusEntity = QEntity(rootEntity)
    torusMesh = QTorusMesh()
    torusMesh.setRadius(5)
    torusMesh.setMinorRadius(1)
    torusMesh.setRings(100)
    torusMesh.setSlices(20)

    torusTransform = QTransform()
    torusTransform.setScale3D(QVector3D(1.5, 1.0, 0.5))
    torusTransform.setRotation(
            QQuaternion.fromAxisAndAngle(QVector3D(1.0, 0.0, 0.0), 45.0))

    torusEntity.addComponent(torusMesh)
    torusEntity.addComponent(torusTransform)
    torusEntity.addComponent(material)

    # Sphere.
    sphereEntity = QEntity(rootEntity)
    sphereMesh = QSphereMesh()
    sphereMesh.setRadius(3)

    sphereEntity.addComponent(sphereMesh)
    sphereEntity.addComponent(material)

    return rootEntity

class Application(QMainWindow):
    def __init__(self):
        super().__init__()
        #
        view3d = View3D()
        self.setCentralWidget(view3d)
        self.show()

# Approach 1 - Integrate Qt3DWindow into a QMainWindow
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Application()
    sys.exit(app.exec_())

'''
# Approach 2 - A native Qt3DWindow
if __name__ == '__main__':
    app = QGuiApplication(sys.argv)
    view = Qt3DWindow()

    scene = createScene()
    initialiseCamera(view, scene)

    view.setRootEntity(scene)
    view.show()

    sys.exit(app.exec_())
'''