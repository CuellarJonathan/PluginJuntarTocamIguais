from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject
from qgis.PyQt.QtWidgets import QAction
from qgis.utils import iface
import os.path
from .custom_dialog import CustomDialog  # Importe a classe CustomDialog do seu módulo custom_dialog

class PluginJuntarTocamIguais:
    def __init__(self, iface):
        self.iface = iface

    def initGui(self):
        # Adicionar um ícone na barra de ferramentas
        self.action = QAction(QIcon(os.path.dirname(__file__) + '/icon.png'), 'Plugin para Juntar os Iguais que se Tocam', self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        # Remover o ícone da barra de ferramentas
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        # Lógica do plugin aqui
        # print('Meu Plugin foi executado!')
        # Aqui você pode adicionar o código para o seu plugin
        iface.messageBar().pushMessage("Plugin Juntar Tocam Iguais", "Plugin para Juntar os Iguais que se Tocam foi Aberto!", duration=10)
        # Crie e exiba o diálogo personalizado
        dialog = CustomDialog()
        dialog.exec_()
        

def init_plugin():
    plugin = PluginJuntarTocamIguais(iface)
    plugin.initGui()

# def unload_plugin():
    #Remova o botão da barra de ferramentas
    # for action in iface.toolbarActions():
        # if action.text() == "Meu Plugin":
            # iface.removeToolBarIcon(action)
